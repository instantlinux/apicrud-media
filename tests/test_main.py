"""test_main

Tests for top-level main app

created 17-oct-2019 by richb@instantlinux.net
"""

import apicrud._version

import test_base
import _version


class TestMain(test_base.TestBase):

    # tutorial:
    # https://www.patricksoftwareblog.com/unit-testing-a-flask-application/

    def test_healthcheck(self):
        expected = dict(
            description=self.config.APPNAME + ' - ' + 'media',
            notes=['build_date:' + _version.build_date, 'schema:960a020329f8',
                   'apicrud_version:' + apicrud._version.__version__],
            releaseId='unset',
            serviceId='media',
            status='pass',
            version=_version.__version__)
        response = self.call_endpoint('/health', 'get')
        self.assertEqual(response.status_code, 200, 'unexpected result %s' %
                         response.get_json().get('output'))
        self.assertEqual(response.get_json(), expected)

    def test_auth(self):
        expected = self.settings_id
        response = self.call_endpoint('/auth', 'post', data=dict(
            username=self.username, password=self.password))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['settings_id'], expected)
        response = self.call_endpoint('/auth', 'post', data=dict(
            username=self.username, password=''))
        self.assertEqual(response.status_code, 400)
