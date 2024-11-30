import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def notify_admin_new_user(username, email):
    """
    Sends an SNS notification to the admin when a new user registers.
    """
    try:
        sns_client = boto3.client(
            "sns",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        message = f"A new user has registered:\n\nUsername: {username}\nEmail: {email}"
        response = sns_client.publish(
            TopicArn=settings.AWS_SNS_TOPIC_ARN,
            Message=message,
            Subject="New User Registration",
        )
        logger.info(f"SNS Notification sent successfully. MessageId: {response['MessageId']}")
        return response
    except ClientError as e:
        logger.error(f"Failed to send SNS notification: {e}")
        raise
