import os

profile = os.environ.get("CALINIFY_TRANSPORT_SERVER_PROFILE")

if profile == "DEV":

    DB_HOST = os.environ.get("CALINIFY_DEV_DATABASE_HOST")
    DB_USERNAME = os.environ.get("CALINIFY_DEV_DATABASE_USERNAME")
    DB_PASSWORD = os.environ.get("CALINIFY_DEV_DATABASE_PASSWORD")
    DB_PORT = os.environ.get("CALINIFY_DEV_DATABASE_PORT")
    DB_TABLE_NAME = os.environ.get("CALINIFY_DEV_DATABASE_TABLE_NAME")

elif profile == "PROD":

    DB_HOST = os.environ.get("CALINIFY_PROD_DATABASE_HOST")
    DB_USERNAME = os.environ.get("CALINIFY_PROD_DATABASE_USERNAME")
    DB_PASSWORD = os.environ.get("CALINIFY_PROD_DATABASE_PASSWORD")
    DB_PORT = os.environ.get("CALINIFY_PROD_DATABASE_PORT")
    DB_TABLE_NAME = os.environ.get("CALINIFY_PROD_DATABASE_TABLE_NAME")

else:
    from dotenv import dotenv_values

    ENV = dotenv_values(f'{os.path.dirname(__file__)}/.env')

    DB_HOST = ENV["CALINIFY_DATABASE_HOST"]
    DB_USERNAME = ENV["CALINIFY_DATABASE_USERNAME"]
    DB_PASSWORD = ENV["CALINIFY_DATABASE_PASSWORD"]
    DB_PORT = ENV["CALINIFY_DATABASE_PORT"]
    DB_TABLE_NAME = ENV["CALINIFY_DATABASE_TABLE_NAME"]