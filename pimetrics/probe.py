# Copyright 2020 by Christophe Lambin
# All rights reserved.

"""
A set of Probes to measure values from different sources and report them to a reporting system (e.g. Prometheus)
"""

import queue
import shlex
import subprocess  # nosec
import threading
import requests
from abc import ABC, abstractmethod


class Probe(ABC):
    """
    Base class for the pimetrics probe.  Calling code should call Probe.run() to measure a new value.
    Measuring goes through the following flow:
        - measure()  measures a new data point
          ->  process() performs any processing logic on the measured data
              ->  report() reports the processed value to a reporting system (e.g. prometheus)

    When creating a derived class, at least the following should be overrideen:
        - measure() to implement the measuring logic
        - report() to report the measured value to the reporting system

    More complex systems may override process() to separate the measument logic from any more complex
    data processing logic.
    """
    def __init__(self):
        """Constructor"""
        self.output = None

    @abstractmethod
    def measure(self):
        """Measure one or more values. Override this method to implement measuring algorithm"""

    def process(self, output):
        """ Process any measured data before reporting it.  By default, this passed through the measured data"""
        return output

    def report(self, output):
        """
        Report the measured data to the reporting system. Base method records the measured value. It can be
        retrieved through Probe.measured().
        """
        pass

    def measured(self):
        """Returns the last measured & processed value"""
        return self.output

    def run(self):
        """
        Measure, process & report a data point.

        This method typically should not need to be overriden.
        """
        output = self.measure()
        output = self.process(output)
        self.output = output
        self.report(output)


class Probes:
    """
    Convenience class to make code a little simpler.

    Rather than calling Probe().run() for each probe, one can register each probe through Probes.register(probe)
    and then call Probes.run() to measure all registed probes.
    """
    def __init__(self):
        """Class constructor"""
        self.probes = []

    def register(self, probe):
        """Register a probe"""
        self.probes.append(probe)
        return probe

    def run(self):
        """Run all probes"""
        for probe in self.probes:
            probe.run()

    def measured(self):
        """
        Get the last value of each registered probe.

        Values are returned in the order the probes were registed in.
        """
        return [probe.measured() for probe in self.probes]


class FileProbe(Probe):
    """
    FileProbe measures (reads) the value of a specified file.

    Any processing logic can be implemented in an overriden process() method. The default implementation
    returns the full content of the file.
    """
    def __init__(self, filename):
        """
        Constructor.  Filename specifies the file to be measured

        Throws a FileNotFoundError exception if the file does not exist at the time of object creation.
        """
        super().__init__()
        self.filename = filename
        f = open(self.filename)
        f.close()

    def measure(self):
        with open(self.filename) as f:
            return ''.join(f.readlines())


class SysFSProbe(FileProbe):
    """
    SysFSProbe extends FileProbe for use in measuring single-line files in /sys filesystems.

    Since /sys values may be larger than needed for reporting (e.g. clock frequencies measured in Hz,
    rather than more user-friendly MHz, the constructor takes a divider argument to divide the measured
    value before reporting it.
    """
    def __init__(self, filename, divider=1):
        """
        Class constructor.

        filename specifies the file to be measured.
        divider specifies the value the measured value will be divided by.

        e.g. if the measured value is in Hz, but we want to report in MHz, specify 1000000. The default is 1.
        """
        super().__init__(filename)
        self.divider = divider

    def measure(self):
        """Measure the value in the file, taking into account the specified divider."""
        content = super().measure()
        return float(content) / self.divider


class _ProcessReader:
    """
    Helper class for ProcessProbe
    """
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, encoding='utf-8')  # nosec
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._enqueue_output)
        self.thread.daemon = True
        self.thread.start()

    def _enqueue_output(self):
        for line in iter(self.process.stdout.readline, ''):
            self.queue.put(line)
        self.process.stdout.close()

    def read(self):
        out = []
        try:
            while True:
                line = self.queue.get_nowait()
                out.append(line)
        except queue.Empty:
            pass
        return out

    def running(self):
        return self.thread.is_alive() or not self.queue.empty()


class ProcessProbe(Probe):
    """
    ProcessProbe measures values reported by an externally spawned process.

    Typical example would be to report latency & packet loss measured by a ping command.
    See https://github.com/clambin/pinger for an example
    """
    def __init__(self, cmd):
        """Class constructor.  cmd specifies the command to run"""
        super().__init__()
        self.cmd = cmd
        self.reader = _ProcessReader(cmd)

    def running(self):
        """Check if the spawned process is still running. Useful to see if the Probe should be recreated."""
        return self.reader.running()

    def measure(self):
        """Read the output of the spawned command. Processing logic should be in ProcessProbe.process()."""
        output = None
        # process may not have any data to measure
        while output is None:
            lines = []
            for line in self.reader.read():
                lines.append(line)
            output = lines
        return output


class APIProbe(Probe, ABC):
    """
    APIProbe measures values reported by an API. See https://github.com/clambin/pimon for an example.

    Currently only HTTP GET & POST are supported.

    Since API calls require specific setup, measure should be overriden to specify application-specific logic.
    """
    def __init__(self, url):
        super().__init__()
        self.url = url

    def get(self, endpoint=None, headers=None, body=None, params=None):
        """Call the API via HTTP GET"""
        url = f'{self.url}{endpoint}' if endpoint else self.url
        return requests.get(url, headers=headers, json=body, params=params)

    def post(self, endpoint=None, headers=None, body=None):
        """Call the API via HTTP POST"""
        url = f'{self.url}{endpoint}' if endpoint else self.url
        return requests.post(url, headers=headers, json=body)
