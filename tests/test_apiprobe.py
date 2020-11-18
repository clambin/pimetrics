import pytest
import proxy
import time
from pimetrics.probe import APIProbe


class APIGetTester(APIProbe):
    def __init__(self, url, proxy_url=None):
        super().__init__(url, proxy=proxy_url)

    def measure(self):
        return self.call()


class APIPostTester(APIProbe):
    def __init__(self, url, name, job):
        super().__init__(url)
        self.body = {'name': name, 'job': job}
        self.behave = True

    def measure(self):
        return self.call(body=self.body if self.behave else 'this will trigger an error', method=APIProbe.Method.POST)


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
    probe.run()
    assert probe.measured() is None


@pytest.mark.parametrize('url, result', [
    ('http://localhost:8888', {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}),
    ('localhost:8888', {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}),
    ('', None),
    (None, None),
])
def test_proxy_parser(url, result):
    assert APIProbe._build_proxy_map(url) == result