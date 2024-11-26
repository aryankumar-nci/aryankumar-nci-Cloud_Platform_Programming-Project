import boto3
from django.conf import settings

def send_sns_email(subject, message):
    """Send an email using AWS SNS."""
    sns_client = boto3.client(
        'sns',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    try:
        response = sns_client.publish(
            TopicArn=settings.SNS_TOPIC_ARN,
            Message=message,
            Subject=subject,
        )
        return response
    except Exception as e:
        print(f"Error sending SNS email: {e}")
        return None
