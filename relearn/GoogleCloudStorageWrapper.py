import base64
import hashlib
from os import path

from google.api_core import exceptions as g_exceptions
from google.cloud import storage as g_storage


class GoogleCloudStorageWrapper:
    @staticmethod
    def md5_base64(filename):
        """Returns md5 hash with base of 64"""
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        hash_md5_base64 = base64.b64encode(hash_md5.digest()).decode('utf-8')
        return hash_md5_base64

    @staticmethod
    def lazy_upload_blob(bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket if it has different hash."""
        storage_client = g_storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        remote_blob = bucket.get_blob(destination_blob_name)

        local_md5 = GoogleCloudStorageWrapper.md5_base64(source_file_name)

        if remote_blob is not None:
            remote_md5 = remote_blob.md5_hash
            if remote_md5 == local_md5:
                print(f'Blob `{destination_blob_name} is '
                      f'already in bucket `{bucket_name}`')
                return

            print(f'Updating blob `{destination_blob_name}` in '
                  f'bucket `{bucket_name}` from `{source_file_name}`')

        blob.upload_from_filename(source_file_name)

        # check for integrity of uploaded file
        uploaded_blob = bucket.get_blob(destination_blob_name)
        uploaded_md5 = uploaded_blob.md5_hash
        if uploaded_md5 != local_md5:
            raise g_exceptions.DataLoss('Downloaded file differs from remote')

        print(f'File `{source_file_name}` successfully uploaded '
              f'to `{destination_blob_name}` of bucket `{bucket_name}`')

    @staticmethod
    def lazy_download_blob(bucket_name, source_blob_name, destination_file_name):
        """Downloads a blob from the bucket if the local version of file differs
        from the remote version (calculated using md5 hash)."""

        storage_client = g_storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        remote_blob = bucket.get_blob(source_blob_name)

        remote_md5 = remote_blob.md5_hash

        if path.exists(destination_file_name):
            local_md5 = GoogleCloudStorageWrapper.md5_base64(destination_file_name)
            if remote_md5 == local_md5:
                print(f'Blob `{source_blob_name}` is already downloaded to `{destination_file_name}`')
                return

        blob.download_to_filename(destination_file_name)

        # check for integrity of downloaded file
        downloaded_md5 = GoogleCloudStorageWrapper.md5_base64(destination_file_name)
        if remote_md5 != downloaded_md5:
            raise g_exceptions.DataLoss('Downloaded file differs from remote')

        print(f'Blob `{source_blob_name}` successfully downloaded to `{destination_file_name}`')
