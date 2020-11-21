from abc import ABC
import json
from pimetrics.probe import APIProbe


class APIStub(APIProbe, ABC):
    def __init__(self, testfiles=None):
        APIProbe.__init__(self, url='')
        self.testfiles = testfiles if testfiles is not None else dict()

    def call(self, endpoint='', headers=None, body=None, params=None, method=APIProbe.Method.GET):
        if endpoint in self.testfiles:
            with open(self.testfiles[endpoint]['filename'], 'r') as f:
                content = f.read()
                raw = self.testfiles[endpoint]['raw'] if 'raw' in self.testfiles[endpoint] else False
                return json.loads(content) if raw is False else content
        return None
