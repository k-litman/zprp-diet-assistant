# http://stackoverflow.com/questions/10390244/
# Full-fledge class: https://stackoverflow.com/a/18046120/104731
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import setting


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
    default_acl = setting("AWS_DEFAULT_ACL_MEDIA", None)
    bucket_name = setting("AWS_STORAGE_MEDIA_BUCKET_NAME", None)
    querystring_auth = setting("AWS_MEDIA_QUERYSTRING_AUTH", None)
