import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    #DB CONFIG
    sql_server = "localhost"
    sql_user = "root"
    sql_password = "Jesualdo2020"
    sql_db = "coviddb"

    #PASSWORD HASHING
    


