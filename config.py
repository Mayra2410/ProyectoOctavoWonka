import os

class Config(object):
    SECRET_KEY = 'ClaveSecreta'
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@127.0.0.1/wonka'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

