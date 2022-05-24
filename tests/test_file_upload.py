"""test_file_upload

Tests for file upload

created 31-jan-2021 by richb@instantlinux.net
"""

import boto3
from datetime import datetime
from moto import mock_s3
import os
from unittest import mock

import constants

import test_base


class TestFileUpload(test_base.TestBase):

    def setUp(self):
        self.authorize()
        response = self.call_endpoint('/album?filter={"name":"upload"}', 'get')
        result = response.get_json()
        if response.status_code == 200 and result['count'] == 1:
            self.album_id = response.get_json()['items'][0]['id']
        else:
            response = self.call_endpoint('/album', 'post', data=dict(
                name='upload'))
            self.assertEqual(response.status_code, 201)
            self.album_id = response.get_json()['id']

    @mock_s3
    def test_get_upload_url(self):
        record = dict(content_type='image/jpeg', height=480, width=720,
                      name='foo.jpg', parent_id=self.album_id, size=25560,
                      storage_id=self.default_storage_id)
        expected = dict(
            params={
                'x-amz-algorithm': 'AWS4-HMAC-SHA256',
                'x-amz-credential': '%s/%s/%s/s3/aws4_request' % (
                    self.access_key_id, datetime.utcnow().strftime('%Y%m%d'),
                    constants.DEFAULT_AWS_REGION)
            },
            upload_url='https://%s.s3.amazonaws.com/' % (self.bucket)
        )
        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        result = response.get_json()
        self.assertEqual(result['params'].pop('key').split('/')[0],
                         self.test_uid)
        self.assertEqual(len(result['params'].pop('x-amz-signature')),
                         64)
        del result['file_id']
        del result['params']['policy']
        del result['params']['x-amz-date']
        self.assertEqual(result, expected)

    @mock_s3
    @mock.patch('media_worker.incoming.delay')
    def test_upload_file(self, mock_incoming):
        record = dict(content_type='image/jpeg', height=64, width=100,
                      name='Sony_HDR-HC3.jpg', parent_id=self.album_id,
                      size=3565, storage_id=self.default_storage_id)

        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 201)
        result = response.get_json()
        file_id = result['file_id']

        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=self.bucket)
        conn.Object(self.bucket, result['params']['key']).put(Body=open(
            os.path.join(os.path.dirname(__file__), 'data',
                         record['name']), 'rb').read())

        response = self.call_endpoint('/upload_complete/%s?status=%s' % (
            file_id, 'done'), 'post')
        self.assertEqual(response.status_code, 201)

        mock_incoming.assert_called_with(self.test_uid, file_id)

    @mock_s3
    @mock.patch('logging.info')
    def test_iphone_filename(self, mock_logging):
        record = dict(content_type='image/jpeg', height=2048, width=3160,
                      name='95a303f2-6504-4b17-968a-4dd8d8435bd3.jpeg',
                      parent_id=self.album_id,
                      size=310565, storage_id=self.default_storage_id)

        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 201)

        mock_logging.assert_called_with(dict(
            action='get_upload_url', name='laMD8mUESxeWik3Y2ENb0w.jpeg',
            uid=self.test_uid, resource='album', size=record['size']))

    @mock_s3
    def test_invalid_storage_cases(self):
        record = dict(content_type='image/jpeg', height=768, width=1024,
                      name='image123.jpeg',
                      size=45181, storage_id=self.default_storage_id)

        self.authorize(username=self.admin_name, password=self.admin_pw)
        response = self.call_endpoint('/album', 'post', data=dict(
            name='restricted'))
        self.assertEqual(response.status_code, 201)
        record['parent_id'] = response.get_json()['id']

        # Post to album that isn't ours
        self.authorize(new_session=True)
        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 403)

        # Post to invalid album
        record['parent_id'] = 'x-invalid3'
        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()['message'],
                         'album not found')

        # Post to invalid storage
        record['parent_id'] = self.album_id
        record['storage_id'] = 'x-invalid4'
        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()['message'],
                         'storage volume not found')

    def test_post_huge_object(self):
        record = dict(content_type='image/jpeg', height=768, width=1024,
                      name='image123.jpeg', size=self.config.DEFAULT_GRANTS[
                          'media_size_max'] + 1, parent_id=self.album_id,
                      storage_id=self.default_storage_id)
        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.get_json()['message'],
                         'file size exceeds max=%d' % (record['size'] - 1))

    def test_post_long_video(self):
        record = dict(content_type='video/mp4', height=480, width=640,
                      name='longvideo.mp4', parent_id=self.album_id,
                      duration=self.config.DEFAULT_GRANTS[
                          'video_duration_max'] + 1,
                      size=1024000, storage_id=self.default_storage_id)
        response = self.call_endpoint('/file_upload_url', 'post', data=record)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.get_json()['message'],
                         'video exceeds maximum duration=%f' % (
                             record['duration'] - 1))

    def test_incomplete_upload(self):
        response = self.call_endpoint('/upload_complete/%s?status=%s' % (
            'x-12345678', 'error_upload'), 'post')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.get_json()['message'],
                         'unhandled frontend status')

    # Edge cases TODO:
    # album max size exceeded
    # blank / unsupported content_type
    # unsupported vendor
    # get_upload_url failure
    # get_file_meta, update_file_meta, del_file_meta failures (redis exception)
    # fetch_album_meta invalid album_id; video within album
    # multiple image sizes in fetch_album
    # invalid storage_id: get/put/del_object
    # del_object
    # generate_presigned exception
    # backblaze vendor test
