class Config(object):
    DEBUG = True
    CSRF_ENABLED = True
    SECRET_KEY = '142-836-543'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:toor@localhost/sangfor_report?charset=utf-8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True
