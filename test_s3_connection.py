import boto3
from src.config.settings import AWS_REGION, S3_BUCKET

def test_connection():
    s3 = boto3.client("s3", region_name=AWS_REGION)

    print(f"Attempting to list contents of bucket: {S3_BUCKET}")

    response = s3.list_objects_v2(Bucket=S3_BUCKET)

    if "Contents" in response:
        print(f"Bucket has {len(response['Contents'])} object(s):")
        for obj in response["Contents"]:
            print(f"  - {obj['Key']}")
    else:
        print("Bucket is empty — connection works, nothing uploaded yet.")

if __name__ == "__main__":
    test_connection()