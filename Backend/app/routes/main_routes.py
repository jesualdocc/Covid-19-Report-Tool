#Adds higher lever package to path directory
import sys, os
dirname = os.path.dirname(__file__)
app_package_dir = os.path.join(dirname, '..')
sys.path.append(dirname)
sys.path.append(app_package_dir)

from flask import Blueprint
from flask.helpers import make_response
from flask import request, jsonify
from flask_csp.csp import csp_header
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from helper_functions import convert_email_username_tuple_to_dict
from jwt_auth import token_required
from predictions_and_analysis.twitter_textblob import Twitter_Textblob
from db.sql_connector import SQLConnector
from predictions_and_analysis.predictor import Covid_Predictor

main = Blueprint('main', __name__)
sql = SQLConnector()

#Configuring Blueprint/Routes
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

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


###################################################################################

#Retrieves list of email and usernames already registered
@main.route('/listof', methods=['GET'])
@limiter.limit("5 per minute")
@csp_header(config_csp)
def list_of_email_username():
    global sql 

    users = sql.find_users()
    users_dict = convert_email_username_tuple_to_dict(users)
    return make_response(jsonify({'users':users_dict}), 200)

##############################################################################################

#Returns actual county data by days 
@main.route('/data',methods = ['POST'])
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
@main.route('/counties', methods=['POST'])
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
    


###########################################################################################    
#
@main.route('/twitter', methods = ['POST'])
@token_required
@csp_header(config_csp)
def twitter_feed():
    global sql 
    tw = Twitter_Textblob()

    if 'county' in request.json and 'state' in request.json:
        county = request.json['county']
        state = request.json['state']

        #Todo - get geolocation from google maps data to filter tweets
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
@main.route('/predictions', methods = ['POST'])
@token_required
@csp_header(config_csp)
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
