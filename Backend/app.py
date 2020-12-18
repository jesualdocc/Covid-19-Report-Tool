from flask import request, jsonify
from flask import Flask
from flask.helpers import make_response
from flask_cors import CORS, cross_origin
from config import Config
from sql_connector import SQLConnector
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta 
from functools import wraps 
from tables import convert_user_tuple_to_dict, convert_email_username_tuple_to_dict

app = Flask(__name__)
app.config.from_object(Config)
sql = SQLConnector(Config.sql_server,Config.sql_user,Config.sql_password,Config.sql_db)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
            data = jwt.decode(token, app.config['SECRET_KEY'])

        except jwt.ExpiredSignatureError:
            return jsonify({'message' : 'Token has expired !!'}), 405 

        except: 
            return jsonify({'message' : 'Token is invalid !!'}), 401
        # returns the current logged in users contex to the routes 
        return  f(*args, **kwargs) 
   
    return decorated 

#Authenticates user: return user data and jwt token
@app.route('/login', methods=['POST'])
def login():
    global sql
    result = request.json
    
    if 'userName' in request.json and 'password' in request.json:
        user = sql.find_users(request.json['userName'])
        if user is None:
            return jsonify({'message': 'Username or Password is incorrect'}), 401

        if not check_password_hash(user[5], request.json['password']):
         
            user_dict = convert_user_tuple_to_dict(user)
            # generates the JWT Token with an expiration time
            token_expiration = datetime.utcnow() + timedelta(minutes = 60)
            token = jwt.encode({'id': user[0], 'exp' : token_expiration
        }, app.config['SECRET_KEY']) 

            return make_response(jsonify({'token' : token.decode('UTF-8'), 'user':user_dict}), 201)

    return make_response(jsonify({'message':'Invalid paramentes'}), 400)

#Retrieves list of email and usernames already registered
@app.route('/listof', methods=['GET'])
def list_of_email_username():
    global sql 
    users = sql.find_users()
    users_dict = convert_email_username_tuple_to_dict(users)

    return make_response(jsonify({'users':users_dict}), 200)

        
#Registers a new user
@app.route('/registration', methods=['POST'])
def registration():
    global sql
    result = request.form.to_dict()
    try:
        password = result['password']
        result['password'] = generate_password_hash(password)
        sql.add_user(result)
        
        return jsonify({'message': 'Succesfull'}), 201
    except:
        return jsonify({'request':result}), 400


#Returns actual county data by days 
@app.route('/data',methods = ['GET'])
def data():
    global sql
    result = request.form.to_dict()
    if 'county' in request.form and 'state' in request.form:
        
        county = request.form['county']
        state = request.form['state']
        fips = sql.get_fips(state,county)
        data = None

        if fips is None:
            return jsonify({"ERROR":"COUNTY AND STATE MISMATCH",'request':result}), 204 #No Content

        if 'days' in request.form and request.form['days'].isdigit():
            data = sql.get_county_info(fips,request.form['days'])
        else:
            data = sql.get_county_info(fips)

        return jsonify({'request':result,"fips":fips,'data':data}), 200
    
    else:
        return jsonify({'request':result}), 400
   
   
#Returns list of counties
@app.route('/counties', methods=['GET'])
def get_counties():
    global sql
    result = request.form.to_dict()

    try:
        counties = sql.get_counties()
        return jsonify({'request':result,"data":counties}), 200
    except:
        return jsonify({'request':result}), 500

   
#Returns predictions of cases/deaths by county
@app.route('/predictions', methods = ['GET'])
def get_predictions():
    return ''




if __name__=="__main__":
   app.run()
