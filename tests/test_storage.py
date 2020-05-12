"""test_storage

Tests for storage controller

created 23-jan-2020 by richb@instantlinux.net
"""

import constants
import test_base


class TestStorage(test_base.TestBase):

    def setUp(self):
        self.authorize(username=self.admin_name, password=self.admin_pw)
        # self.bucket = 'unittest-bucket'
        self.bucket = constants.DEFAULT_BUCKET
        self.flask = self.media_flask

    def test_add_and_fetch_storage(self):
        record = dict(name='my storage', bucket=self.bucket)
        expected = dict(
            prefix='', cdn_uri=None, identifier=None, credentials_id=None,
            region=constants.DEFAULT_AWS_REGION,
            privacy='public', owner=self.adm_person_name, uid=self.admin_uid,
            rbac='dru', status='active', **record)
        response = self.call_endpoint('/storage', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/storage/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        expected['id'] = id
        self.assertEqual(result, expected)

    def test_update_storage(self):
        record = dict(name='your storage', bucket='bucket2')
        updated = dict(name='storage two')
        expected = dict(
            prefix='', cdn_uri=None, identifier=None, credentials_id=None,
            region=constants.DEFAULT_AWS_REGION,
            privacy='public', owner=self.adm_person_name, uid=self.admin_uid,
            rbac='dru', status='active', **record)

        response = self.call_endpoint('/storage', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/storage/%s' % id, 'put', data=dict(
            record, **updated))
        self.assertEqual(response.status_code, 200, 'put failed message=%s' %
                         response.get_json().get('message'))
        response = self.call_endpoint('/storage/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        del(result['modified'])
        expected.update(updated)
        expected['id'] = id
        self.assertEqual(result, expected)

    def test_storage_delete(self):
        record = dict(name='wedding cake', bucket=self.bucket)
        expected = dict(
            prefix='', cdn_uri=None, identifier=None, credentials_id=None,
            region=constants.DEFAULT_AWS_REGION,
            privacy='public', owner=self.adm_person_name, uid=self.admin_uid,
            rbac='dru', status='disabled', **record)

        response = self.call_endpoint('/storage', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/storage/%s' % id, 'delete')
        self.assertEqual(response.status_code, 204)

        # The record should still exist, with disabled status
        response = self.call_endpoint('/storage/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        expected['id'] = id

        self.assertEqual(result, expected)

        # Force delete -- should no longer exist
        response = self.call_endpoint('/storage/%s?force=true' % id, 'delete')
        self.assertEqual(response.status_code, 204)
        response = self.call_endpoint('/storage/%s' % id, 'get')
        result = response.get_json()
        self.assertEqual(response.status_code, 404)

    def test_invalid_storage(self):
        response = self.call_endpoint('/storage?filter={"name":"invalid"}',
                                      'get')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['count'], 0)

        response = self.call_endpoint('/storage/x-invalid8', 'get')
        self.assertEqual(response.status_code, 404)
