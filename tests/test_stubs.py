import xmltodict
from pimetrics.stubs import APIStub


test_files = {
    '/json': {
        'filename': 'samples/sample.json',
        'raw': False
    },
    '/xml': {
        'filename': 'samples/sample.xml',
        'raw': True
    }
}


class APIStubTest(APIStub):
    def __init__(self, files):
        super().__init__(files)

    def measure(self):
        pass


def test_stub():
    probe = APIStubTest(test_files)

    output = probe.call('/json')
    assert output['1']['name'] == 'foo'
    assert output['1']['firstName'] == 'snafu'
    assert output['2']['name'] == 'bar'
    assert output['2']['firstName'] == 'ufans'
    output = xmltodict.parse(probe.call('/xml'), 'UTF-8')
    assert output['users']['user'][0]['@id'] == '1'
    assert output['users']['user'][0]['name'] == 'foo'
    assert output['users']['user'][0]['firstName'] == 'snafu'
    assert output['users']['user'][1]['@id'] == '2'
    assert output['users']['user'][1]['firstName'] == 'ufans'
