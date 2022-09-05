import os

from dotenv import load_dotenv
load_dotenv()


class Config(object):
    DEBUG = os.getenv("DEBUG", True)
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///api.sqlite3')
    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT") or os.getcwd()
