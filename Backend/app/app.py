from dotenv import load_dotenv
load_dotenv()
import os
import threading
import time
from flask import Flask
from flask_cors import CORS
import schedule
import joblib
from waitress import serve
from routes.users_routes import users_bp
from routes.main_routes import main_bp
from dailyops import get_latest_data, update_globe_data, model_training

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
    schedule.every().day.at("00:10").do(update_globe_data)
    schedule.every().day.at("00:20").do(model_training)
    
    th_schedule = None

    try:
        #Start a thread for running scheduling operations
        th_schedule = threading.Thread(target = run_schedule)
        th_schedule.start()

        #Starts Flask application for development
        #app.run(host='0.0.0.0', port=8000) 
        
        #Start application for production
        serve(app, host='0.0.0.0', port=8000)

        #Stop Schedule operations
        
        stop_thread_exec()
        th_schedule.join() 
    
    except Exception as e:
        #Stop Schedule operations
        stop_thread_exec()
        th_schedule.join() 


    