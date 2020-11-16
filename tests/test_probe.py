import os
import time
import pytest
import requests
import proxy
from pimetrics.probe import Probe, FileProbe, SysFSProbe, ProcessProbe, Probes, APIProbe


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


class APIGetTester(APIProbe):
    def __init__(self, url, proxy_url=None):
        super().__init__(url, proxy=proxy_url)

    def measure(self):
        response = self.get()
        if response.status_code != 200:
            return None
        return response.json()


class APIPostTester(APIProbe):
    def __init__(self, url, name, job):
        super().__init__(url)
        self.body = {'name': name, 'job': job}
        self.behave = True

    def measure(self):
        response = self.post(body=self.body if self.behave else 'this will trigger an error')
        if response.status_code != 201:
            return None
        return response.json()


@pytest.fixture
def supply_url():
    return 'https://reqres.in/api'


@pytest.mark.parametrize('user_id, first_name', [(1, 'George'), (2, 'Janet')])
def test_api_get(supply_url, user_id, first_name):
    url = supply_url + "/users/" + str(user_id)
    probe = APIGetTester(url)
    probe.run()
    response = probe.measured()
    assert response is not None
    assert response['data']['id'] == user_id
    assert response['data']['first_name'] == first_name


def test_api_get_exception(supply_url):
    url = supply_url + "/users/50"
    probe = APIGetTester(url)
    probe.run()
    response = probe.measured()
    assert response is None


@pytest.mark.parametrize('name, job', [('morpheus', 'leader'), ('neo', 'the one')])
def test_api_post(supply_url, name, job):
    url = supply_url + "/users/"
    probe = APIPostTester(url, name, job)
    probe.run()
    response = probe.measured()
    assert response is not None
    assert response['name'] == name
    assert response['job'] == job
    assert response['id'] is not None
    assert response['createdAt'] is not None
    probe.behave = False
    probe.run()
    response = probe.measured()
    assert response is None


def test_api_get_proxy(supply_url):
    with proxy.start(['--host', '127.0.0.1', '--port', '8888']):
        time.sleep(2)
        url = supply_url + "/users/1"
        probe = APIGetTester(url, proxy_url='http://localhost:8888')
        probe.run()
        response = probe.measured()
        assert response is not None
        assert response['data']['id'] == 1
        assert response['data']['first_name'] == 'George'


def test_api_get_bad_proxy(supply_url):
    url = supply_url + "/users/1"
    probe = APIGetTester(url, proxy_url='http://localhost:8889')
    with pytest.raises(requests.exceptions.RequestException):
        probe.run()


@pytest.mark.parametrize('url, result', [
    ('http://localhost:8888', {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}),
    ('localhost:8888', {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}),
    ('', None),
    (None, None),
])
def test_proxy_parser(url, result):
    assert APIProbe._build_proxy_map(url) == result
