import threading
import time
from flask import Flask
from flask_cors import CORS
import schedule
from waitress import serve
from predictions_and_analysis.predictor import Covid_Predictor
from db.sql_connector import SQLConnector
from routes.users_routes import users
from routes.main_routes import main

#Application Configuration
app = Flask(__name__)

cors_config = {
    "origins": "*",
}

CORS(app, resources={r"/*": cors_config})

#Adding routes
app.register_blueprint(users)
app.register_blueprint(main)

#Configuring response headers
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


#Placeholder entry point route
@app.route('/')
def indexpage():
    return 'Server Running @JCC 2021 01/09 - vf'

#Establisk conection to db 

sql = SQLConnector()

#############################################

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
        break
        
################################################         
def get_latest_data():
    #Get daily update
    global sql 
    sql.update_db() #Latest data

#############################
stop_thread = False
def run_schedule():
    #Function to be executed by thread for scheduling tasks
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
    
    th_schedule = threading.Thread(target = run_schedule)
    th_schedule.start()
    
    #Starts Flask application for development
    #app.run(host='0.0.0.0', port=8000) 
    
    #Start application for production
    serve(app, host='0.0.0.0', port=8000)
  
    stop_thread = True
    th_schedule.join() #Stop Schedule operations


    