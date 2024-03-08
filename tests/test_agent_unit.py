# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
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

import pytest
import gevent

from volttron.client.known_identities import PLATFORM_DRIVER
from volttrontesting.platformwrapper import PlatformWrapper
from volttrontesting.fixtures.volttron_platform_fixtures import volttron_instance

def test_get_point_set_point(publish_agent):
    result = publish_agent.vip.rpc.call('agent.sysmon', 'cpu_times_percent', per_cpu=False, sub_points=None, capture_interval=5).get(timeout=10)
    assert type(result) == dict, "Result should be a dictionary"
    assert len(result) > 0, "Dictionary should not be empty"

@pytest.fixture(scope="module")
def publish_agent(volttron_instance: PlatformWrapper):
    assert volttron_instance.is_running()
    vi = volttron_instance
    assert vi is not None
    assert vi.is_running()

    # install platform driver
    config = {
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
    puid = vi.install_agent(agent_dir="volttron-sysmon",
                            config_file=config,
                            start=False,
                            vip_identity="agent.sysmon")
    assert puid is not None
    gevent.sleep(1)
    assert vi.start_agent(puid)
    assert vi.is_agent_running(puid)

    # create the publish agent
    publish_agent = volttron_instance.build_agent()
    assert publish_agent.core.identity
    gevent.sleep(1)

    capabilities = {"edit_config_store": {"identity": PLATFORM_DRIVER}}
    volttron_instance.add_capabilities(publish_agent.core.publickey, capabilities)

    gevent.sleep(10)

    yield publish_agent

    volttron_instance.stop_agent(puid)
    publish_agent.core.stop()