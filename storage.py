import boto3
import os

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

def get_s3_ayca():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AYCA_AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AYCA_AWS_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'),
    )
