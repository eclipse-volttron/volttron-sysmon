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
from pathlib import Path

from volttron.client.messaging.health import STATUS_GOOD
from volttron.client.vip.agent import Agent
from volttrontesting.platformwrapper import PlatformWrapper

def test_sysmon_agent_successful_install_on_volttron_platform(
        publish_agent: Agent, volttron_instance: PlatformWrapper):
    # Agent install path based upon root of this repository
    agent_dir = Path(__file__).parent.parent.resolve().as_posix()
    sysmon_config = {
        "default_publish_type": "datalogger",
        "base_topic": "Log/Platform",
        "monitor": {
            "cpu_percent": {
                "point_name": "CPU/Percent",
                "check_interval": 5,
                "poll": True,
                "params": {
                    "per_cpu": True,
                    "capture_interval": None
                }
            }
        }
    }
    pdriver_id = "agent.sysmon"

    pdriver_uuid = volttron_instance.install_agent(agent_dir=agent_dir,
                                                config_file=sysmon_config,
                                                start=False,
                                                vip_identity=pdriver_id)
    assert pdriver_uuid is not None
    gevent.sleep(1)
    started = volttron_instance.start_agent(pdriver_uuid)
    assert started
    assert volttron_instance.is_agent_running(pdriver_uuid)

    assert publish_agent.vip.rpc.call(
        pdriver_id, "health.get_status").get(timeout=10).get('status') == STATUS_GOOD
