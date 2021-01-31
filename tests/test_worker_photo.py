"""test_worker_photo

Tests for media_worker - photos

Sample images are from github.com:ianare/exif-samples

created 28-jan-2021 by richb@instantlinux.net
"""

import boto3
from moto import mock_s3
import os
from unittest import mock

from apicrud.media.worker_processing import MediaProcessing
from apicrud.utils import gen_id, utcnow

import test_base


class TestWorkerPhoto(test_base.TestBase):

    def setUp(self):
        self.authorize()
        response = self.call_endpoint('/album?filter={"name":"work"}', 'get')
        result = response.get_json()
        if response.status_code == 200 and result['count'] == 1:
            self.album_id = response.get_json()['items'][0]['id']
        else:
            response = self.call_endpoint('/album', 'post', data=dict(
                name='work'))
            self.assertEqual(response.status_code, 201)
            self.album_id = response.get_json()['id']
        self.uri = 'https://%s.s3.amazonaws.com' % self.bucket

    @mock.patch('apicrud.media.storage.StorageAPI.get_object')
    @mock.patch('apicrud.media.storage.StorageAPI.get_file_meta')
    def test_photo(self, mock_meta, mock_storage):
        record = dict(name='Sony_HDR-HC3.jpg', size=3565,
                      album_id=self.album_id,
                      storage_id=self.default_storage_id)
        expected = dict(
            path='test/Sony_HDR-HC3', caption=None, format_original='jpeg',
            sha1='569abe4bdd9aef0dd791a950beb1dfa8d7eee408',
            sha256='4f707d9b40d423a5246748bc1e05b66c'
                   '4b87e30863f7a51ce18904a7ec43a39e',
            compression=None, is_encrypted=False,
            datetime_original='2007-06-15T04:42:32Z', gps_altitude=None,
            height=64, make='SONY', model='HDR-HC3', orientation=1, width=100,
            duration=None, category_id='x-3423ceaf', category='default',
            uid=self.test_uid, privacy='invitee', owner=self.test_person_name,
            rbac='dru', status='active', **record)
        mock_storage.return_value = open(os.path.join(os.path.dirname(
            __file__), 'data', record['name']), 'rb').read()

        id = gen_id()
        mock_meta.return_value = dict(
            created=utcnow(),
            ctype='jpeg',
            duration=None,
            fid=id,
            height=64,
            modified=None,
            name=record['name'],
            oid='x-589a2b51',
            path='test/%s' % record['name'].split('.')[0],
            pid=self.album_id,
            sid=self.default_storage_id,
            size=record['size'],
            uid=self.test_uid,
            width=100)

        media = MediaProcessing(self.test_uid, id)
        media.photo(media.meta)
        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        self.assertEqual(result['thumbnail50x50'][:22],
                         'data:image/jpeg;base64')
        del(result['created'])
        expected['id'] = id
        del(expected['album_id'])
        del(result['thumbnail50x50'])
        self.assertEqual(result, expected)

    @mock_s3
    @mock.patch('apicrud.media.storage.StorageAPI.get_file_meta')
    def test_gps_meta(self, mock_meta):
        record = dict(name='DSCN0012.jpg', size=159137,
                      album_id=self.album_id,
                      storage_id=self.default_storage_id)
        expected = dict(
            caption=None, format_original='jpeg',
            sha1='629b0b141634d6c0906e49af448bec8d755ba32c',
            sha256='84d60184ac4098b7967e2ef6dae6b03f'
                   'c0d98b24624d2b57412dbcd7cb864680',
            compression=None, is_encrypted=False,
            datetime_original='2008-10-22T16:29:49Z',
            geo=[11.8853949, 43.4671566], gps_altitude=None, height=480,
            width=640, make='NIKON', model='COOLPIX P6000', orientation=1,
            duration=None, category_id='x-3423ceaf', category='default',
            uid=self.test_uid, privacy='invitee', owner=self.test_person_name,
            rbac='dru', status='active', **record)

        id = gen_id()
        expected['path'] = 'test/%s/%s/DSCN0012' % (self.test_uid, id)
        mock_meta.return_value = dict(
            created=utcnow(),
            ctype='jpeg',
            duration=None,
            fid=id,
            height=64,
            modified=None,
            name=record['name'],
            oid='x-589a2b51',
            path=expected['path'],
            pid=self.album_id,
            sid=self.default_storage_id,
            size=record['size'],
            uid=self.test_uid,
            width=100)

        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=self.bucket)
        conn.Object(
            self.bucket, expected['path'] + '.jpeg').put(Body=open(
                os.path.join(os.path.dirname(__file__), 'data',
                             record['name']), 'rb').read())
        media = MediaProcessing(self.test_uid, id)
        media.photo(media.meta)
        contents = []
        for item in conn.Bucket(self.bucket).objects.filter(
                Prefix=expected['path']).all():
            contents.append(dict(key=item.key, size=item.size))
        self.assertCountEqual(contents, [
            dict(key='%s.jpeg' % expected['path'], size=record['size']),
            dict(key='%s.120.jpeg' % expected['path'], size=5902)])

        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        self.assertEqual(result['thumbnail50x50'][:22],
                         'data:image/jpeg;base64')
        del(result['created'])
        expected['id'] = id
        del(expected['album_id'])
        del(result['thumbnail50x50'])
        self.assertEqual(result, expected)

    @mock_s3
    @mock.patch('apicrud.media.storage.StorageAPI.get_file_meta')
    def test_mp4(self, mock_meta):
        record = dict(name='Video-5sec.mp4', size=179698,
                      album_id=self.album_id,
                      storage_id=self.default_storage_id)
        expected = dict(
            caption=None, format_original='mp4',
            sha1='c4ec0e5719b173db1063afb8ee100fe534382808',
            sha256='38c8925017431d67a63b6ca8c665eccb'
                   'cf9b00e99b78a9ca8182b0f637611066',
            compression=None, is_encrypted=False,
            datetime_original=None,
            gps_altitude=None, height=320,
            width=560, make=None, model=None, orientation=None,
            duration=None, category_id='x-3423ceaf', category='default',
            uid=self.test_uid, privacy='invitee', owner=self.test_person_name,
            rbac='dru', status='active', **record)

        id = gen_id()
        expected['path'] = 'test/%s/%s/Video-5sec' % (self.test_uid, id)
        mock_meta.return_value = dict(
            created=utcnow(),
            ctype='mp4',
            duration=None,
            fid=id,
            height=320,
            modified=None,
            name=record['name'],
            oid='x-89a2b515',
            path=expected['path'],
            pid=self.album_id,
            sid=self.default_storage_id,
            size=record['size'],
            uid=self.test_uid,
            width=560)

        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=self.bucket)
        conn.Object(
            self.bucket, expected['path'] + '.mp4').put(Body=open(
                os.path.join(os.path.dirname(__file__), 'data',
                             record['name']), 'rb').read())
        media = MediaProcessing(self.test_uid, id)
        media.video(media.meta)
        contents = []
        for item in conn.Bucket(self.bucket).objects.filter(
                Prefix=expected['path']).all():
            contents.append(dict(key=item.key, size=item.size))
        self.assertCountEqual(contents, [
            dict(key='%s.mp4' % expected['path'], size=record['size'])])

        response = self.call_endpoint('/picture/%s' % id, 'get')
        result = response.get_json()
        del(result['created'])
        expected['id'] = id
        del(expected['album_id'])
        del(result['thumbnail50x50'])
        self.assertEqual(result, expected)

    """
    More tests: scaling, video, storage
    """
