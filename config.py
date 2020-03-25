import os

from dotenv import load_dotenv

module_path = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(module_path, '.env'))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_FLASK_KEY')
    API_KEY = os.environ.get('API_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DB_NAME = os.environ.get('RDS_DB_NAME')
    USER = os.environ.get('RDS_USERNAME')
    PASSWORD = os.environ.get('RDS_PASSWORD')
    HOST = os.environ.get('RDS_HOSTNAME')
    PORT = os.environ.get('RDS_PORT')

    SQLALCHEMY_DATABASE_URI = f'postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(module_path, 'app.db')
