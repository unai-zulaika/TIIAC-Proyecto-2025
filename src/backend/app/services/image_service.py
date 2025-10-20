import boto3
from botocore.config import Config as BotoConfig
from app.core.config import get_settings

settings = get_settings()


class ImageService:
    """
    Servicio de imágenes compatible con:
    - MinIO (S3 local): usa endpoint_url + MINIO_ROOT_USER/ROOT_PASSWORD + MINIO_BUCKET_NAME
    - AWS S3 (opcional): usa región + AWS_ACCESS_KEY_ID/SECRET + S3_BUCKET
    La firma de URLs se hace con presigned URLs (GET).
    """

    def __init__(self):
        if settings.USE_MINIO:
            # MinIO
            self.bucket = settings.MINIO_BUCKET_NAME
            self.client = boto3.client(
                "s3",
                endpoint_url=settings.MINIO_ENDPOINT,
                aws_access_key_id=settings.MINIO_ROOT_USER,
                aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
                config=BotoConfig(signature_version="s3v4"),
            )
        else:
            # AWS S3
            self.bucket = settings.S3_BUCKET
            self.client = boto3.client(
                "s3",
                region_name=settings.S3_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
                config=BotoConfig(signature_version="s3v4"),
            )

    def get_presigned_url(self, key: str, minutes: int = 15) -> str:
        """
        Devuelve una URL firmada temporal para descargar el objeto.
        'key' debe coincidir con el campo 'image_s3_key' guardado en la tabla items.
        """
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=60 * minutes,
        )


def get_image_service() -> ImageService:
    return ImageService()
