import os

profile = os.environ.get("CALINIFY_TRANSPORT_SERVER_PROFILE")

if profile == "PROD":

    DB_HOST = os.environ.get("CALINIFY_PROD_DATABASE_HOST")
    DB_USERNAME = os.environ.get("CALINIFY_PROD_DATABASE_USERNAME")
    DB_PASSWORD = os.environ.get("CALINIFY_PROD_DATABASE_PASSWORD")
    DB_PORT = os.environ.get("CALINIFY_PROD_DATABASE_PORT")
    DB_TABLE_NAME = os.environ.get("CALINIFY_PROD_DATABASE_TABLE_NAME")
    
    S3_IAM_ACCESS_KEY = os.environ.get("S3_IAM_ACCESS_KEY")
    S3_IAM_SECRET_KEY = os.environ.get("S3_IAM_SECRET_KEY")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    AWS_REGION = os.environ.get("AWS_REGION")

else:
    from dotenv import dotenv_values

    ENV = dotenv_values(f'{os.path.dirname(__file__)}/.env')

    DB_HOST = ENV["CALINIFY_DATABASE_HOST"]
    DB_USERNAME = ENV["CALINIFY_DATABASE_USERNAME"]
    DB_PASSWORD = ENV["CALINIFY_DATABASE_PASSWORD"]
    DB_PORT = ENV["CALINIFY_DATABASE_PORT"]
    DB_TABLE_NAME = ENV["CALINIFY_DATABASE_TABLE_NAME"]
    
    S3_IAM_ACCESS_KEY = ENV["S3_IAM_ACCESS_KEY"]
    S3_IAM_SECRET_KEY = ENV["S3_IAM_SECRET_KEY"]
    S3_BUCKET_NAME = ENV["S3_BUCKET_NAME"]
    AWS_REGION = ENV["AWS_REGION"]
