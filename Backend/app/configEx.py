
#INSTRUCTIONS
# 1) RENAME THIS FILE TO config.py
# 2) FILL IN THE VARIABLES

import os
dirname = os.path.dirname(__file__)

class Config(object):
    #JWT AUTHENTICATION
    SECRET_KEY = ''
    
    #DB CONFIGURATION
    SQL_SERVER = "localhost"
    SQL_USER = ''
    SQL_PASSWORD = ''
    SQL_DB_NAME = ''
    SQL_PORT = 3306

    ###SSL Certificate if NEEDED
    
    SQL_SSL_CA = os.path.join(dirname, 'BaltimoreCyberTrustRoot.crt.pem') #Azure certifcate

    #TWITTER API KEYS - FOR SENTIMENT ANALYSIS

    TWITTER_API_KEY = ''
    TWITTER_API_SECRET_KEY = ''
    TWITTER_BEARER_TOKEN = ''
    TWITTER_ACCESS_TOKEN = ''
    TWITTER_ACESS_TOKEN_SECRET = ''