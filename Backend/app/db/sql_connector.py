#Adds higher lever package to path directory
import sys, os
dirname = os.path.dirname(__file__)
app_package_dir = os.path.join(dirname, '..')
sys.path.append(dirname)
sys.path.append(app_package_dir)

import os
import time
import mysql.connector.errors as DbException
import mysql.connector
import pandas as pd
import requests
from config import Config

class DbManagement(object):
    db = None
    cursor = None

    def __init__(self):
        self.connect_to_db()
        

    def connect_to_db(self):
        i = 0
        while True:
            i = i + 1
        #Retry until db is up and running
            try:
                DbManagement.db = mysql.connector.connect(host=Config.sql_server,user=Config.sql_user,password=Config.sql_password,database = Config.sql_db, port = 3306, connection_timeout = 220 ,ssl_ca = Config.sql_ssl_ca, ssl_verify_cert=False )
                DbManagement.cursor = DbManagement.db.cursor()
                break

            except Exception as e:
                print('Attempting to Connect')
                time.sleep(1) #Waiting before retrying

            if i > 2: #3 attemps
                break


    def create_initial_tables(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'cases.csv')
        
        df = pd.read_csv(filename)
        columns_to_drop = ['iso2', 'iso3', 'code3', 'Country_Region', 'Combined_Key']
        df = df.drop(columns=columns_to_drop)
     
        county_columns = ['UID','FIPS','Province_State','Admin2', 'Lat', 'Long_']
  
        self.create_and_seed_list_of_counties_table('counties', df.filter(county_columns))
        self.create_user_table()

        print('------------------------------ CREATING COUNTY TABLES -----------------------------')
        total = len(df['UID'])
        for count, uid in enumerate(df['UID']):
            table_name = 'UID_' + str(uid)
            self.create_each_county_table(table_name)
            print('\r' + str(count + 2) + ' of ' + str(total) + ' tables created', end='\r')

        print('-------------------------- DONE CREATING COUNTY TABLES -----------------------------')

    
            
    def create_and_seed_list_of_counties_table(self, table_name, df_data):
        '''
        List of counties with state and fips identifier
        '''
        df_data['FIPS'] = df_data['FIPS'].where(pd.notnull(df_data['FIPS']), 0) #Counties without fips
        
        #Replaces null values for states without counties(us territories)
        df_data['Admin2'] = df_data['Admin2'].where(pd.notnull(df_data['Admin2']), 'All (* US Territory)') 
        
        county_info = df_data.values.tolist()

        while True:
            try:
             
                DbManagement.cursor.execute("DROP TABLE IF EXISTS " + table_name)
                sql = "CREATE TABLE "+ table_name +"(uid INT NOT NULL , fips VARCHAR(45) NOT NULL,state VARCHAR(45) NULL,county VARCHAR(45) NULL, latitude FLOAT NULL, longitude FLOAT NULL, PRIMARY KEY (uid));"
                DbManagement.cursor.execute(sql)

                sql = f"INSERT INTO "+ table_name +" (uid, fips, state, county, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s)"
                DbManagement.cursor.executemany(sql, county_info) #2D-List
                DbManagement.db.commit()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def create_each_county_table(self, table_name):
        '''
        Creates each county table with unique identifier as table name
        '''
        while True:
            try:
                
                DbManagement.cursor.execute("DROP TABLE IF EXISTS " + table_name)
                sql = "CREATE TABLE " + table_name + " ( id INT AUTO_INCREMENT PRIMARY KEY, cases INT NULL, deaths INT NULL, time DATETIME NULL)"
                DbManagement.cursor.execute(sql)
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
    
    def insert_new_data(self, initial_setup = False):
        print('------------------------------ INSERTING DATA -----------------------------')

        dirname = os.path.dirname(__file__)
        filename_cases = os.path.join(dirname, 'cases.csv')
        filename_deaths = os.path.join(dirname, 'deaths.csv')

        df_cases = pd.read_csv(filename_cases)
        df_deaths = pd.read_csv(filename_deaths)

       #Drop columns not needed
        columns_to_drop_c = ['iso2', 'iso3', 'code3', 'Country_Region', 'Combined_Key', 'FIPS','Province_State','Admin2', 'Lat', 'Long_']
        columns_to_drop_d = columns_to_drop_c + ['Population'] 
     
        df_cases = df_cases.drop(columns=columns_to_drop_c)
        df_deaths = df_deaths.drop(columns=columns_to_drop_d)
 
        uid_list = df_cases['UID']
        total_counties = len(uid_list)
 
        if initial_setup:
           
            for count, id in enumerate(uid_list):
                table_name = "UID_" + str(id)
                #Cases
                df_c = df_cases[df_cases['UID'] == id] #Filter by ID (row)
                df_c = df_c.drop(columns=['UID'])
                cases_list = []
                for col in df_c:
                    tmp = [int(df_c[col]), pd.to_datetime(col)] #[cases, date]
                    cases_list.append(tmp) 
                    
                #Deaths
                df_d = df_deaths[df_deaths['UID'] == id] #Filter by ID (row)
                df_d = df_d.drop(columns=['UID'])
                deaths_list = []
                for col in df_d:
                    tmp = [int(df_d[col])] #[deaths]
                    deaths_list.append(tmp) 
                    
                #Merge Cases and deaths data to be inserted
                data = []
                for i in range(len(cases_list)):
                    tmp = cases_list[i] + deaths_list[i] #[cases, date, deaths]
                    data.append(tmp) # [[cases, date, deaths], [cases, date, deaths] ...]

                query = "INSERT INTO "+ table_name + " (cases, time, deaths) VALUES (%s, %s, %s);"
                DbManagement.cursor.executemany(query, data)
                DbManagement.db.commit()
                print('\r' + str(count + 2) + ' of ' + str(total_counties) + ' tables updated', end='\r')
            
            return True
               
        else:
            for count, id in enumerate(uid_list):
                
                table_name = 'UID_' + str(id)

                #Drop ID column (Only date columns remain after)
                df_c = df_cases[df_cases['UID'] == id] #Filter by ID (row)
                df_c = df_c.drop(columns=['UID'])

                df_d = df_deaths[df_deaths['UID'] == id] #Filter by ID (row)
                df_d = df_d.drop(columns=['UID'])

                #Compare new data with the one in the database
                record_query = 'SELECT time FROM ' + table_name + ' ORDER BY id DESC LIMIT 1;'
                DbManagement.cursor.execute(record_query)
                last_db_record = DbManagement.cursor.fetchone()
                last_db_record = last_db_record[0].strftime("%Y-%m-%d %H:%M:%S")
                col_index = 0

                while True:
                    last_updated = df_c.iloc[:, col_index - 1:].columns
                    last_updated = str(pd.to_datetime(last_updated[0]))

                    if last_db_record == last_updated:
                        break

                    col_index = col_index - 1

                    if col_index < -300:
                        return self.insert_new_data(True) #Peform initial set up
                
                if col_index == 0:
                    #Table is up to date, check next table
                    print("Up-to-Date")
                    break

                #Slices dataframe, keeps columns (dates) not in db yet
                #Cases
                df_c = df_c.iloc[:, col_index:]
                cases_list = []
                for col in df_c:
                    tmp = [int(df_c[col]), pd.to_datetime(col)] #[cases, date]
                    cases_list.append(tmp) 

                #Deaths
                df_d = df_d.iloc[:, col_index:]
                deaths_list = []
                for col in df_d:
                    tmp = [int(df_d[col])] #[deaths]
                    deaths_list.append(tmp) 
                    
                #Merge Cases and deaths data to be inserted
                data = []
                for i in range(len(cases_list)):
                    tmp = cases_list[i] + deaths_list[i] #[cases, date, deaths]
                    data.append(tmp) # [[cases, date, deaths], [cases, date, deaths] ...]

                query = "INSERT INTO "+ table_name + " (cases, time, deaths) VALUES (%s, %s, %s);"
                DbManagement.cursor.executemany(query, data)
                DbManagement.db.commit()
                print('\r' + str(count + 2) + ' of ' + str(total_counties) + ' tables updated', end='\r')
        
        print('------------------------------ DONE INSERTING DATA -----------------------------')



    def fetch_online_data(self):
        print('------------------------------ FETCHING DATA -----------------------------')
        #Data from John Hopkins Github repo
        dirname = os.path.dirname(__file__)
        filename_cases = os.path.join(dirname, 'cases.csv')
        filename_deaths = os.path.join(dirname, 'deaths.csv')

        url_cases = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
        url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
        
        try:
            r1 = requests.get(url_cases, allow_redirects=True)
            with open(filename_cases,'wb') as f1:
                f1.write(r1.content)
                f1.close()

            r2 = requests.get(url_deaths, allow_redirects=True)
            with open(filename_deaths,'wb') as f2:
                f2.write(r2.content)
                f2.close()

            print('------------------------------ DONE FETCHING DATA -----------------------------')
            return True

        except:
            return False
        

    
    def create_user_table(self):
        while True:
            try:
                DbManagement.cursor.execute("DROP TABLE IF EXISTS " + "users")
                sql = "CREATE TABLE "+ "users " +"(id int NOT NULL AUTO_INCREMENT,firstName VARCHAR(45) NOT NULL, lastName VARCHAR(45) NOT NULL,email VARCHAR(45) NOT NULL,userName VARCHAR(45) NOT NULL, password VARCHAR(200) NOT NULL,county VARCHAR(45) NOT NULL, state VARCHAR(45) NOT NULL,PRIMARY KEY (id), UNIQUE(userName), UNIQUE(email));"
                DbManagement.cursor.execute(sql)
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
    
    def find_users(self, username=None):
        #Function to retrieve users from db (all and by id)
        if username is None:
            #Returns list of usernames and emails already registered
            query = "SELECT email, userName FROM users"

            while True:
                try:
                    DbManagement.cursor.execute(query)
                    result = DbManagement.cursor.fetchall()
                    return result

                except DbException.DatabaseError as e:
                    if e.args[0] == 2003:
                        self.connect_to_db()
        
        else:
            query = "SELECT * FROM users WHERE userName='" + str(username) + "'"
            
            while True:
                try:
                    DbManagement.cursor.execute(query)
                    result = DbManagement.cursor.fetchone()
                    return result
                
                except DbException.DatabaseError as e:
                    if e.args[0] == 2003:
                        self.connect_to_db()
    
    def add_user(self, user:dict):
        #Function to add new user
        query = "INSERT INTO `users` (`firstName`, `lastName`, `email`, `userName`, `password`, `county`, `state`) "
        values = f"VALUES ('{user['firstName']}', '{user['lastName']}', '{user['email']}', '{user['userName']}', '{user['password']}', '{user['county']}', '{user['state']}'); "
        
        while True:
            try:
                DbManagement.cursor.execute(query + values)
                DbManagement.db.commit()
                return True
            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def update_user(self, user:dict):
        #Function to updater user info
        query = f"UPDATE users SET firstName='{user['firstName']}', lastName= '{user['lastName']}', email='{user['email']}',"
        queryCont = f" userName= '{user['userName']}', password='{user['password']}', county='{user['county']}', state ='{user['state']}' "
        condition = f"WHERE id={user['id']};"

        full_query = query + queryCont + condition
        
        while True:
            try:
                DbManagement.cursor.execute(full_query)
                DbManagement.db.commit()
                return True

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
                else:
                    return False

    def get_counties(self, state):
        '''
        Function to get counties
        '''
        while True:
            try:
                query = f'SELECT county FROM counties where state ="{state}";'
                DbManagement.cursor.execute(query)
                result  = DbManagement.cursor.fetchall()
                return result

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
        
    def get_uid(self,state,county):
        '''
        Unique county identifier
        '''
        query = 'SELECT uid FROM counties WHERE state="' + str(state) +'" AND county="' + str(county) + '";'
        
        result = None
        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchall()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

        if len(result) == 0:
            return None
        else:
            return result[0][0]

    def get_lat_lon(self, county, state):
        query = 'SELECT latitude, longitude FROM counties WHERE state="' + str(state) +'" AND county="' + str(county) + '";'

        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchone()

                return result

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()


    def get_all_state_county(self):
        query = "SELECT county, state FROM counties;"
        result = None

        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchall()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

        if len(result) == 0:
            return None
        else:
            return result

    def get_county_info(self,uid,days = None):
        '''
        Function to get info per county: UID = UID_84008031
        '''
        table_name = 'UID_' + str(uid)
        result = None
        while True:
            try:
                if days is None:
                    DbManagement.cursor.execute("SELECT * FROM " + table_name)
                else:
                    DbManagement.cursor.execute("SELECT * FROM " + table_name + " WHERE time>CURRENT_DATE - INTERVAL " + str(days + 1) + " DAY")
                result  = DbManagement.cursor.fetchall()
                
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
        
        refined_result = {}
        for res in result:
            #Date is key of refined result
            refined_result[res[-1].strftime("%m/%d/%Y")] = {"cases":res[1],"deaths":res[2]}
        
        return refined_result
    
    def get_all_data_per_county(self, county:str, state:str):
        uid = self.get_uid(state, county)
        table_name = 'UID_' + str(uid)
        query = "SELECT * FROM " + table_name +";"
        
        tmp = None
        while True:
            try:
                DbManagement.cursor.execute(query)
                tmp = DbManagement.cursor.fetchall()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
        
        result = []
        remove_duplicate_dates = {}
        
        for res in tmp:
            remove_duplicate_dates[res[-1].strftime("%m/%d/%Y")] = {'id':res[0], 'cases': res[1], 'deaths': res[2]}
            
        count = 1
        for date, values in remove_duplicate_dates.items():
            data = [count, values['cases'], values['deaths']]
            result.append(data)
            count = count + 1
        
        return result
    
    def inital_set_up(self):
        '''
        RUN THIS FUNCTION TO SET UP THE DATABASE
        '''
        print('-------------------------- SETTING UP DATABASE -----------------------------')
        #Retrives data from Github repo
        self.fetch_online_data()
        #Creates all tables, drops existing one
        self.create_initial_tables()
        #Inserts history data
        self.insert_new_data(initial_setup=True)
        print('-------------------------- DATABASE SETUP COMPLETE -----------------------------')

        
    def update_db(self):
        #Retrives data from Github repo
        self.fetch_online_data()
        #Updates db with latest records
        self.insert_new_data()
        