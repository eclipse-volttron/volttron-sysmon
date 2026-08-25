# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2024 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from sysmon.agent import SysMonAgent


@pytest.fixture
def mock_agent():
    agent = object.__new__(SysMonAgent)
    agent.default_publish_type = "datalogger"
    agent.base_topic = "Log/Platform"
    agent._scheduled = []
    agent.last_path_sizes = {}
    agent.last_disk_read_bytes = {}
    agent.last_disk_write_bytes = {}
    agent.last_network_received_bytes = {}
    agent.last_network_sent_bytes = {}
    agent.vip = MagicMock()
    agent.core = MagicMock()
    return agent


def test_implemented_methods_and_units_alignment():
    """Verify all IMPLEMENTED_METHODS have corresponding entries in UNITS and are callable."""
    for method in SysMonAgent.IMPLEMENTED_METHODS:
        assert hasattr(SysMonAgent, method), f"SysMonAgent missing method {method}"
        assert method in SysMonAgent.UNITS, f"SysMonAgent.UNITS missing {method}"

    for method in SysMonAgent.RECORD_ONLY_PUBLISH_METHODS:
        assert method in SysMonAgent.IMPLEMENTED_METHODS, f"RECORD_ONLY method {method} not in IMPLEMENTED_METHODS"


def test_cpu_statistics_alias(mock_agent):
    """Verify cpu_statistics and cpu_stats return the same data."""
    stats1 = mock_agent.cpu_stats()
    stats2 = mock_agent.cpu_statistics()
    assert isinstance(stats1, dict)
    assert isinstance(stats2, dict)
    assert set(stats1.keys()) == set(stats2.keys())


def test_cpu_metrics(mock_agent):
    """Verify CPU percent, times, frequency, and count."""
    percent = mock_agent.cpu_percent(per_cpu=False)
    assert isinstance(percent, (int, float))

    per_cpu_percent = mock_agent.cpu_percent(per_cpu=True)
    assert isinstance(per_cpu_percent, dict)

    cpu_count = mock_agent.cpu_count(logical=True)
    assert isinstance(cpu_count, int) and cpu_count > 0

    times = mock_agent.cpu_times()
    assert isinstance(times, dict)

    load = mock_agent.load_average()
    assert isinstance(load, dict)
    assert "OneMinute" in load


def test_memory_and_swap(mock_agent):
    """Verify memory and swap statistics."""
    mem = mock_agent.memory()
    assert isinstance(mem, dict)
    assert "total" in mem
    assert "available" in mem
    assert "percent" in mem

    swap = mock_agent.swap()
    assert isinstance(swap, dict)
    assert "total" in swap


def test_disk_metrics(mock_agent, tmp_path):
    """Verify disk usage, partitions, path usage, and rate calculations."""
    usage = mock_agent.disk_usage(disk_path="/")
    assert isinstance(usage, dict)
    assert "/" in usage

    partitions = mock_agent.disk_partitions(all_partitions=True)
    assert isinstance(partitions, dict)

    # Test path_usage on a test directory
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello volttron sysmon")
    path_sz = mock_agent.path_usage(str(tmp_path))
    assert path_sz[str(tmp_path)] == len(b"hello volttron sysmon")

    # Test path_usage_rate
    initial_rate = mock_agent.path_usage_rate(str(tmp_path))
    assert initial_rate[str(tmp_path)] == -2  # First call returns -2 baseline

    test_file.write_bytes(b"hello volttron sysmon extended")
    second_rate = mock_agent.path_usage_rate(str(tmp_path))
    assert isinstance(second_rate[str(tmp_path)], (int, float))


def test_disk_and_network_io_zero_division_guard(mock_agent):
    """Ensure throughput calculations never raise ZeroDivisionError even when called instantaneously."""
    mock_agent.disk_io(per_disk=False)
    mock_agent.disk_io(per_disk=True)
    mock_agent.network_io(per_nic=False)
    mock_agent.network_io(per_nic=True)

    # Immediate second call with 0 elapsed seconds
    io_res = mock_agent.disk_io(per_disk=False)
    assert isinstance(io_res, dict)
    assert "read_throughput" in io_res

    net_res = mock_agent.network_io(per_nic=False)
    assert isinstance(net_res, dict)
    assert "receive_throughput" in net_res


def test_sensors_temperatures_with_filters(mock_agent):
    """Verify sensors_temperatures accepts included_sensors and sub_points without crashing."""
    res = mock_agent.sensors_temperatures(
        fahrenheit=True,
        included_sensors=["cpu_thermal"],
        sub_points=["current", "label"]
    )
    assert res == "No hardware to read" or isinstance(res, dict)


def test_sub_point_filtering(mock_agent):
    """Verify _filter_sub_points supports list, dict, and str filters."""
    from collections import namedtuple
    TestTuple = namedtuple("TestTuple", ["a", "b", "c"])
    item = TestTuple(a=1, b=2, c=3)

    # List filter
    filtered_list = mock_agent._filter_sub_points(item, ["a", "c"])
    assert filtered_list == {"a": 1, "c": 3}

    # Dict filter
    filtered_dict = mock_agent._filter_sub_points(item, {"a": True, "b": False, "c": True})
    assert filtered_dict == {"a": 1, "c": 3}

    # Str filter
    filtered_str = mock_agent._filter_sub_points(item, "b")
    assert filtered_str == {"b": 2}


def test_on_configure_full_config(mock_agent):
    """Verify on_configure successfully parses all monitors from default configuration."""
    config_file = Path(__file__).parent.parent / "sysmon_agent_config.json"
    with open(config_file) as f:
        config = json.load(f)

    expected_count = len(config["monitor"])
    # Enable all monitors for testing
    for mon in config["monitor"].values():
        mon["poll"] = True

    mock_agent.on_configure("config", "NEW", config)
    assert len(mock_agent._scheduled) == expected_count


def test_publish_modes(mock_agent):
    """Verify datalogger, all, and record publish formatting."""
    # Test datalogger mode
    mock_agent._periodic_pub(mock_agent.load_average, "datalogger", 5, "CPU/LoadAverage", {})
    datalogger_fn = mock_agent.core.schedule.call_args[0][1]
    mock_agent.vip.pubsub.publish.reset_mock()
    datalogger_fn({})
    pub_args = mock_agent.vip.pubsub.publish.call_args[1]
    assert pub_args["topic"] == "datalogger/Log/Platform/CPU/LoadAverage"
    assert "OneMinute" in pub_args["message"]
    assert "Readings" in pub_args["message"]["OneMinute"]

    # Test all mode
    mock_agent._periodic_pub(mock_agent.load_average, "all", 5, "CPU/LoadAverage", {})
    all_fn = mock_agent.core.schedule.call_args[0][1]
    mock_agent.vip.pubsub.publish.reset_mock()
    all_fn({})
    pub_args_all = mock_agent.vip.pubsub.publish.call_args[1]
    assert pub_args_all["topic"] == "all/Log/Platform/CPU/LoadAverage/all"
    assert isinstance(pub_args_all["message"], list)
    assert isinstance(pub_args_all["message"][0], dict)  # values
    assert isinstance(pub_args_all["message"][1], dict)  # metadata

    # Test record mode
    mock_agent._periodic_pub(mock_agent.network_connections, "record", 5, "Network/Connections", {"kind": "inet"})
    record_fn = mock_agent.core.schedule.call_args[0][1]
    mock_agent.vip.pubsub.publish.reset_mock()
    record_fn({"kind": "inet"})
    pub_args_rec = mock_agent.vip.pubsub.publish.call_args[1]
    assert pub_args_rec["topic"] == "record/Log/Platform/Network/Connections"
