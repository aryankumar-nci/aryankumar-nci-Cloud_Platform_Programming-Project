import boto3
import json
from botocore.exceptions import ClientError
from django.conf import settings


def get_s3_client():
    try:
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN or None,
            region_name=settings.AWS_S3_REGION_NAME,
        )
    except ClientError as e:
        print(f"Error creating S3 client: {e}")
        raise



def create_bucket():
  
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise ValueError("Bucket name is not set. Ensure AWS_STORAGE_BUCKET_NAME is configured in your .env file.")

    region = settings.AWS_S3_REGION_NAME
    s3_client = get_s3_client()

    try:
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        print(f"Bucket '{bucket_name}' created successfully.")
        return True
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        return False


def add_bucket_policy():
   
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise ValueError("Bucket name is not set. Ensure AWS_STORAGE_BUCKET_NAME is configured in your .env file.")

    s3_client = get_s3_client()

    # Correct bucket policy as a Python dictionary
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }

    try:
        # Convert policy dictionary to JSON string
        policy_json = json.dumps(policy)

        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=policy_json)
        print(f"Public read policy applied to bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        print(f"Error applying bucket policy: {e}")
        return False


def configure_cors():
    """
    Configures CORS rules for the bucket specified in AWS_STORAGE_BUCKET_NAME.
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise ValueError("Bucket name is not set. Ensure AWS_STORAGE_BUCKET_NAME is configured in your .env file.")

    s3_client = get_s3_client()

    cors_rules = [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3000,
        }
    ]

    try:
        s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration={"CORSRules": cors_rules})
        print(f"CORS configuration applied to bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        print(f"Error configuring CORS: {e}")
        return False


def upload_to_s3(file_obj, file_name):
    try:
        s3_client = get_s3_client()
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            file_name,
            ExtraArgs={"ACL": "public-read"}  
        )
        return f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None


def delete_from_s3(file_name):
   
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise ValueError("Bucket name is not set. Ensure AWS_STORAGE_BUCKET_NAME is configured in your .env file.")

    s3_client = get_s3_client()

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        print(f"File '{file_name}' deleted successfully from bucket '{bucket_name}'.")
        return True
    except ClientError as e:
        print(f"Error deleting file: {e}")
        return False
