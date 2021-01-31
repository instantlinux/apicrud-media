"""test_albums

Tests for albums controller

created 8-nov-2019 by richb@instantlinux.net
"""

import constants
import test_base


class TestAlbums(test_base.TestBase):

    def setUp(self):
        self.authorize(username=self.admin_name, password=self.admin_pw)

    def test_add_and_fetch_album(self):
        record = dict(name='my album', sizes=[240, 1024])
        expected = dict(
            cover_id=None, list_id=None, category='default',
            pictures=[], category_id=self.adm_cat_id, privacy='invitee',
            encryption=None, password=None, owner=self.adm_person_name,
            uid=self.admin_uid, rbac='dru', status='active',
            **record)
        response = self.call_endpoint('/album', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/album/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        result.pop('event_id', None)
        expected['id'] = id
        expected['sizes'].append(self.config.DEFAULT_GRANTS['photo_res_max'])
        self.assertEqual(result, expected)

    def test_update_album(self):
        record = dict(name='your album', sizes=[
            int(x) for x in constants.DEFAULT_THUMBNAIL_SIZES.split(',')])
        updated = dict(name='album two')
        expected = dict(
            cover_id=None, list_id=None,
            pictures=[], category='default', category_id=self.adm_cat_id,
            privacy='invitee', owner=self.adm_person_name,
            encryption=None, password=None, uid=self.admin_uid,
            rbac='dru', status='active', **record)

        response = self.call_endpoint('/album', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/album/%s' % id, 'put', data=dict(
            record, **updated))
        self.assertEqual(response.status_code, 200, 'put failed message=%s' %
                         response.get_json().get('message'))
        response = self.call_endpoint('/album/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        del(result['modified'])
        result.pop('event_id', None)
        expected.update(updated)
        expected['id'] = id
        self.assertEqual(result, expected)

    """
    TODO remove, this is a crap test, should return 405 as admin or
    should run as non-admin
    def test_update_invalid(self):
        record = dict(name='your album', sizes=[
            int(x) for x in constants.DEFAULT_THUMBNAIL_SIZES.split(',')])
        updated = dict(name='album two', uid='x-invalid1')

        response = self.call_endpoint('/album', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/album/%s' % id, 'put', data=dict(
            record, **updated))
        self.assertEqual(response.status_code, 403, 'put failed message=%s' %
                         response.get_json().get('message'))
    """

    # TODO test get populated album with details=true

    def test_album_delete(self):
        record = dict(name='wedding cake', sizes=[
            int(x) for x in constants.DEFAULT_THUMBNAIL_SIZES.split(',')])
        expected = dict(
            cover_id=None, list_id=None,
            pictures=[], category='default', category_id=self.adm_cat_id,
            privacy='invitee', owner=self.adm_person_name,
            encryption=None, password=None, uid=self.admin_uid,
            rbac='dru', status='disabled', **record)

        response = self.call_endpoint('/album', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/album/%s' % id, 'delete')
        self.assertEqual(response.status_code, 204)

        # The record should still exist, with disabled status
        response = self.call_endpoint('/album/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        result.pop('event_id', None)
        expected['id'] = id
        expected['sizes'].append(self.config.DEFAULT_GRANTS['photo_res_max'])

        self.assertEqual(result, expected)

        # Force delete -- should no longer exist
        response = self.call_endpoint('/album/%s?force=true' % id, 'delete')
        self.assertEqual(response.status_code, 204)
        response = self.call_endpoint('/album/%s' % id, 'get')
        result = response.get_json()
        self.assertEqual(response.status_code, 404)

    def test_invalid_album(self):
        response = self.call_endpoint('/album?filter={"name":"invalid"}',
                                      'get')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['count'], 0)

        response = self.call_endpoint('/album/x-invalid8', 'get')
        self.assertEqual(response.status_code, 404)
