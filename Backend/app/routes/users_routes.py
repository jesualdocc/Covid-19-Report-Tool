#Adds higher lever package to path directory
import sys, os
dirname = os.path.dirname(__file__)
app_package_dir = os.path.join(dirname, '..')
sys.path.append(dirname)
sys.path.append(app_package_dir)

import jsonschema
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import Blueprint
from flask.helpers import make_response
from flask import request, jsonify
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jsonschema import validate
from config import Config
from db.sql_connector import DbManagement
from jwt_auth import token_required

users_bp = Blueprint('users_bp', __name__)
sql = DbManagement()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

#Set up schema for validation
users_schema = {
    "type":"object",
    "properties":{
        "id":{"type":"integer"},
        "firstName":{"type":"string", "maxLength": 44},
        "lastName":{"type":"string", "maxLength":44},
        "email":{"type":"string", "format":"email"},
        "userName":{"type":"string", "minLength":5},
        "password":{"type":"string", "minLength":6},
        "county":{"type":"string"},
        "state":{"type":"string"}
    },
    "required":["userName", "password"]
}

#################################################

@users_bp.route('/login', methods=['POST'])
@limiter.limit("3 per minute")
def login():
    global sql 
    result = request.json

    try:
        #Validate data from client
        validate(result, users_schema)

    except jsonschema.ValidationError as e:
        return make_response(jsonify({'message':'Invalid paramentes'}), 400)
   
    if 'userName' in result and 'password' in result:
        
        user = sql.find_users(result['userName'])
       
        if user is None:
            return jsonify({'message': 'Username or Password is incorrect'}), 401

        if check_password_hash(user[5], result['password']):
            #convert user tuple to dict
            user_dict = {}
            users_table_cols = ('id', 'firstName', 'lastName', 'email', 'userName', 'password', 'county', 'state')
            for i in range(len(users_table_cols)):
                key = users_table_cols[i]
                user_dict[key] = user[i] 

            # generates the JWT Token with an expiration time
            token_expiration = datetime.utcnow() + timedelta(minutes = 60)
            token = jwt.encode({'id': user[0], 'exp' : token_expiration}, Config.SECRET_KEY) 

            return make_response(jsonify({'token' : token.decode('UTF-8'), 'user':user_dict}), 201)
       
        else:
            return make_response(jsonify({'message': 'Username or Password is incorrect'}), 401)

    return make_response(jsonify({'message':'Invalid paramentes'}), 400)

############################################################################
#Registers a new user
@users_bp.route('/registration', methods=['POST'])
@limiter.limit("2 per minute")
def registration():
    global sql
    result = request.json

    try:
        #Validate data from client
        validate(result, users_schema)

    except jsonschema.ValidationError:
        return make_response(jsonify({'message':'Invalid paramentes'}), 400)

    try:
        password = result['password']
        result['password'] = generate_password_hash(password)
        
        sql.add_user(result)
        
        return jsonify({'message': 'Succesfull'}), 201
    except Exception as e:
        return jsonify({'request':result}), 500

############################################################################
#Update user info
@users_bp.route('/profileinfo', methods=['PUT'])
@token_required 
def profile_info():
    global sql
    result = request.json

    try:
        #Validate data from client
        validate(result, users_schema)

    except jsonschema.ValidationError:
        return make_response(jsonify({'message':'Invalid paramentes'}), 400)
    
    if 'changeType' in request.headers:
        if request.headers['changeType'] == 'profile':
        
            try:
                sql.update_user(result)

                return make_response(jsonify({'message': 'Succesfull'}), 201)
            except:
                
                return make_response(jsonify({'request':result}), 400)

        #Change password only
        if request.headers['changeType'] == 'password':
            password = result['password']
           
            result['password'] = generate_password_hash(password)

            try:
                
                sql.update_user(result)

                return make_response(jsonify({'message': 'Succesfull'}), 201)
            except:
                
                return make_response(jsonify({'request':result}), 400)
            
    return make_response(jsonify({'request':result}), 400)
