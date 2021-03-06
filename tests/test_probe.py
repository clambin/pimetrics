import os
import pytest
from pimetrics.probe import Probe, FileProbe, SysFSProbe, ProcessProbe, Probes


class SimpleProbe(Probe):
    def __init__(self, test_sequence):
        super().__init__()
        self.test_sequence = test_sequence
        self.index = 0

    def measure(self):
        output = self.test_sequence[self.index]
        self.index = (self.index + 1) % len(self.test_sequence)
        return output


class SimpleProcessProbe(ProcessProbe):
    def __init__(self, command):
        super().__init__(command)

    def process(self, lines):
        val = 0
        for line in lines:
            val += int(line)
        return val


def test_simple():
    testdata = [1, 2, 3, 4]
    probe = SimpleProbe(testdata)
    for val in testdata:
        probe.run()
        assert probe.measured() == val


def test_file():
    # create the file
    open('testfile.txt', 'w')
    probe = FileProbe('testfile.txt')
    expected = ""
    for val in range(1, 10):
        with open('testfile.txt', 'a') as f:
            f.write(f'{val}\n')
        expected += f'{val}\n'
        probe.run()
        assert probe.measured() == expected
    os.remove('testfile.txt')


def test_bad_file():
    with pytest.raises(FileNotFoundError):
        FileProbe('testfile.txt')


def test_sysfs():
    # create the file
    open('testfile.txt', 'w')
    probe = SysFSProbe('testfile.txt')
    for val in range(1, 10):
        with open('testfile.txt', 'w') as f:
            f.write(f'{val}')
        probe.run()
        assert probe.measured() == val
    os.remove('testfile.txt')


def test_process():
    probe = SimpleProcessProbe('/bin/sh -c ./process_ut.sh')
    out = 0
    while probe.running():
        probe.run()
        out += probe.measured()
    assert out == 55


def test_bad_process():
    with pytest.raises(FileNotFoundError):
        SimpleProcessProbe('missing_process_ut.sh')


def test_probes():
    test_data = [
        [0, 1, 2, 3, 4],
        [4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4],
        [4, 3, 2, 1, 0]
    ]
    probes = Probes()
    for test in test_data:
        probes.register(SimpleProbe(test))
    for i in range(len(test_data[0])):
        probes.run()
        results = probes.measured()
        for j in range(len(results)):
            target = i if j % 2 == 0 else 4 - i
            assert results[j] == target
