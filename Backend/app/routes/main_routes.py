#Adds higher lever package to path directory

import sys
import os
dirname = os.path.dirname(__file__)
app_package_dir = os.path.join(dirname, '..')
sys.path.append(dirname)
sys.path.append(app_package_dir)

from predictions_and_analysis.predictor import Covid_Predictor
from db.sql_connector import DbManagement
from predictions_and_analysis.twitter_textblob import Twitter_Textblob
from jwt_auth import token_required
from jsonschema import validate
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_csp.csp import csp_header
from flask import request, jsonify
from flask.helpers import make_response
from flask import Blueprint
import jsonschema
import joblib

main_bp = Blueprint('main_bp', __name__)
sql = DbManagement()

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

#Set up schema for validation
data_schema = {
    "type": "object",
    "properties": {
        "county": {"type": "string"},
        "state": {"type": "string"},
        "days": {"type": "integer"}
    }
}


###################################################################################

#Retrieves list of email and usernames already registered
@main_bp.route('/listof', methods=['GET'])
@limiter.limit("5 per minute")
@csp_header(config_csp)
def list_of_email_username():
    global sql

    try:
        users = sql.find_users()
        users_dict = {}
        emails = []
        usernames = []
        for i in range(len(users)):

            emails.append(users[i][0])
            usernames.append(users[i][1])

        users_dict['email'] = emails
        users_dict['userName'] = usernames

        return make_response(jsonify({'users': users_dict}), 200)

    except:
        return make_response(jsonify({'request': {}}), 500)

##############################################################################################

#Returns actual county data by days


@main_bp.route('/data', methods=['POST'])
@csp_header(config_csp)
def data():
    global sql
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    if 'county' in result and 'state' in result:

        county = result['county']
        state = result['state']
        data = None

        if 'days' in result:
            days = result['days']

            data = sql.get_county_info(county=county, state=state, days=days)

        else:
            data = sql.get_county_info(county=county, state=state)

        return make_response(jsonify({'data': data}), 200)

    else:
        return make_response(jsonify({}), 400)

#################################################################################

#Returns list of counties


@main_bp.route('/counties', methods=['POST'])
@csp_header(config_csp)
def get_counties():
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    if 'state' in result:
        counties = sql.get_counties(result['state'])

        if counties is not None:
            return make_response(jsonify({'data': counties}), 200)

        else:
            return make_response(jsonify({}), 400)

    else:
        return make_response(jsonify({}), 400)


###########################################################################################
#
@main_bp.route('/twitter', methods=['POST'])
@token_required
@csp_header(config_csp)
def twitter_feed():
    global sql
    tw = Twitter_Textblob()
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    if 'county' in result and 'state' in result:
        county = result['county']
        state = result['state']

        #Todo - get geolocation from google maps data to filter tweets
        #Not many tweets geocoded
        #g = "37.469887, -122.0446721, 100mi"
        geocode = []
        #Hashtags, geocode, count
        tweets = tw.get_tweets( ['coronavirus', 'covid', 'covid19'], geocode, 20)

        return make_response(jsonify({'tweets': tweets}), 200)

    else:
        return make_response(jsonify({}), 400)


#################################################################################################
#Returns predictions of cases/deaths by county
@main_bp.route('/predictions', methods=['POST'])
@token_required
@csp_header(config_csp)
def get_predictions():
    global sql
    result = request.json
    days = 20

    if 'county' in result and 'state' in result:
        county = result['county']
        state = result['state']
        covid_predictor = Covid_Predictor(sql, county, state)
        predictions = covid_predictor.predict(days)

        return make_response(jsonify({'cases': predictions[0], 'deaths': predictions[1], 'days': days}), 200)

    else:
        return make_response(jsonify({}), 400)

###################################################################################
#Returns data for globe


@main_bp.route('/globedata', methods=['GET'])
@limiter.limit("5 per minute")
@csp_header(config_csp)
def get_globe_data():
    global sql

    try:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'GlobeData')
        data = joblib.load(filename)
        
        return make_response(jsonify({'data': data}), 200)

    except:
        return make_response(jsonify({}), 500)
