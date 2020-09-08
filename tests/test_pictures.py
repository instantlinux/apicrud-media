"""test_picture

Tests for picture controller

created 24-jan-2020 by richb@instantlinux.net
"""

import constants
import test_base


class TestPictures(test_base.TestBase):

    def setUp(self):
        self.authorize()
        response = self.call_endpoint('/album?filter={"name":"album1"}', 'get')
        result = response.get_json()
        if response.status_code == 200 and result['count'] == 1:
            self.album_id = response.get_json()['items'][0]['id']
        else:
            response = self.call_endpoint('/album', 'post', data=dict(
                name='album1'))
            self.assertEqual(response.status_code, 201)
            self.album_id = response.get_json()['id']
        self.uri = 'https://%s.s3.amazonaws.com' % self.bucket

    def test_add_and_fetch_picture(self):
        record = dict(name='my picture', size=1500, album_id=self.album_id,
                      storage_id=self.default_storage_id)
        expected = dict(
            path='', caption=None, thumbnail50x50=None, format_original=None,
            sha1=None, sha256=None, compression=None, is_encrypted=False,
            datetime_original=None, gps_altitude=None, height=None, make=None,
            model=None, orientation=None, width=None, duration=None,
            category_id=self.cat_id, category='default', uid=self.test_uid,
            privacy='invitee', owner=self.test_person_name,
            rbac='dru', status='active', **record)
        response = self.call_endpoint('/picture', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        expected['id'] = id
        del(expected['album_id'])
        self.assertEqual(result, expected)

    def test_add_pictures_fetch_album(self):
        expected = dict(
            name='album2', list_id=None, category='default',
            category_id=self.cat_id, privacy='invitee',
            sizes=[int(x)
                   for x in constants.DEFAULT_THUMBNAIL_SIZES.split(',')],
            media=[], encryption=None, password=None,
            owner=self.test_person_name, uid=self.test_uid,
            rbac='dru', status='active')

        response = self.call_endpoint('/album', 'post', data=dict(
            name=expected['name'], sizes=expected['sizes']))

        self.assertEqual(response.status_code, 201)
        album_id = response.get_json()['id']
        pic_ids = []
        for pic in range(5):
            name = 'photo-%d.jpeg' % pic
            response = self.call_endpoint('/picture', 'post', data=dict(
                name=name, size=1023, album_id=album_id, rank=pic + 1,
                format_original='jpeg',
                path='%s/%s' % (self.test_uid, 'photo-%d' % pic),
                storage_id=self.default_storage_id))
            self.assertEqual(response.status_code, 201)
            id = response.get_json()['id']
            pic_ids.append(id)
            expected['media'].append(dict(
                description=None, height=None, id=id, name=name,
                original='%s/%s/%s' % (self.uri, self.test_uid, name),
                path='%s/%s' % (self.test_uid, 'photo-%d' % pic),
                size=1023, thumbnail='%s/%s/photo-%d.120.jpeg' % (
                    self.uri, self.test_uid, pic),
                type='image/jpeg', uid=self.test_uid, width=None,
                duration=None))
        response = self.call_endpoint('/album/%s?details=true' % album_id,
                                      'get')
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        del(result['created'])
        result.pop('event_id', None)
        for pic in range(5):
            # ignore complicated imageSet values for this test
            del(result['media'][pic]['imageSet'])
        expected['sizes'].append(self.config.DEFAULT_GRANTS['photo_res_max'])
        self.assertEqual(result, dict(id=album_id, pictures=pic_ids,
                                      cover_id=pic_ids[0], **expected))

    def test_update_picture(self):
        record = dict(name='your picture', size=8888, album_id=self.album_id,
                      storage_id=self.default_storage_id)
        updated = dict(name='picture two')
        expected = dict(
            path='', caption=None, thumbnail50x50=None, format_original=None,
            sha1=None, sha256=None, compression=None, is_encrypted=False,
            datetime_original=None, gps_altitude=None, height=None, make=None,
            model=None, orientation=None, width=None, duration=None,
            category_id=self.cat_id, category='default',
            privacy='invitee', owner=self.test_person_name, uid=self.test_uid,
            rbac='dru', status='active', **record)

        response = self.call_endpoint('/picture', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/picture/%s' % id, 'put', data=dict(
            record, **updated))
        self.assertEqual(response.status_code, 200, 'put failed message=%s' %
                         response.get_json().get('message'))
        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        del(result['modified'])
        del(expected['album_id'])
        expected.update(updated)
        expected['id'] = id
        self.assertEqual(result, expected)

    def test_picture_delete(self):
        record = dict(name='old picture', size=1288, album_id=self.album_id,
                      storage_id=self.default_storage_id)
        expected = dict(
            path='', caption=None, thumbnail50x50=None, format_original=None,
            sha1=None, sha256=None, compression=None, is_encrypted=False,
            datetime_original=None, gps_altitude=None, height=None, make=None,
            model=None, orientation=None, width=None, duration=None,
            category_id=self.cat_id, category='default',
            privacy='invitee', owner=self.test_person_name, uid=self.test_uid,
            rbac='dru', status='disabled', **record)

        response = self.call_endpoint('/picture', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        response = self.call_endpoint('/picture/%s' % id, 'delete')
        self.assertEqual(response.status_code, 204)

        # The record should still exist, with disabled status
        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        del(expected['album_id'])
        expected['id'] = id

        self.assertEqual(result, expected)

        # Force delete -- should no longer exist
        response = self.call_endpoint('/picture/%s?force=true' % id, 'delete')
        self.assertEqual(response.status_code, 204)
        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        self.assertEqual(response.status_code, 404)

    def test_invalid_picture(self):
        response = self.call_endpoint('/picture?filter={"name":"invalid"}',
                                      'get')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['count'], 0)

        response = self.call_endpoint('/picture/x-invalid8', 'get')
        self.assertEqual(response.status_code, 404)
