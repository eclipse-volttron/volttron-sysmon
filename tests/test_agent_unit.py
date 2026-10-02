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


# ---------------------------------------------------------------------------------------------------------------------
# Regression tests for problems found while running the agent on a live platform (2026-10-01).

from collections import namedtuple
from enum import IntEnum


def _publish_once(mock_agent, method, publish_type, point_name, params):
    """Schedule a monitor through _periodic_pub, run its callback once and return the publish call kwargs."""
    mock_agent._periodic_pub(getattr(mock_agent, method), publish_type, 5, point_name, params)
    fn = mock_agent.core.schedule.call_args[0][1]
    mock_agent.vip.pubsub.publish.reset_mock()
    fn(params)
    return mock_agent.vip.pubsub.publish.call_args[1] if mock_agent.vip.pubsub.publish.called else None


def test_units_table_has_no_misspelled_keys_and_swap_percent_is_percent():
    assert 'network_interface_statitics' not in SysMonAgent.UNITS
    assert SysMonAgent.UNITS['swap']['percent'] == 'percent'


def test_publish_tolerates_sub_points_missing_from_units_table(mock_agent):
    """psutil 5.9 added a 'flags' field to net_if_stats that is absent from UNITS; it must not abort the publish."""
    snicstats = namedtuple('snicstats', ['isup', 'duplex', 'speed', 'mtu', 'flags'])

    class NicDuplex(IntEnum):
        NIC_DUPLEX_FULL = 2

    with patch('psutil.net_if_stats',
               return_value={'lo': snicstats(True, NicDuplex.NIC_DUPLEX_FULL, 0, 65536, 'up,loopback')}):
        pub = _publish_once(mock_agent, 'network_interface_statistics', 'datalogger',
                            'Network/Interface/Statistics', {})
    assert pub['topic'] == 'datalogger/Log/Platform/Network/Interface/Statistics/lo'
    assert pub['message']['flags']['Readings'][1] == 'up,loopback'
    assert pub['message']['flags']['Units'] is None
    assert pub['message']['mtu']['Units'] == 'bytes'
    assert pub['message']['duplex']['Readings'][1] == 'NIC_DUPLEX_FULL'


def test_publish_converts_enum_values(mock_agent):
    """sensors_battery.secsleft is a psutil.BatteryTime enum; it must be published as its value, not dropped."""

    class BatteryTime(IntEnum):
        POWER_TIME_UNLIMITED = -2

    sbattery = namedtuple('sbattery', ['percent', 'secsleft', 'power_plugged'])
    with patch('psutil.sensors_battery', return_value=sbattery(50.0, BatteryTime.POWER_TIME_UNLIMITED, True)):
        pub = _publish_once(mock_agent, 'sensors_battery', 'datalogger', 'Sensors/Battery', {})
    assert pub['message']['secsleft']['Readings'][1] == -2
    assert pub['message']['secsleft']['data_type'] == 'int'
    assert pub['message']['power_plugged']['Readings'][1] is True


def test_publish_unpacks_lists_and_none_values(mock_agent):
    """sensors_fans returns {chip: [sfan, ...]}; list items are published by index and None values are kept."""
    sfan = namedtuple('sfan', ['label', 'current'])
    with patch('psutil.sensors_fans', return_value={'thinkpad': [sfan('fan1', 2500), sfan(None, 0)]}):
        pub = _publish_once(mock_agent, 'sensors_fans', 'datalogger', 'Sensors/Fans', {})
    assert pub['message']['0/current']['Readings'][1] == 2500
    assert pub['message']['1/label']['Readings'][1] is None
    assert pub['topic'] == 'datalogger/Log/Platform/Sensors/Fans/thinkpad'


def test_cpu_times_returns_seconds_not_percentages(mock_agent):
    scputimes = namedtuple('scputimes', ['user', 'system', 'idle'])
    with patch('psutil.cpu_times', return_value=scputimes(1234.5, 67.8, 99999.0)) as cpu_times, \
            patch('psutil.cpu_times_percent') as cpu_times_percent:
        assert mock_agent.cpu_times() == {'user': 1234.5, 'system': 67.8, 'idle': 99999.0}
    cpu_times.assert_called_once_with(percpu=False)
    cpu_times_percent.assert_not_called()


def test_sensors_temperatures_without_hardware_returns_empty_dict(mock_agent):
    with patch('psutil.sensors_temperatures', return_value={}):
        assert mock_agent.sensors_temperatures() == {}
    shwtemp = namedtuple('shwtemp', ['label', 'current', 'high', 'critical'])
    with patch('psutil.sensors_temperatures', return_value={'coretemp': [shwtemp('Core 0', 45.0, 90.0, 100.0)]}):
        assert mock_agent.sensors_temperatures(included_sensors=['other']) == {}
        temps = mock_agent.sensors_temperatures(sub_points=['label', 'high'])
    assert temps == {'coretemp': [{'label': 'Core 0', 'high': 90.0}]}


def test_throughput_respects_sub_points_dict_false(mock_agent):
    mock_agent.disk_io()
    result = mock_agent.disk_io(sub_points={'read_bytes': True, 'read_throughput': False, 'write_throughput': True})
    assert 'read_bytes' in result
    assert 'read_throughput' not in result
    assert 'write_throughput' in result


def test_disk_io_without_disks_does_not_raise(mock_agent):
    """psutil.disk_io_counters returns None on systems without block devices."""
    with patch('psutil.disk_io_counters', return_value=None):
        assert mock_agent.disk_io() == {}


def test_network_connections_single_connection_is_flattened_consistently(mock_agent):
    addr = namedtuple('addr', ['ip', 'port'])
    sconn = namedtuple('sconn', ['fd', 'family', 'type', 'laddr', 'raddr', 'status', 'pid'])
    import socket
    conn = sconn(3, socket.AF_INET, socket.SOCK_STREAM, addr('127.0.0.1', 22), (), 'LISTEN', 1)
    with patch('psutil.net_connections', return_value=[conn]):
        result = mock_agent.network_connections()
    assert result == {'fd': 3, 'family': 'AF_INET', 'type': 'SOCK_STREAM', 'laddr': '127.0.0.1:22', 'raddr': '',
                      'status': 'LISTEN', 'pid': 1}


def test_on_configure_bad_monitor_does_not_stop_others(mock_agent):
    config = {
        "default_publish_type": "datalogger", "base_topic": "Log/Platform",
        "monitor": {
            "cpu_percent": {"point_name": "CPU/Percent", "check_interval": 4, "poll": True},    # no params: allowed
            "memory": {"point_name": "Memory", "check_interval": "often", "poll": True, "params": {}},    # invalid
            "swap": {"point_name": "Swap", "check_interval": 4, "poll": True, "params": {}},
            "load_average": {"point_name": "CPU/LoadAverage", "check_interval": 4, "poll": False, "params": {}},
        }
    }
    mock_agent.on_configure("config", "NEW", config)
    scheduled = [call[0][1].__name__ for call in mock_agent.core.schedule.call_args_list]
    assert len(mock_agent._scheduled) == 2
    assert scheduled == ['_datalogger_publish', '_datalogger_publish']


def test_on_configure_deprecated_format(mock_agent):
    config = {"base_topic": "datalogger/log/platform", "cpu_check_interval": 4, "disk_check_interval": 10,
              "disk_path": "/tmp"}
    mock_agent.on_configure("config", "NEW", config)
    assert mock_agent.default_publish_type == 'datalogger'
    assert mock_agent.base_topic == 'log/platform'
    assert len(mock_agent._scheduled) == 2
    params = [call[0][2] for call in mock_agent.core.schedule.call_args_list]
    assert params == [{}, {'disk_path': '/tmp'}]
    # Running the disk_usage publish with the deprecated path must work end to end.
    disk_fn = mock_agent.core.schedule.call_args_list[1][0][1]
    mock_agent.vip.pubsub.publish.reset_mock()
    disk_fn(params[1])
    assert mock_agent.vip.pubsub.publish.call_args[1]['topic'] == 'datalogger/log/platform/Disk/Usage/tmp'


def test_on_configure_reconfigure_cancels_previous_schedules(mock_agent):
    config = {"default_publish_type": "datalogger", "base_topic": "Log/Platform",
              "monitor": {"memory": {"point_name": "Memory", "check_interval": 4, "poll": True, "params": {}}}}
    mock_agent.on_configure("config", "NEW", dict(config))
    first = list(mock_agent._scheduled)
    mock_agent.on_configure("config", "UPDATE", dict(config))
    for sched in first:
        sched.cancel.assert_called_once()
    assert len(mock_agent._scheduled) == 1


def test_heartbeat_started_on_start(mock_agent):
    mock_agent.onstart(None)
    mock_agent.vip.heartbeat.start.assert_called_once()
