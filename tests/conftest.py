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

"""Configuration for the pytest test suite."""

import sys
from pathlib import Path
import pytest

if "src" not in sys.path:
    sys.path.insert(0, "src")

from volttrontesting.fixtures.volttron_platform_fixtures import (
    build_wrapper,
    cleanup_wrapper,
    get_rand_vip,
)


@pytest.fixture(scope="module", params=[dict(messagebus="zmq", ssl_auth=False)])
def volttron_instance(request, **kwargs):
    """Fixture that returns a single instance of volttron platform for volttrontesting."""
    address = kwargs.pop("address", get_rand_vip())
    wrapper = build_wrapper(
        address,
        messagebus=request.param["messagebus"],
        ssl_auth=request.param["ssl_auth"],
        **kwargs,
    )
    wrapper_pid = wrapper.p_process.pid if wrapper.p_process else None

    try:
        yield wrapper
    except Exception as ex:
        print(ex.args)
    finally:
        cleanup_wrapper(wrapper)
        if not wrapper.debug_mode:
            assert not Path(wrapper.volttron_home).exists()
        if wrapper_pid:
            import psutil
            if psutil.pid_exists(wrapper_pid):
                psutil.Process(wrapper_pid).kill()


@pytest.fixture()
def publish_agent(volttron_instance):
    assert volttron_instance.is_running()
    yield volttron_instance.build_agent(identity="publish_agent")
