import threading
import time
from flask import request, jsonify
from flask import Flask
from flask.helpers import make_response
from flask_cors import CORS
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta 
from functools import wraps 
from tables import convert_user_tuple_to_dict, convert_email_username_tuple_to_dict
from predictor import Covid_Predictor
import schedule
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twitter_textblob import Twitter_Textblob
from sql_connector import SQLConnector
from waitress import serve
from flask_csp.csp import csp_header, csp_default

#Application Configuration
app = Flask(__name__)
app.config.from_object(Config)

#Establisk conection to db 

sql = SQLConnector()

##################################################################################

cors_config = {
    "origins": "*",
}

CORS(app, resources={r"/*": cors_config})

##############################################################

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

######################################################################

config_csp = {
  "default-src": "'self'",
  "script-src": "'self'",
  "img-src": "'self'",
  "object-src": "'self'",
  "plugin-src": "'self'",
  "style-src": "'self'",
  "media-src": "'self'",
  "child-src": "'self'",
  "connect-src": "'self'",
  "base-uri": "'self'"
}
h = csp_default()
h.update(config_csp)

tw = Twitter_Textblob()

####################################################################################
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
#############################################################################

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
##########################################################################################

#Placeholder entry point
@app.route('/')
@csp_header()
def indexpage():
    return 'Server Running @JCC 2020 01/03 - vf'

############################################################################################
#Authenticates user: return user data and jwt token
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    global sql 
   
    if 'userName' in request.json and 'password' in request.json:
        
        user = sql.find_users(request.json['userName'])
       
        if user is None:
            return jsonify({'message': 'Username or Password is incorrect'}), 401

        if check_password_hash(user[5], request.json['password']):
         
            user_dict = convert_user_tuple_to_dict(user)
            # generates the JWT Token with an expiration time
            token_expiration = datetime.utcnow() + timedelta(minutes = 60)
            token = jwt.encode({'id': user[0], 'exp' : token_expiration
        }, app.config['SECRET_KEY']) 

            return make_response(jsonify({'token' : token.decode('UTF-8'), 'user':user_dict}), 201)
       
        else:
            return jsonify({'message': 'Username or Password is incorrect'}), 401

    return make_response(jsonify({'message':'Invalid paramentes'}), 400)

###################################################################################
#Retrieves list of email and usernames already registered
@app.route('/listof', methods=['GET'])
@limiter.limit("5 per minute")
def list_of_email_username():
    global sql 

    users = sql.find_users()
    users_dict = convert_email_username_tuple_to_dict(users)
    return make_response(jsonify({'users':users_dict}), 200)

##############################################################################

#Registers a new user
@app.route('/registration', methods=['POST'])
@limiter.limit("2 per minute")
def registration():
    global sql

    result = request.json
    try:
        password = result['password']
        result['password'] = generate_password_hash(password)
        
        sql.add_user(result)
        
        return jsonify({'message': 'Succesfull'}), 201
    except:
        return jsonify({'request':result}), 400

##############################################################################################

#Returns actual county data by days 
@app.route('/data',methods = ['POST'])
@csp_header(config_csp)
def data():
    global sql 
    
    if 'county' in request.json and 'state' in request.json:
        
        county = request.json['county']
        state = request.json['state']
        fips = sql.get_fips(state,county)
        data = None

        if fips is None:
            return jsonify({"ERROR":"COUNTY AND STATE MISMATCH",'request':{}}), 204 #No Content

        if 'days' in request.json:
            days = None
            try:
                #Make sure days in int
                days = int(request.json['days'])
                
            except:
                return make_response(jsonify({}), 400)

            data = sql.get_county_info(fips, days)
            
        else:
            data = sql.get_county_info(fips)
        
        return make_response(jsonify({"fips":fips,'data':data}), 200)
    
    else:
        return make_response(jsonify({}), 400)
   
#################################################################################

#Returns list of counties
@app.route('/counties', methods=['POST'])
@csp_header(config_csp)
def get_counties():
    
    result = request.json

    if 'state' in result:
        counties = sql.get_counties(result['state'])

        if counties is not None:
            return make_response (jsonify({'data':counties}), 200)

        else:
            return make_response(jsonify({}), 400)

    else:
        return make_response(jsonify({}), 400)
    
############################################################################
#Update user info
@app.route('/profileinfo', methods=['PUT'])
@token_required 
def profile_info():
    global sql

    result = request.json
    
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

###########################################################################################    
#
@app.route('/twitter', methods = ['POST'])
@token_required 
def twitter_feed():
    global sql 
    global tw


    if 'county' in request.json and 'state' in request.json:
        county = request.json['county']
        state = request.json['state']

        #Todo - get geolocation from google maps api to filter tweets
        #Not many tweets geocoded
        #g = "37.469887, -122.0446721, 100mi"
        geocode = []
        #Hashtags, geocode, count
        tweets = tw.get_tweets(['coronavirus', 'covid', 'covid19'], geocode, 20)

        return make_response(jsonify({'tweets':tweets}), 200)

    else:
        return make_response(jsonify({}), 400)


#################################################################################################
#Returns predictions of cases/deaths by county
@app.route('/predictions', methods = ['POST'])
def get_predictions():
    global sql 
    days = 20

    if 'county' in request.json and 'state' in request.json:
        county = request.json['county']
        state = request.json['state']
        covid_predictor = Covid_Predictor(sql, county, state)
        result = covid_predictor.predict(days)

        return make_response(jsonify({'cases':result[0], 'deaths':result[1], 'days':days}), 200)

    else:
        return make_response(jsonify({}), 400)

#########################################################################################

def perform_model_training():
    #Function to perform training for each county
    global sql 
    result = sql.get_all_state_county()
    
    for res in result:
        
        #(sql, county, state, poly degree)
        print('-'*40)
        print(f"{res[0]}, {res[1]}")
        covid_predictor = Covid_Predictor(sql, res[0], res[1])
        covid_predictor.train_models()
        print('-'*40)
        
          
def get_latest_data():
    global sql 
    sql.update_db() #Latest data

def run_schedule():
    while True:
        global stop_thread
        schedule.run_pending()
        time.sleep(50)

        if stop_thread:
            break

if __name__=="__main__":
    
    #Perform training and daily data update every day once a day
    schedule.every().day.at("00:00").do(get_latest_data)
    schedule.every().day.at("00:30").do(perform_model_training)

    #Start a thread for running scheduling operations
    stop_thread = False
    th_schedule = threading.Thread(target = run_schedule)
    th_schedule.start()
    
    #Starts Flask application for development
    app.run(host='0.0.0.0', port=8000) 
    
    #Start application for production
    serve(app, host='0.0.0.0', port=8000)
  
    stop_thread = True
    th_schedule.join() #Stop Schedule operations


    