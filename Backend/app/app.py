import os
import threading
import time
from flask import Flask
from flask_cors import CORS
import schedule
import joblib
from waitress import serve
from predictions_and_analysis.predictor import Covid_Predictor
from db.sql_connector import DbManagement
from routes.users_routes import users_bp
from routes.main_routes import main_bp

#Application Configuration
app = Flask(__name__)

cors_config = {
    "origins": "*",
}

CORS(app, resources={r"/*": cors_config})

#Adding routes
app.register_blueprint(users_bp)
app.register_blueprint(main_bp)

#Configuring response headers (Not Strict)
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


#Placeholder entry point route
@app.route('/')
def indexpage():
    return 'Server Running @JCC 2021 01/25'

#Establisk conection to db 

sql = DbManagement()

#############################################

def model_training():
    #Function to perform training for each county
    global sql 
    result = sql.get_all_state_county()
    
    for res in result:
        #(sql, county, state)
        covid_predictor = Covid_Predictor(sql, res[0], res[1])
        covid_predictor.train_models()
        
       
        
################################################         
def get_latest_data():
    #Get daily update
    global sql 
    sql.update_db() #Latest data
####################################################
def update_globe_data():
    #Cache data for globe (Threejs)
    print('-------------------------- UPDADING GLOBE DATA -----------------------------')

    global sql
    try:
        locations = sql.get_all_state_county()  # county, state

        data = []
        for res in locations:
            #res => res[0] - county, res[1] - state
            coordinates = sql.get_lat_lon(county=res[0], state=res[1])
            uid = sql.get_uid(county = res[0], state = res[1])
            tmp = sql.get_county_info(uid, 1)

            date = list(tmp.keys())[0]

            values = list(tmp.values())[0] #cases, deaths
            values['county'] = res[0]
            values['state']  = res[1]
            values['latitude'] = coordinates[0]
            values['longitude'] = coordinates[1]
            values['last_update'] = date
            data.append(values)
 
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'routes/GlobeData')
        joblib.dump(data, filename) #Save data for regular use (avoid multiple db calls)
        print('-------------------------- DONE UPDADING GLOBE DATA -----------------------------')


    except Exception as e:
        print(e)
        return

#############################
stop_thread = False
def run_schedule():
    #Function to be executed by thread for scheduling tasks
    while True:
        global stop_thread
        schedule.run_pending()
        time.sleep(30)

        if stop_thread:
            break

def stop_thread_exec():
    global stop_thread
    stop_thread = True
    

if __name__=="__main__":
    #Perform daily data update and training every day once a day
    schedule.every().day.at("00:00").do(get_latest_data)
    schedule.every().day.at("00:30").do(update_globe_data)
    schedule.every().day.at("00:45").do(model_training)
    
    th_schedule = None

    try:
        #Start a thread for running scheduling operations
        th_schedule = threading.Thread(target = run_schedule)
        th_schedule.start()

        #Starts Flask application for development
        app.run(host='0.0.0.0', port=8000) 
        
        #Start application for production
        #serve(app, host='0.0.0.0', port=8000)
    
    except Exception as e:
        #Stop Schedule operations
        stop_thread_exec()
        th_schedule.join() 


    