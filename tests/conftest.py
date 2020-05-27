import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--proxies", action="store", default='http://192.168.0.10:8888,https://192.168.0.10:8888', help='addresses of proxy servers'
    )


@pytest.fixture
def cmdopt_proxies(request):
    return request.config.getoption("--proxies")