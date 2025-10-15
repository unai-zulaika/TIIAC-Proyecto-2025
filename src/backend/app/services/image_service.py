import boto3
from botocore.config import Config as BotoConfig
from fastapi import Depends
from app.core.config import settings


class ImageService:
    """Simple image service stub for future expansion (validation, uploads, etc.)."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.client = boto3.client(
            "s3",
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
            config=BotoConfig(signature_version="s3v4"),
        )

    def get_presigned_url(self, key: str, minutes: int = 15) -> str:
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=60 * minutes,
        )


def get_image_service() -> ImageService:
    return ImageService()
