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

import gevent
from unittest.mock import MagicMock
from sysmon.agent import SysMonAgent


def test_sysmon_agent_end_to_end_polling_and_pubsub():
    """Integration test simulating full SysMon agent lifecycle with PubSub messages."""
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

    published_messages = []

    def mock_publish(peer, topic, headers, message):
        published_messages.append({"peer": peer, "topic": topic, "headers": headers, "message": message})

    agent.vip.pubsub.publish.side_effect = mock_publish

    # Full config with diverse publish types and subpoint filters
    config = {
        "default_publish_type": "datalogger",
        "base_topic": "Log/Platform",
        "monitor": {
            "cpu_percent": {
                "point_name": "CPU/Percent",
                "check_interval": 1,
                "poll": True,
                "params": {"per_cpu": False, "capture_interval": None}
            },
            "memory": {
                "point_name": "Memory",
                "check_interval": 1,
                "poll": True,
                "params": {"sub_points": {"available": True, "percent": True, "used": True}}
            },
            "load_average": {
                "point_name": "CPU/LoadAverage",
                "check_interval": 1,
                "poll": True,
                "params": {"sub_points": {"OneMinute": True, "FiveMinute": True}}
            },
            "network_connections": {
                "point_name": "Network/Connections",
                "check_interval": 1,
                "poll": True,
                "params": {"kind": "inet"}
            }
        }
    }

    agent.on_configure("config", "NEW", config)
    assert len(agent._scheduled) == 4

    # Trigger all scheduled periodic tasks
    for sched_call in agent.core.schedule.call_args_list:
        task_func = sched_call[0][1]
        task_params = sched_call[0][2]
        task_func(task_params)

    assert len(published_messages) == 4

    topics = [m["topic"] for m in published_messages]
    assert "datalogger/Log/Platform/CPU" in topics
    assert "datalogger/Log/Platform/Memory" in topics
    assert "datalogger/Log/Platform/CPU/LoadAverage" in topics
    assert "record/Log/Platform/Network/Connections" in topics
