import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #From Docker
    sql_server = "localhost"

    sql_user = os.environ['DB_REMOTE_ROOT_NAME'] if 'DB_REMOTE_ROOT_NAME' in os.environ else 'Jesualdo'
    sql_password = os.environ['DB_REMOTE_ROOT_PASS'] if 'DB_REMOTE_ROOT_PASS' in os.environ else 'Jesualdo2020'
    sql_db = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else 'coviddb'

#Testing git ignore