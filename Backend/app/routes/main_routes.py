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
        "country": {"type": "string"},
        "state": {"type": "string"},
        "county": {"type": "string"},
        "days": {"type": "integer"}
    }
}

###################################################################################

#Retrieves list of email and usernames already registered
@main_bp.route('/listof', methods=['GET'])
@limiter.limit("5 per minute")
@csp_header(config_csp)
def list_of_username():
    #sqlite throws thread error if sql definedand used as global for all routes/methods
    #would have worked fine for mysql
    sql = DbManagement()

    i = 0
    while True:
        i = i + 1
        try:
            users = sql.find_users()
            users_dict = {}
            usernames = []
            for i in range(len(users)):

                usernames.append(users[i][1])

            users_dict['userName'] = usernames

            return make_response(jsonify({'users': users_dict}), 200)

        except:
            sql.connect_to_db()
            if i > 5:
                return make_response(jsonify({'request': {}}), 500)

##############################################################################################

#Returns actual county data by days


@main_bp.route('/data', methods=['POST'])
@csp_header(config_csp)
def data():
    sql = DbManagement()
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    country = None
    state = None
    county = None

    
    if 'country' in result:
        country = result['country']

        if 'state' in result:
            state = result['state']
            
            if 'county' in result:
                county = result['county']
            
    else:
        return make_response(jsonify({}), 400)

    data = None
    i = 0
    while True:
        i = i + 1
        try:
            if 'days' in result:
                days = result['days']

                data = sql.get_info(country=country, state=state, county=county, days=days)  
                
            else:
                data = sql.get_info(country=country, state=state, county=county)

            return make_response(jsonify({'data': data}), 200)

        except Exception as e:
            sql.connect_to_db()
            if i > 5:
                return make_response(jsonify({}), 500)

            
#################################################################################

#Returns list of counties

@main_bp.route('/counties', methods=['POST'])
@csp_header(config_csp)
def get_counties():
    sql = DbManagement()
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    if 'state' in result:
        i = 0
        while True:
            i = i + 1
            try:
                counties = sql.get_counties(result['state'])

                if counties is not None:
                    return make_response(jsonify({'data': counties}), 200)

                else:
                    return make_response(jsonify({}), 400)

            except Exception as e:
                sql.connect_to_db()
                if i > 5:
                    return make_response(jsonify({}), 500)



    else:
        return make_response(jsonify({}), 400)

###########################################################################################
#Returns list of states/provinces
@main_bp.route('/states', methods=['POST'])
@csp_header(config_csp)
def get_states():
    sql = DbManagement()
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
       
        return make_response(jsonify({}), 400)

    states = None
    if 'country' in result:
        i = 0
        while True:
            i = i + 1
            try:
                if result['country'] == 'US':
                    states = sql.get_all_state_county(states_only=True)

                else:
                    states = []
                    tmp_states = sql.get_country_provs_states(result['country'])
                    
                    if len(tmp_states) > 0:
                        for state in tmp_states:
                            states.append(state[0])

                return make_response(jsonify({'data': states}), 200)

            except Exception as e:
                sql.connect_to_db()
                if i > 5:
                    return make_response(jsonify({}), 500)
                    
    return make_response(jsonify({'request':result}), 400)
   

###########################################################################################

@main_bp.route('/countries', methods=['GET'])
@csp_header(config_csp)
def get_countries():
    sql = DbManagement()
    i = 0
    while True:
        i = i + 1
        try:
            countries = sql.get_all_countries()

            return make_response(jsonify({'data': countries}), 200)

        except Exception as e:
            sql.connect_to_db()
            if i > 5:
                return make_response(jsonify({}), 500)

###########################################################################################
#
@main_bp.route('/twitter', methods=['POST'])
@token_required
@csp_header(config_csp)
def twitter_feed():
    tw = Twitter_Textblob()
    result = request.json

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    country = None
    state = None
    county = None
    geocode = []

    if 'country' in result:
        country = result['country']

        if 'state' in result:
            state = result['state']
            
            if 'county' in result:
                county = result['county']

        #Not many tweets are geocoded
        ####sql.get_lat_lon(country=country, state=state, county=county)
                #geocode format [lat, long, distance/radius]
                #37.469887, -122.0446721, 100mi
        
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
    sql = DbManagement()
    result = request.json
    days = 20

    try:
        #Validate data
        validate(result, data_schema)
    except jsonschema.ValidationError:
        return make_response(jsonify({}), 400)

    country = None
    state = None
    county = None

    if 'country' in result:
        country = result['country']

        if 'state' in result:
            state = result['state']
            
            if 'county' in result:
                county = result['county']

    else:
        return make_response(jsonify({}), 400)
    
    i = 0
    while True:
        i = i + 1
        try:
            covid_predictor = Covid_Predictor(sql, country=country, state =state, county=county)
            predictions = covid_predictor.predict(days)

            return make_response(jsonify({'cases': predictions[0], 'deaths': predictions[1], 'days': days}), 200)
        except Exception as e:
            sql.connect_to_db()
            if i > 5:
                return make_response(jsonify({}), 500)
    
        

###################################################################################
#Returns data for globe

@main_bp.route('/globedata', methods=['GET'])
@limiter.limit("5 per minute")
@csp_header(config_csp)
def get_globe_data():
    
    try:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'GlobeData')
        data = joblib.load(filename)
        
        return make_response(jsonify({'data': data}), 200)

    except:
        return make_response(jsonify({}), 500)
