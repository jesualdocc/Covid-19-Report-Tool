#Adds higher lever package to path directory
import sys, os
dirname = os.path.dirname(__file__)
app_package_dir = os.path.join(dirname, '..')
sys.path.append(app_package_dir)

import jwt
from functools import wraps 
from flask import request, jsonify
from config import Config

# decorator for verifying the JWT 
def token_required(f): 
    @wraps(f) 
    def decorated(*args, **kwargs): 
        token = None
        # jwt is passed in the request header 
        if 'token' in request.headers: 
            token = request.headers['token'] 
        # return 401 if token is not passed 
        if not token: 
            return jsonify({'message' : 'Token is missing !!'}), 401
   
        try: 
            # decoding the payload to fetch the stored details 
            data = jwt.decode(token, Config.SECRET_KEY)

        except jwt.ExpiredSignatureError:
            return jsonify({'message' : 'Token has expired !!'}), 405 

        except: 
            return jsonify({'message' : 'Token is invalid !!'}), 401
        # returns the current logged in users contex to the routes 
        return  f(*args, **kwargs) 
   
    return decorated 
