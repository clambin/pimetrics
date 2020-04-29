# Copyright 2020 by Christophe Lambin
# All rights reserved.

import queue
import shlex
import subprocess
import threading
import requests
from abc import ABC, abstractmethod


class Probe(ABC):
    def __init__(self):
        self.output = None

    @abstractmethod
    def measure(self):
        """Measure one or more values and return then"""

    def process(self, output):
        return output

    def report(self, output):
        self.output = output

    def measured(self):
        return self.output

    def run(self):
        output = self.measure()
        output = self.process(output)
        self.report(output)


# Convenience class to make code a little simpler
class Probes:
    def __init__(self):
        self.probes = []

    def register(self, probe):
        self.probes.append(probe)
        return probe

    def run(self):
        for probe in self.probes:
            probe.run()

    def measured(self):
        return [probe.measured() for probe in self.probes]


class FileProbe(Probe):
    def __init__(self, filename, divider=1):
        super().__init__()
        self.filename = filename
        self.divider = divider
        f = open(self.filename)
        f.close()

    def process(self, content):
        return float(content) / self.divider

    def measure(self):
        with open(self.filename) as f:
            return ''.join(f.readlines())


class ProcessReader:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, encoding='utf-8')
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


class ProcessProbe(Probe, ABC):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.reader = ProcessReader(cmd)

    @abstractmethod
    def process(self, lines):
        """Implement measurement logic in the inherited class"""

    def running(self):
        return self.reader.running()

    def measure(self):
        output = None
        # process may not have any data to measure
        while output is None:
            lines = []
            for line in self.reader.read(): lines.append(line)
            output = lines
        return output


class APIProbe(Probe, ABC):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def get(self, endpoint=None, headers=None, body=None, params=None):
        url = f'{self.url}{endpoint}' if endpoint else self.url
        return requests.get(url, headers=headers, json=body, params=params)

    def post(self, endpoint=None, headers=None, body=None):
        url = f'{self.url}{endpoint}' if endpoint else self.url
        return requests.post(url, headers=headers, json=body)
