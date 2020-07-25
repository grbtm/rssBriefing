import os

from dotenv import load_dotenv
from django.conf import settings

module_path = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(module_path, '.env'))

# Load Django settings - solely for the email backend
settings.configure({},
                   EMAIL_HOST=os.environ.get('EMAIL_HOST'),
                   EMAIL_PORT=os.environ.get('EMAIL_PORT'),
                   EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER'),
                   EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD'),
                   EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
                   EMAIL_USE_TLS=False,
                   EMAIL_USE_SSL=os.environ.get('EMAIL_USE_SSL'),
                   EMAIL_TIMEOUT=None,
                   EMAIL_SSL_KEYFILE=None,
                   EMAIL_SSL_CERTFILE=None,
                   DEFAULT_CHARSET='utf-8',
                   EMAIL_USE_LOCALTIME=False)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_FLASK_KEY') or 'dev-secret-key'
    API_KEY = os.environ.get('API_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(module_path, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = ['robobriefing@posteo.net']
    BETA_CODE = os.environ.get('BETA_CODE') or 'test'


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
