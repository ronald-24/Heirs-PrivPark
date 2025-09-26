import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4
from typing import BinaryIO

from app.core.config import get_settings


def _get_s3_client():
    settings = get_settings()
    session = boto3.session.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", None),
        region_name=os.getenv("AWS_S3_REGION", settings.env),
    )
    return session.client("s3")


def upload_fileobj_to_s3(file_obj: BinaryIO, filename: str, content_type: str | None = None) -> str:
    bucket = os.getenv("AWS_S3_BUCKET") or None
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET not configured")
    s3 = _get_s3_client()
    key = f"parking_photos/{uuid4().hex}_{filename}"
    extra_args = {"ACL": "public-read"}
    if content_type:
        extra_args["ContentType"] = content_type
    try:
        s3.upload_fileobj(file_obj, bucket, key, ExtraArgs=extra_args)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"S3 upload failed: {exc}")
    region = os.getenv("AWS_S3_REGION") or None
    # Construct public URL (works for most regions)
    if region:
        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return f"https://{bucket}.s3.amazonaws.com/{key}"
