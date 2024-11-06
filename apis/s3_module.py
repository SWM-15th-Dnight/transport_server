from typing import Literal

from fastapi import HTTPException

from config import S3_IAM_SECRET_KEY, S3_IAM_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME
import boto3
from botocore.exceptions import NoCredentialsError


class S3Client:
    
    S3_BUCKET_NAME = S3_BUCKET_NAME
    
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id = S3_IAM_ACCESS_KEY,
            aws_secret_access_key = S3_IAM_SECRET_KEY,
            region_name = AWS_REGION
        )
    
    def upload_file(self, file, uid, T : Literal["export", "import"]):
        
        try:
        # 파일 데이터를 S3에 업로드
            self.s3_client.upload_fileobj(file, S3_BUCKET_NAME, f"{T}/{uid}")
        except NoCredentialsError:
            raise HTTPException(status_code=403, detail="AWS 자격 증명이 없습니다.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {e}, {uid}")

        return uid
    
s3_bucket = S3Client()