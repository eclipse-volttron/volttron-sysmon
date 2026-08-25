# volttron-sysmon

The System Monitoring Agent (colloquially “SysMon”) can be installed on the platform to monitor system resource metrics,
including but not limited to percent CPU utilization, percent system memory (RAM) utilization, and percent storage (disk) utilization based
on disk path.

## Requires

* python >= 3.10
* volttron >= 10.0

## Installation

Before installing, VOLTTRON should be installed and running.  Its virtual environment should be active.
Information on how to install of the VOLTTRON platform can be found
[here](https://github.com/eclipse-volttron/volttron-core).

Create a directory called `config` and use the change directory command to enter it.

```shell
mkdir config
cd config
```

After entering the config directory, create a file named `sysmon_agent_config.json`, use the below JSON to populate your new file.

For simplicity, copy all of the JSON below and switch the key `"poll": false,` to `"poll": true,` for each system resource you want to monitor.

```json
{
    "default_publish_type": "datalogger",
    "base_topic": "Log/Platform",
    "monitor": {
        "cpu_percent": {
            "point_name": "CPU/Percent",
            "check_interval": 5,
            "poll": false,
            "params": {
                "per_cpu": true,
                "capture_interval": null
            }
        },
        "cpu_times": {
            "point_name": "CPU/Times",
            "check_interval": 5,
            "poll": false,
            "params": {
                "per_cpu": false,
                "sub_points": {
                    "user": false,
                    "nice": false,
                    "system": false,
                    "idle": false,
                    "iowait": false,
                    "irq": false,
                    "softirq": false,
                    "steal": false,
                    "guest": false,
                    "guest_nice": false
                }
            }
        },
        "cpu_times_percent": {
            "point_name": "CPU/TimePercentages",
            "check_interval": 5,
            "poll": false,
            "params": {
                "per_cpu": false,
                "capture_interval": null,
                "sub_points": {
                    "user": false,
                    "nice": false,
                    "system": false,
                    "idle": false,
                    "iowait": false,
                    "irq": false,
                    "softirq": false,
                    "steal": false,
                    "guest": false,
                    "guest_nice": false
                }
            }
        },
        "cpu_statistics": {
            "point_name": "CPU/Statistics",
            "check_interval": 5,
            "poll": false,
            "params": {
                "sub_points": {
                    "ctx_switches": false,
                    "interrupts": false,
                    "soft_interrupts": false
                }
            }
        },
        "cpu_frequency": {
            "point_name": "CPU/Frequencies",
            "check_interval": 5,
            "poll": false,
            "params": {
                "per_cpu": false,
                "sub_points": {
                    "current": false,
                    "min": false,
                    "max": false
                }
            }
        },
        "memory": {
            "point_name": "Memory",
            "check_interval": 5,
            "poll": false,
            "params": {
                "sub_points": {
                    "total": false,
                    "available": true,
                    "percent": true,
                    "used": true,
                    "free": false,
                    "active": false,
                    "inactive": false,
                    "buffers": false,
                    "cached": false,
                    "shared": false,
                    "slab": false
                }
            }
        },
        "disk_usage": {
            "point_name": "Disk/Usage",
            "check_interval": 3600,
            "poll": true,
            "params": {
                "disk_path": ["/"],
                "sub_points": {
                    "total": false,
                    "used": true,
                    "free": true,
                    "percent": true
                }
            }
        },
        "load_average": {
            "point_name": "CPU/LoadAverage",
            "check_interval": 5,
            "poll": true,
            "params": {
                "sub_points": {
                    "OneMinute": true,
                    "FiveMinute": true,
                    "FifteenMinute": true
                }
            }
        },
        "swap": {
            "point_name": "Swap",
            "check_interval": 5,
            "poll": false,
            "params": {
                "sub_points": {
                    "total": false,
                    "used": true,
                    "free": true,
                    "percent": true,
                    "sin": false,
                    "sout": false
                }
            }
        },
        "path_usage": {
            "point_name": "Disk/Path/Usage",
            "check_interval": 3600,
            "poll": false,
            "params": {
                "path_name": "/var/log/journal"
            }
        },
        "path_usage_rate": {
            "point_name": "Disk/Path/Rate",
            "check_interval": 3600,
            "poll": false,
            "params": {
                "path_name": "/var/log/journal"
            }
        },
        "disk_io": {
            "point_name": "Disk/IO",
            "check_interval": 5,
            "poll": false,
            "params": {
                "per_disk": false,
                "included_disks": [],
                "no_wrap": true,
                "sub_points": {
                    "read_count": false,
                    "write_count": false,
                    "read_bytes": true,
                    "write_bytes": true,
                    "read_time": true,
                    "write_time": true,
                    "read_merged_count": false,
                    "write_merged_count": false,
                    "busy_time": true,
                    "read_throughput": true,
                    "write_throughput": true
                }
            }
        },
        "network_io": {
            "point_name": "Network/IO",
            "check_interval": 5,
            "poll": false,
            "params": {
                "per_nic": true,
                "included_nics": [],
                "no_wrap": true,
                "sub_points": {
                    "bytes_sent": true,
                    "bytes_recv": true,
                    "packets_sent": true,
                    "packets_recv": true,
                    "errin": true,
                    "errout": true,
                    "dropin": true,
                    "dropout": true,
                    "receive_throughput": true,
                    "send_throughput": true
                }
            }
        },
        "network_connections": {
            "point_name": "Network/Connections",
            "check_interval": 5,
            "poll": false,
            "params": {
                "kind": "inet",
                "sub_points": {
                    "fd": false,
                    "family": false,
                    "type": false,
                    "laddr": false,
                    "raddr": false,
                    "status": false,
                    "pid": false
                }
            }
        },
        "network_interface_addresses": {
            "point_name": "Network/Interface/Addresses",
            "check_interval": 5,
            "poll": false,
            "params": {
                "included_interfaces": [],
                "sub_points": {
                    "family": false,
                    "address": false,
                    "netmask": false,
                    "broadcast": false,
                    "ptp": false
                }
            }
        },
        "network_interface_statistics": {
            "point_name": "Network/Interface/Statistics",
            "check_interval": 5,
            "poll": false,
            "params": {
                "included_interfaces": [],
                "sub_points": {
                    "isup": false,
                    "duplex": false,
                    "speed": false,
                    "mtu": false
                }
            }
        },
        "sensors_temperatures": {
            "point_name": "Sensors/Temperatures",
            "check_interval": 5,
            "poll": false,
            "params": {
                "fahrenheit": false,
                "included_sensors": [],
                "sub_points": {
                    "label": true,
                    "current": true,
                    "high": true,
                    "critical": true
                }
            }
        },
        "sensors_fans": {
            "point_name": "Sensors/Fans",
            "check_interval": 5,
            "poll": false,
            "params": {
                "included_sensors": [],
                "sub_points": {
                    "label": false,
                    "current": false
                }
            }
        },
        "sensors_battery": {
            "point_name": "Sensors/Battery",
            "check_interval": 5,
            "poll": false,
            "params": {
                "sub_points": {
                    "percent": false,
                    "secsleft": false,
                    "power_plugged": false
                }
            }
        },
        "boot_time": {
            "point_name": "BootTime",
            "check_interval": 5,
            "poll": false,
            "params": {}
        },
        "users": {
            "point_name": "Users",
            "check_interval": 5,
            "poll": false,
            "params": {
                "sub_points": {
                    "name": false,
                    "terminal": false,
                    "host": false,
                    "started": false,
                    "pid": false
                }
            }
        }
    }
}

```

Besides `poll`, there are four other important options in SysMon's configuration:

- `default_publish_type`: Specifies the default publish type (`datalogger`, `all`, or `record`).
- `base_topic`: Specifies the base topic (e.g., `Log/Platform`).
- `point_name`: Sets the topic suffix for the specific monitor. In combination with `default_publish_type` and `base_topic`, data for `cpu_percent` is published to VOLTTRON with a topic of **datalogger/Log/Platform/CPU/Percent**.
- `check_interval`: Adjusts the polling interval in seconds for that resource.

The SysMon agent serves as a configurable wrapper around `psutil`. You can enable or disable specific sub-metrics by setting boolean values in the configuration file. For detailed insights into each metric, consult the [psutil documentation](https://psutil.readthedocs.io/en/latest/).

Unused monitor sections may be deleted. For example, a minimal configuration to monitor only `cpu_percent` looks like:

```json
{
    "default_publish_type": "datalogger",
    "base_topic": "Log/Platform",
    "monitor": {
        "cpu_percent": {
            "point_name": "CPU/Percent",
            "check_interval": 5,
            "poll": true,
            "params": {
                "per_cpu": false,
                "capture_interval": null
            }
        }
    }
}
```

### Install and start the SysMon Agent

Install and start the agent (it automatically uses the default VIP identity `platform.sysmon`):

```bash
vctl install volttron-sysmon --start
```

*(Optional: you can supply a custom VIP identity using `--vip-identity <identity>`)*.

### Store Configuration in the Configuration Store

Add `sysmon_agent_config.json` to the agent's configuration store under the key `config`:

```bash
vctl config store platform.sysmon config sysmon_agent_config.json
```

> **Note:** The second argument `config` is required as `SysMonAgent` listens for configuration events on the `config` key name.

### Observe Data

To verify telemetry being published to the bus, install and start a [Listener Agent](https://pypi.org/project/volttron-listener/):

```bash
vctl install volttron-listener --start
```

### Periodic Publish

At the interval specified by the configuration option for each resource, the agent queries the system and publishes metrics to the message bus under the configured topic.

Example of a `LoadAverage` publish captured by the Listener agent in the VOLTTRON log:

```log
2026-08-25 12:03:50,435 (volttron-listener-2.0.0rc3) listener.agent INFO: Peer: pubsub, Sender: platform.sysmon:, Bus: , Topic: datalogger/Log/Platform/CPU/LoadAverage, Headers: {'Date': '2026-08-25T17:03:50.426814+00:00', 'min_compatible_version': '3.0', 'max_compatible_version': ''}, Message:
{'FifteenMinute': {'Readings': ['2026-08-25T17:03:50.426814+00:00',
                                0.009765625],
                   'Units': 'load_average',
                   'data_type': 'float',
                   'tz': 'UTC'},
 'FiveMinute': {'Readings': ['2026-08-25T17:03:50.426814+00:00', 0.05517578125],
                'Units': 'load_average',
                'data_type': 'float',
                'tz': 'UTC'},
 'OneMinute': {'Readings': ['2026-08-25T17:03:50.426814+00:00', 0.14404296875],
               'Units': 'load_average',
               'data_type': 'float',
               'tz': 'UTC'}}
```

## Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
