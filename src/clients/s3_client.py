import boto3
from botocore.exceptions import ClientError
from src.config.settings import AWS_REGION, S3_BUCKET
from src.common.logger import logger


class S3Client:
    """
    Reusable wrapper around boto3 S3 operations for this project.
    """

    def __init__(self):
        self.bucket = S3_BUCKET
        self.client = boto3.client("s3", region_name=AWS_REGION)

    def upload_json(self, data: bytes, key: str) -> str:
        """
        Upload raw bytes to S3 under the given key.
        Returns the S3 URI of the uploaded object.
        """
        try:
            logger.info(f"Uploading to s3://{self.bucket}/{key}")

            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType="application/json",
            )

            s3_uri = f"s3://{self.bucket}/{key}"
            logger.info(f"Upload successful: {s3_uri}")
            return s3_uri

        except ClientError as err:
            logger.error(f"S3 upload failed: {err}")
            raise