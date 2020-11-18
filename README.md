# pimetrics
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/clambin/pimetrics?color=green&label=Release&style=plastic)
![Codecov](https://img.shields.io/codecov/c/gh/clambin/pimetrics?style=plastic)
![Build](https://github.com/clambin/pimetrics/workflows/Build/badge.svg?branch=master)
![GitHub](https://img.shields.io/github/license/clambin/pimetrics?style=plastic)

A set of Probes to measure values from different sources and report them to a reporting system (e.g. Prometheus)

## Classes

```
NAME
    pimetrics.probe

DESCRIPTION
    A set of Probes to measure values from different sources and report them to a reporting system (e.g.
    Prometheus)

CLASSES
    abc.ABC(builtins.object)
        Probe
            APIProbe(Probe, abc.ABC)
            FileProbe
                SysFSProbe
            ProcessProbe
    builtins.object
        Probes
    
    class APIProbe(Probe, abc.ABC)
     |  APIProbe(url, proxy=None)
     |  
     |  APIProbe measures values reported by an API. See https://github.com/clambin/pimon for an example.
     |  
     |  Currently only HTTP GET & POST are supported.
     |  
     |  Since API calls require specific setup, measure should be overriden to specify application-specific logic.
     |  
     |  Method resolution order:
     |      APIProbe
     |      Probe
     |      abc.ABC
     |      builtins.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, url, proxy=None)
     |      :param url: the base URL for the API service. Will be extended by the endpoint specified in get/post
     |      :param proxy: URL of Proxy server
     | 
     |  call(self, endpoint=None, headers=None, body=None, params=None, method=<Method.GET: 1>)
     |      Convenience wrapper function for HTTP GET/POST calls
     | 
     |  get(self, endpoint=None, headers=None, body=None, params=None)
     |      Call the API via HTTP GET
     |  
     |  post(self, endpoint=None, headers=None, body=None)
     |      Call the API via HTTP POST
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __abstractmethods__ = frozenset({'measure'})
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from Probe:
     |  
     |  measure(self)
     |      Measure one or more values. Override this method to implement measuring algorithm
     |  
     |  measured(self)
     |      Returns the last measured & processed value
     |  
     |  process(self, output)
     |      Process any measured data before reporting it.  By default, this passes through the measured data
     |      
     |      :param output: value measured by measure()
     |  
     |  report(self, output)
     |      Report the measured & processed data to the reporting system
     |      
     |      :param output: value processed by process()
     |  
     |  run(self)
     |      Measure, process & report a data point.
     |      
     |      This method typically should not need to be overriden.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Probe:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class FileProbe(Probe)
     |  FileProbe(filename)
     |  
     |  FileProbe measures (reads) the value of a specified file.
     |  
     |  Any processing logic can be implemented in an overriden process() method. The default implementation
     |  returns the full content of the file.
     |  
     |  Method resolution order:
     |      FileProbe
     |      Probe
     |      abc.ABC
     |      builtins.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, filename)
     |      Class constructor.
     |      
     |      :param filename: name of the file to be measured
     |      
     |      Throws a FileNotFoundError exception if the file does not exist at the time of object creation.
     |  
     |  measure(self)
     |      Measure one or more values. Override this method to implement measuring algorithm
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __abstractmethods__ = frozenset()
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from Probe:
     |  
     |  measured(self)
     |      Returns the last measured & processed value
     |  
     |  process(self, output)
     |      Process any measured data before reporting it.  By default, this passes through the measured data
     |      
     |      :param output: value measured by measure()
     |  
     |  report(self, output)
     |      Report the measured & processed data to the reporting system
     |      
     |      :param output: value processed by process()
     |  
     |  run(self)
     |      Measure, process & report a data point.
     |      
     |      This method typically should not need to be overriden.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Probe:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Probe(abc.ABC)
     |  Abstract Base class for the pimetrics probe. Calling code should call Probe.run() to measure
     |  a new value.  Measuring goes through the following flow:
     |      -> measure()  measures a new data point
     |         ->  process() performs any processing logic on the measured data
     |             ->  report() reports the processed value to a reporting system (e.g. prometheus)
     |  
     |  When creating a derived class, at least the following should be overridden:
     |      - measure() to implement the measuring logic
     |      - report() to report the measured value to the reporting system
     |  
     |  More complex systems may override process() to separate the measument logic from more complex data
     |  processing logic.
     |  
     |  Method resolution order:
     |      Probe
     |      abc.ABC
     |      builtins.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Class constructor
     |  
     |  measure(self)
     |      Measure one or more values. Override this method to implement measuring algorithm
     |  
     |  measured(self)
     |      Returns the last measured & processed value
     |  
     |  process(self, output)
     |      Process any measured data before reporting it.  By default, this passes through the measured data
     |      
     |      :param output: value measured by measure()
     |  
     |  report(self, output)
     |      Report the measured & processed data to the reporting system
     |      
     |      :param output: value processed by process()
     |  
     |  run(self)
     |      Measure, process & report a data point.
     |      
     |      This method typically should not need to be overriden.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __abstractmethods__ = frozenset({'measure'})
    
    class Probes(builtins.object)
     |  Convenience class to make code a little simpler.
     |  
     |  Rather than calling Probe().run() for each probe, one can register each probe through Probes.register(probe)
     |  and then call Probes.run() to measure all registed probes.
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Class constructor
     |  
     |  measured(self)
     |      Get the last value of each registered probe.
     |      
     |      Values are returned in the order the probes were registed in.
     |  
     |  register(self, probe)
     |      Register a probe
     |      
     |      :param probe: probe to register
     |  
     |  run(self)
     |      Run all probes
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class ProcessProbe(Probe)
     |  ProcessProbe(cmd)
     |  
     |  ProcessProbe measures values reported by an externally spawned process.
     |  
     |  Typical example would be to report latency & packet loss measured by a ping command.
     |  See https://github.com/clambin/pinger for an example
     |  
     |  Method resolution order:
     |      ProcessProbe
     |      Probe
     |      abc.ABC
     |      builtins.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, cmd)
     |      Class constructor.
     |      
     |      :param cmd: command to run
     |  
     |  measure(self)
     |      Read the output of the spawned command. Processing logic should be in ProcessProbe.process().
     |  
     |  running(self)
     |      Check if the spawned process is still running. Useful to see if the Probe should be recreated.
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __abstractmethods__ = frozenset()
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from Probe:
     |  
     |  measured(self)
     |      Returns the last measured & processed value
     |  
     |  process(self, output)
     |      Process any measured data before reporting it.  By default, this passes through the measured data
     |      
     |      :param output: value measured by measure()
     |  
     |  report(self, output)
     |      Report the measured & processed data to the reporting system
     |      
     |      :param output: value processed by process()
     |  
     |  run(self)
     |      Measure, process & report a data point.
     |      
     |      This method typically should not need to be overriden.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Probe:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class SysFSProbe(FileProbe)
     |  SysFSProbe(filename, divider=1)
     |  
     |  SysFSProbe extends FileProbe for use in measuring single-line files in /sys filesystems.
     |  
     |  Since /sys values may be larger than needed for reporting (e.g. clock frequencies measured in Hz,
     |  rather than more user-friendly MHz, the constructor takes a divider argument to divide the measured
     |  value before reporting it.
     |  
     |  Method resolution order:
     |      SysFSProbe
     |      FileProbe
     |      Probe
     |      abc.ABC
     |      builtins.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self, filename, divider=1)
     |      Class constructor.
     |      
     |      :param filename: name of the file to be measured
     |      :param divider: the value the measured value will be divided by.
     |      
     |      e.g. if the measured value is in Hz, but we want to report in MHz, specify 1000000. The default is 1.
     |  
     |  measure(self)
     |      Measure the value in the file, taking into account the specified divider
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  __abstractmethods__ = frozenset()
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from Probe:
     |  
     |  measured(self)
     |      Returns the last measured & processed value
     |  
     |  process(self, output)
     |      Process any measured data before reporting it.  By default, this passes through the measured data
     |      
     |      :param output: value measured by measure()
     |  
     |  report(self, output)
     |      Report the measured & processed data to the reporting system
     |      
     |      :param output: value processed by process()
     |  
     |  run(self)
     |      Measure, process & report a data point.
     |      
     |      This method typically should not need to be overriden.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from Probe:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

NAME
    pimetrics.scheduler

CLASSES
    builtins.object
        Scheduler
    
    class Scheduler(builtins.object)
     |  Methods defined here:
     |  
     |  register(self, probe, interval=5)
     |      Register a probe to run at a certain interval
     |      
     |      :param probe: probe to register
     |      :param interval: interval at which to run the probe
     |  
     |  run(self, once=False, duration=None)
     |      Run all registered probes
     |      
     |      :param once: Run all probes only once (regardless of their specified interval)
     |      :param duration: How long we should run all required probes
     |  
```

## Examples

See the following github sources for examples:

- https://github.com/clambin/pimon - Docker container to report Raspberry Pi CPU speed, temperature & fan status to prometheus.
- https://github.com/clambin/pinger - Measures the latency and packet loss to one of more hosts and reports the data to Prometheus.
- https://github.com/clambin/vpnmon - Monitors OpenVPN connection status & usage

## Author

* **Christophe Lambin**

# License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
