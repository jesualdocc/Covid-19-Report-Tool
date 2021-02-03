# Covid Report App

Link to the running app: https://jesualdocc.github.io/covid-app-test/

### Threejs Animation
![Home (Globe)](https://user-images.githubusercontent.com/46726672/106687404-48b9e780-6589-11eb-87fd-0d03337d4504.jpg)

### Dashboard
![Dashboard](https://user-images.githubusercontent.com/46726672/106687496-72730e80-6589-11eb-9265-ccf1c2ebf2f2.jpg)

### Reports
![Reports](https://user-images.githubusercontent.com/46726672/106687508-7868ef80-6589-11eb-8944-3b7887711fa3.jpg)

## How to run app locally

1) Go Backend/app
* Run “pip install -r requirements.txt” to install all dependencies
* Rename configEx.py to config.py, and fill the empty fields (DB info, JWT secret key,and Twitter API Keys if needed)
2) Go Backend/app/db
* Open sql_conector.py
* Instantiate a DbManagement instance (*choose between the default sqlite, and MySQL)
* Run function initial_set_up() to setup all tables and data in the db
* Delete instance
3) Go Backend/app
* Run app.py to start server
4) Go to Frontend/covidapp/src/app
* Run “npm install” to install all dependencies
* Run “ng serve” to start client
* Go to browser and navigate to URL
