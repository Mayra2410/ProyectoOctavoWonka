import os

class Config(object):
    SECRET_KEY = 'ClaveSecreta'
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://wonka_app:Wonka2026*@127.0.0.1/wonka'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
from sqlalchemy import create_engine


