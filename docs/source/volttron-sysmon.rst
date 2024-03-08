.. _volttron-sysmon:
===============
volttron-sysmon
===============

The System Monitoring Agent (colloquially “SysMon”) can be installed on the platform to monitor system resource metrics, including but not limited to percent CPU utilization, percent system memory (RAM) utilization, and percent storage (disk) utilization based on disk path.

.. _volttron-sysmon:
Configuration and Installation
==============================

Requires
--------

- python >= 3.10
- volttron >= 10.0

Installation
------------

The Sysmon agent can be installed using vctl:

.. code-block:: bash

    vctl install volttron-sysmon --vip-identity agent.sysmon --force --start

Configuration
-------------

You can find the full configuration with all system monitors in place here: https://github.com/eclipse-volttron/volttron-sysmon/sysmon_agent_config.json
for simplicity, you can copy this entire file and set ``poll`` to ``true`` for each system you want to monitor. 

Besides ``poll``, there are four other important options in sysmons configuration.

- ``default_publish_type`` only needs to be specified once in the configuration, this is the default publish type.
- ``base_topic`` also only needs to be specified once. This is the base topic.
- ``point_name`` changes the point name for the specific system monitor. In combination with publish_type and base_topic our data for cpu_precent would be published to volttron with a topic of: **datalogger/Log/Platform/CPU/Percent** using the below json as an example.
- ``check_interval`` adjusts the time in seconds to poll for new system data. This can be modified for each system resource.

The Sysmon agent serves as a wrapper for psutil. You can adjust resource specific options by adjusting false to true in the configuration file. For detailed insights into these options and their impact, you can read the `psutil documentation <https://psutil.readthedocs.io/en/latest/>`_.

JSON RPC Methods
----------------

For subpoints, please refer to the `psutil documentation <https://psutil.readthedocs.io/en/latest/>`_.

- **cpu_percent**:  Returns current CPU utilization percentage over a specified interval.
  
  - *per_cpu* (bool): If True, returns utilization for each CPU core separately. If False, returns overall CPU utilization.
  - *capture_interval* (float or None): Time in seconds over which to measure CPU usage.

- **cpu_times**: Returns the percentage of time the CPU has spent in a given mode
  
  - *per_cpu* (bool): If True, returns statistics for each CPU core separately. If False, returns overall statistics for all cores.
  - `sub_points <https://psutil.readthedocs.io/en/latest/index.html#psutil.cpu_times>`

- **cpu_times_percent**: Returns the percentages of time the CPU has spent in different modes over a specified interval.
  
  - *per_cpu* (bool): If True, returns statistics for each CPU core separately. If False, returns overall statistics for all cores.
  - `sub_points <https://psutil.readthedocs.io/en/latest/index.html#psutil.cpu_times_percent>`
  - *capture_interval* (float or None): The time in seconds over which to measure CPU usage. If None, measures the instantaneous CPU usage since the last call or system start.

- **cpu_count**: Return the number of CPU cores if logical=True or the number of physical CPUs if logical=False

- **cpu_stats**: Return various CPU statistics.
  
  - `sub_points <https://psutil.readthedocs.io/en/latest/index.html#psutil.cpu_stats>`

- **cpu_frequency**: Returns current frequency of the CPU cores.
  
  - *per_cpu* (bool): If True, returns frequency information for each individual CPU core. If False, returns an overall view for the entire CPU.
  - `sub_points <https://psutil.readthedocs.io/en/latest/index.html#psutil.cpu_freq>`

- **memory**: Return memory usage statistics.

- **swap**: Return swap usage statistics.

- **disk_partitions**: Returns information about disk partitions.

- **disk_percent**: Returns usage of disk mounted at configured path.

- **disk_usage**: Returns disk usage statistics.

- **load_average**: Returns load averages.

- **path_usage**: Returns storage used within a filesystem path.

- **path_usage_rate**: Returns rate of change in storage used within a filesystem path in bytes per second.

- **disk_io**: Returns disk input/output statistics.

- **network_io**: Returns network input/output statistics.

- **network_connections**: Return system-wide socket connections.

- **network_interface_addresses**: Returns addresses associated with network interfaces.

- **network_interface_statistics**: Returns information about each network interface.

- **sensors_temperatures**: Returns hardware temperatures.

- **sensors_fans**: Returns fan speed in RPM.

- **sensors_battery**: Returns battery status information.

- **boot_time**: Returns time of last system boot as seconds since the epoch.

- **users**: Returns user session data for users currently connected to the system.
