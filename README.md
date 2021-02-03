# Covid Report App

Link to the running app: https://github.com/jesualdocc/covid-app-test

![Home (Globe)](https://user-images.githubusercontent.com/46726672/106687404-48b9e780-6589-11eb-87fd-0d03337d4504.jpg)

![Dashboard](https://user-images.githubusercontent.com/46726672/106687496-72730e80-6589-11eb-9265-ccf1c2ebf2f2.jpg)

![Reports](https://user-images.githubusercontent.com/46726672/106687508-7868ef80-6589-11eb-8944-3b7887711fa3.jpg)

##How to run app locally

1) Go Backend/app
a. Run “pip install -r requirements.txt” to install all dependencies
2) Go Backend/app/db
a. Open sql_conector.py
b. Instantiate a DbManagement instance (*choose between the default sqlite, and MySQL)
c. Run function initial_set_up() to setup all tables and data in the db
d. Delete instance
3) Go Backend/app
a. Run app.py to start server
4) Go to Frontend/covidapp/src/app
a. Run “npm install” to install all dependencies
b. Run “ng serve” to start client
c. Go to browser and navigate to URL
