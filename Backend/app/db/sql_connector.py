#Adds higher lever package to path directory
from datetime import datetime
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
import sqlite3
from config import Config

class DbManagement(object):
    db = None
    cursor = None

    def __init__(self, db_engine:str = 'sqlite'):
        self.select_db_type(db_engine)
        self.connect_to_db()
        self.filename_us_cases = os.path.join(dirname, 'us_cases.csv')
        self.filename_us_deaths = os.path.join(dirname, 'us_deaths.csv')
        self.filename_global_cases = os.path.join(dirname, 'global_cases.csv')
        self.filename_global_deaths = os.path.join(dirname, 'global_deaths.csv')
  
        
    def select_db_type(self, db_engine:str):
        #To be able to quickly switch between mySQL, SQLite...
        #Changes Syntax in some of the queries to fit each
        self.db_engine = db_engine

        if db_engine == 'mysql':
            #MySQL
            self.AUTO_INCREMENT = 'AUTO_INCREMENT' #mysql requires this keyword for autoincrement
            self.sym = '%s' #mysql syntax for inserting values 

        elif db_engine == 'sqlite':
            #SQLITE
            self.AUTO_INCREMENT = '' #No need to add AUTOINCREMENT keyword for sqlite
            self.sym = '?' # sqlite syntax for inserting values 

        else:
            raise Exception('DB-ENGINE NOT AVAILABLE <==> AVAILABLE OPTIONS: mysql, sqlite')

    def connect_to_db(self):
        i = 0
        while True:
        #Retry until db is up and running
            try:
                db_name = Config.SQL_DB_NAME

                if self.db_engine == 'sqlite':
                    db_name = os.path.join(dirname, db_name + '.db')
                    DbManagement.db = sqlite3.connect(db_name)
                    DbManagement.cursor = DbManagement.db.cursor()

                elif self.db_engine == 'mysql':
                    DbManagement.db = mysql.connector.connect(host=Config.SQL_SERVER,user=Config.SQL_USER,password=Config.SQL_PASSWORD,database = db_name, port = Config.SQL_PORT, connection_timeout = 220 ,ssl_ca = Config.SQL_SSL_CA, ssl_verify_cert=False )
                    DbManagement.cursor = DbManagement.db.cursor()
                
                else:
                    raise Exception('DB-ENGINE NOT AVAILABLE <==> AVAILABLE OPTIONS: mysql, sqlite')

                break

            except Exception as e:
                i = i + 1
                if i > 2: #3 attemps
                    break
                print(e)
                print('Attempting to Connect')
                time.sleep(1) #Waiting before retrying

    def create_all_tables(self):
        
        df = pd.read_csv(self.filename_us_deaths)
        columns_to_drop = ['iso2', 'iso3', 'code3', 'Country_Region', 'Combined_Key']
        df = df.drop(columns=columns_to_drop)
     
        print('------------------------------ CREATING USERS TABLE -----------------------------')
        self.create_user_table()

        print('------------------------------ CREATING WORLD COUNTRIES TABLES -----------------------------')
        self.create_overall_world_table()
        self.create_and_seed_countries_table()
        self.create_world_tables()

        print('------------------------------ CREATING USA COUNTIES TABLES -----------------------------')
        county_columns = ['UID','FIPS','Province_State','Admin2', 'Population', 'Lat', 'Long_']
        self.create_state_level_tables_usa()
        self.create_and_seed_usa_counties_table('counties_usa', df.filter(county_columns))

        total = len(df)
        for count in range(total):
            state = df.iloc[count]['Province_State']
            county = df.iloc[count]['Admin2']

            
            table_name = None
            if str(county) == 'nan':
                #States with no counties - US Territories
                table_name = 'US_' + str(state)
            else:
                table_name = 'US_' + str(state) + '_' + str(county)
    
            self.create_each_location_table(table_name)
            print('\r ' + ' ' + str(count + 2) + ' of ' + str(total) + ' tables created', end='\r')


        print('-------------------------- DONE CREATING TABLES -----------------------------')

    def create_overall_world_table(self):
        table_name = 'world'
        while True:
            try:
                DbManagement.cursor.execute("DROP TABLE IF EXISTS " + table_name)
                sql = "CREATE TABLE `" + table_name + f"` ( id INTEGER PRIMARY KEY {self.AUTO_INCREMENT}, cases INT NULL, deaths INT NULL, time DATETIME NULL)"
                DbManagement.cursor.execute(sql)
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def create_sub_tables_for_countries(self, country, data):
        '''
        CREATES TABLES FOR COUNTRIES WITH PROVINCE/STATE LEVEL DATA (*NOT INCLUDING USA WHICH HAS COUNTY LEVEL DATA)
        '''
        table_name = country + '_' + 'prov_states' 
        while True:
            try:
                
                DbManagement.cursor.execute("DROP TABLE IF EXISTS `" + table_name + "`")
                sql = "CREATE TABLE `" + table_name + f"` ( id INTEGER PRIMARY KEY {self.AUTO_INCREMENT}, state_name VARCHAR(45) NOT NULL, latitude FLOAT NULL, longitude FLOAT NULL);"
                DbManagement.cursor.execute(sql)

                sql = f"INSERT INTO `"+ table_name + f"` (state_name, latitude, longitude) VALUES ({self.sym}, {self.sym}, {self.sym})"
                DbManagement.cursor.executemany(sql, data) #2D-List
                DbManagement.db.commit()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def create_state_level_tables_usa(self):

        df_cases = pd.read_csv(self.filename_us_cases)
       
        df_cases = df_cases.filter(['Province_State'])
        
        states = set(df_cases['Province_State']) #ELiminates duplicates
       
        for s in states:
             table_name = 'US_' + str(s)
             self.create_each_location_table(table_name)


    def create_and_seed_usa_counties_table(self, table_name, df_data):
        '''
        List of USA STATE counties with state and fips identifier
        '''
        df_data['FIPS'] = df_data['FIPS'].where(pd.notnull(df_data['FIPS']), 0) #Counties without fips
        
        #Replaces null values for states without counties(us territories)
        df_data['Admin2'] = df_data['Admin2'].where(pd.notnull(df_data['Admin2']), None) 
        
        county_info = df_data.values.tolist()
      
        while True:
            try:
             
                DbManagement.cursor.execute("DROP TABLE IF EXISTS " + table_name)
                sql = "CREATE TABLE "+ table_name + f"(id INTEGER PRIMARY KEY {self.AUTO_INCREMENT}, fips VARCHAR(45) NOT NULL,state VARCHAR(45) NULL,county VARCHAR(45) NULL, population INT NULL, latitude FLOAT NULL, longitude FLOAT NULL);"
                DbManagement.cursor.execute(sql)

                sql = f"INSERT INTO "+ table_name + f" (id, fips, state, county, population, latitude, longitude) VALUES ({self.sym}, {self.sym}, {self.sym}, {self.sym}, {self.sym}, {self.sym}, {self.sym})"
                DbManagement.cursor.executemany(sql, county_info) #2D-List
                DbManagement.db.commit()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def create_each_location_table(self, table_name):
        '''
        Creates each USA STATE county tables with unique identifier as table name
        Creates table for world data - COUNTRY LEVEL (*state/province for some - depending on data provided)

        '''
        while True:
            try:
                
                DbManagement.cursor.execute("DROP TABLE IF EXISTS `" + table_name + "`")
                sql = "CREATE TABLE `" + table_name + f"` ( id INTEGER PRIMARY KEY {self.AUTO_INCREMENT}, cases INT NULL, deaths INT NULL, time DATETIME NULL)"
                DbManagement.cursor.execute(sql)
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
    
    def create_world_tables(self):
        '''
        Creates table for world data - COUNTRY LEVEL (*state/province for some - depending on data provided)
        '''       
        df_cases = pd.read_csv(self.filename_global_cases)
        df_cases = df_cases.filter(['Province/State', 'Country/Region', 'Lat', 'Long'])

        total = len(df_cases['Country/Region'])
        countries_with_more_data = []
        for count, country in enumerate(df_cases['Country/Region']):
            
            records = df_cases[df_cases['Country/Region'] == country]
            
            if country in countries_with_more_data:
                continue

            #Verifies if country has state/province level data (creates additional tables)
            records = records.where(pd.notnull(records), None)
            num_records = len(records)
            if( num_records> 1):
                countries_with_more_data.append(country)
                self.create_each_location_table(country)
                
                data = [] #To create secondary tables
                for i in range(len(records)):
                    prov_state = records.iloc[i]['Province/State']

                    if prov_state is not None:
                        latitude = records.iloc[i]['Lat']
                        longitude = records.iloc[i]['Long']

                        data.append([prov_state, latitude, longitude])

                        table_name = str(country) + '_' + str(prov_state)
                        self.create_each_location_table(table_name)

                self.create_sub_tables_for_countries(country, data)

            else:
                self.create_each_location_table(country)

            print('\r' + ' ' + str(count + 2) + ' of ' + str(total) + ' Country Tables created', end='\r')


    def create_and_seed_countries_table(self):
        '''
        CREATES TABLE OF COUNTRIES
        '''
        table_name = 'countries'

        #hasmore indicates multiple records for country(state/province level data available)
        
        while True:
            try:
                DbManagement.cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                query = f'CREATE TABLE `{table_name}` ( id INTEGER PRIMARY KEY {self.AUTO_INCREMENT}, country_name VARCHAR(45) NOT NULL UNIQUE, population INT NULL, latitude FLOAT NULL, longitude FLOAT NULL, hasmore INT NULL); '
                DbManagement.cursor.execute(query)
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
        
        #FIELD hasmore  DETAILS
        #hasmore = 0 ---> Data for a single country(unified -- MOST ROWS/COUNTRIES) (eg. Angola, Portugal...)
        #hasmore = 1 ---> Country divided by states/provinces, country data not unified (eg. Australia, China)
        #hasmore = 2 ---> Country with territories, has main country, each territory data separated (eg. UK, France)

        df_cases = pd.read_csv(self.filename_global_cases)
        df_cases = df_cases.filter(['Province/State','Country/Region', 'Lat', 'Long'])

        total = len(df_cases)
        countries_with_more_data = []
        for count, country in enumerate(df_cases['Country/Region']):
            
            records = df_cases[df_cases['Country/Region'] == country]
            
            if country in countries_with_more_data:
                continue
            
            #Verifies if country has state/province/territories level data (creates additional tables)
            num_records = len(records)
            values = None
            if( num_records> 1):
                countries_with_more_data.append(country)

                values = (country, 0, records.iloc[0]['Lat'], records.iloc[0]['Long'], 1)
                for state in records['Province/State']:
                    if str(state) == 'nan':
                        values = (country, 0, records.iloc[0]['Lat'], records.iloc[0]['Long'], 2)
                        break

            else:
                values = (country, 0, records.iloc[0]['Lat'], records.iloc[0]['Long'], 0)
                
            query = 'INSERT INTO ' + table_name + f' (country_name,population, latitude, longitude, hasmore) VALUES ({self.sym}, {self.sym}, {self.sym}, {self.sym}, {self.sym});'
            DbManagement.cursor.execute(query, values) 
            DbManagement.db.commit()
            print('\r' + ' ' + str(count + 2) + ' of ' + str(total) + ' Countries Added to table', end='\r')
        
    def insert_overall_world_data(self, initial_setup=False):
        print('------------------------------ INSERTING OVERALL DAILY WORLD DATA -----------------------------')
     
        df_cases = pd.read_csv(self.filename_global_cases)
        df_deaths = pd.read_csv(self.filename_global_deaths)

        columns_to_drop = ['Lat', 'Long', 'Province/State','Country/Region']
        df_cases = df_cases.drop(columns=columns_to_drop)
        df_deaths = df_deaths.drop(columns=columns_to_drop)
        
        table_name = 'world'
        total_days = len(df_cases)

        dates = df_cases.columns.tolist()
        df_c = pd.DataFrame()
        df_d = pd.DataFrame()

        for count, date in enumerate(dates):
            daily_total_c =  df_cases[date].sum(skipna=True)
            daily_total_d =  df_deaths[date].sum(skipna=True)

            df_c[date] = pd.Series(daily_total_c)
            df_d[date] = pd.Series(daily_total_d)
            
        self.insert_new_data(df_c, df_d, table_name, 'overall_world', initial_setup)
        
    def insert_usa_state_level_data(self, initial_setup=False):
        print('------------------------------ INSERTING USA STATE LEVEL DATA -----------------------------')

        df_cases = pd.read_csv(self.filename_us_cases)
        df_deaths = pd.read_csv(self.filename_us_deaths)

        #Drop columns not needed
        columns_to_drop = ['Admin2', 'UID','iso2', 'iso3', 'code3', 'Country_Region', 'Combined_Key', 'FIPS', 'Lat', 'Long_']
     
        df_cases = df_cases.drop(columns=columns_to_drop)
        df_deaths = df_deaths.drop(columns=columns_to_drop + ['Population'])

        states = set(df_cases['Province_State'])
        total_states = len(states)
        for count, state in enumerate(states):
            df_tmp_c = df_cases[df_cases['Province_State'] == state]
            df_tmp_d = df_deaths[df_deaths['Province_State'] == state]

            df_tmp_c = df_tmp_c.drop(columns=['Province_State'])
            df_tmp_d = df_tmp_d.drop(columns=['Province_State'])
            
            table_name = 'US_' + str(state)
            dates = df_tmp_c.columns.tolist()
            df_c_overall = pd.DataFrame()
            df_d_overall = pd.DataFrame()

            for i, date in enumerate(dates):
                daily_total_c =  df_tmp_c[date].sum(skipna=True)
                daily_total_d =  df_tmp_d[date].sum(skipna=True)

                df_c_overall[date] = pd.Series(daily_total_c)
                df_d_overall[date] = pd.Series(daily_total_d)

       
            self.insert_new_data(df_c_overall, df_d_overall, table_name, 'state', initial_setup)
            print('\r' + ' ' + str(count + 2) + ' of ' + str(total_states) + ' tables updated', end='\r')

    def insert_county_level_data(self, initial_setup = False):
        print('------------------------------ INSERTING COUNTY LEVEL DATA -----------------------------')

        df_cases = pd.read_csv(self.filename_us_cases)
        df_deaths = pd.read_csv(self.filename_us_deaths)

       #Drop columns not needed
        columns_to_drop = ['iso2', 'iso3', 'code3', 'Country_Region', 'Combined_Key', 'FIPS', 'Lat', 'Long_']
     
        df_cases = df_cases.drop(columns=columns_to_drop)
        df_deaths = df_deaths.drop(columns=columns_to_drop)
 
        uid_list = df_cases['UID']
        total_counties = len(uid_list)
     
        #Update population in counties table
        for count, id in enumerate(uid_list):
            df_d = df_deaths[df_deaths['UID'] == id] #Filter by ID (row)
            
            population_count = df_d.iloc[0]['Population']
            state = df_d.iloc[0]['Province_State']
            county = df_d.iloc[0]['Admin2']

            query = f'UPDATE counties_usa SET population={population_count} WHERE state="{state}" AND county="{county}";'
          
            DbManagement.cursor.execute(query)
            DbManagement.db.commit()
       
        #Insert Daily Data Until last update
        df_deaths = df_deaths.drop(columns=['Population'])
        for count, id in enumerate(uid_list):
            state = df_deaths.iloc[count]['Province_State']
            county = df_deaths.iloc[count]['Admin2']

            table_name = None
            if str(county) == 'nan':
                table_name = 'US_' + str(state)
            else:
                table_name = 'US_' + str(state) + '_' + str(county)
          
            #Drop ID column (Only date columns remain after)
            df_c = df_cases[df_cases['UID'] == id] #Filter by ID (row)
            df_c = df_c.drop(columns=['UID','Province_State', 'Admin2'])

            df_d = df_deaths[df_deaths['UID'] == id] #Filter by ID (row)
            df_d = df_d.drop(columns=['UID', 'Province_State', 'Admin2'])

            self.insert_new_data(df_c, df_d, table_name, 'county', initial_setup)
            print('\r' + ' ' + str(count + 2) + ' of ' + str(total_counties) + ' tables updated', end='\r')
    
    def insert_new_data(self, df_c, df_d, table_name, calling_function_name, initial_setup):
        #Insert Daily Data Until last update
        col_index = 0
        #if initial setup => col_index will be = 0 which means insert all History data available
        #if not initial setup=> slices dataframe, keeps columns (dates) not in db yet (if col_index = 0, db is up to date)
        if not initial_setup:
            #Compare new data with the one in the database
            record_query = 'SELECT time FROM `' + table_name + '` ORDER BY id DESC LIMIT 1;'
            DbManagement.cursor.execute(record_query)
            last_db_record = DbManagement.cursor.fetchone()[0]
            
            try:
                last_db_record = pd.to_datetime(last_db_record)
            except Exception as e:
                print(e)
                raise Exception('POSSIBLY EMPTY TABLE - SET FUNCTION to initial_setup=True')
            
            while True:
                last_updated = df_c.iloc[:, col_index - 1:].columns
                last_updated = pd.to_datetime(last_updated[0])

                if last_db_record == last_updated:
                    break

                col_index = col_index - 1

                if col_index < -300:
                    #Peform initial set up
                    if calling_function_name == 'overall_world':
                        return self.insert_overall_world_data(initial_setup=True)

                    elif calling_function_name == 'world':
                        return self.insert_world_level_data(initial_setup=True)

                    elif calling_function_name == 'state':
                        return self.insert_usa_state_level_data(initial_setup=True)

                    elif calling_function_name == 'county':
                        return self.insert_county_level_data(initial_setup=True) 
                    else:
                        return

            if col_index == 0:
                #Table is up to date, check next table
                return

        #Cases
        df_c = df_c.iloc[:, col_index:]
        cases_list = []
        for col in df_c:
            date = None
            if self.db_engine == 'sqlite':
                date = str(col) #DATETIME field in sqlite seen as string/TEXT

            if self.db_engine == 'mysql':
                date = pd.to_datetime(col) #mysql DATETIME requires datetime object

            tmp = [int(df_c[col]), date] #[cases, date]
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

        query = "INSERT INTO `"+ table_name + f"` (cases, time, deaths) VALUES ({self.sym}, {self.sym}, {self.sym});"
        
        try:
            DbManagement.cursor.executemany(query, data)
            DbManagement.db.commit()

        except Exception as e:
            print(e)
            return


    def insert_world_level_data(self, initial_setup=False):
        print('------------------------------ INSERTING WORLD LEVEL DATA -----------------------------')
  
        df_cases = pd.read_csv(self.filename_global_cases)
        df_deaths = pd.read_csv(self.filename_global_deaths)

        columns_to_drop = ['Lat', 'Long']
        df_cases = df_cases.drop(columns=columns_to_drop)
        df_deaths = df_deaths.drop(columns=columns_to_drop)

        countries_with_more_data = []
        total = len(df_cases)
        #Insert Daily Data Until last update
        for count, country in enumerate(df_cases['Country/Region']):

            if country in countries_with_more_data:
                continue

            df_c = df_cases[df_cases['Country/Region'] == country]
            df_d = df_deaths[df_deaths['Country/Region'] == country]

            num_areas = len(df_c)
            if(num_areas > 1):
                countries_with_more_data.append(country)
                
                has_territories_data = False 
                for ps in df_c['Province/State']:
                    #Check to see if country has main country and territory data as well
                    if str(ps) == 'nan':
                        #(eg. Denmark, Netherlands)
                        has_territories_data = True
                        break

                if not has_territories_data:
                    #Countries that don't have territory data, but have main country split
                    #into state/provinces (eg. Canada, China, Australia)

                    #Sum all state/provinces data to create a unified table with record in addition to the ones already split
    
                    df_tmp_c = df_c.drop(columns=['Country/Region', 'Province/State'])
                    df_tmp_d = df_d.drop(columns=['Country/Region', 'Province/State'])

                    table_name = str(country)
                    dates = df_tmp_c.columns.tolist()
                    df_c_overall = pd.DataFrame()
                    df_d_overall = pd.DataFrame()

                    for count, date in enumerate(dates):
                        daily_total_c =  df_tmp_c[date].sum(skipna=True)
                        daily_total_d =  df_tmp_d[date].sum(skipna=True)

                        df_c_overall[date] = pd.Series(daily_total_c)
                        df_d_overall[date] = pd.Series(daily_total_d)
            
                    self.insert_new_data(df_c_overall, df_d_overall, table_name, 'world', initial_setup)


                for i in range(num_areas):
                    #Replace nan with None
                    df_c1 = df_c.where(pd.notnull(df_c), None)
                    df_d1 = df_d.where(pd.notnull(df_d), None)
                    
                    area = df_c1.iloc[i]['Province/State']

                    df_c1 = df_c1.drop(columns=['Country/Region', 'Province/State'])
                    df_d1 = df_d1.drop(columns=['Country/Region', 'Province/State'])
                    
                    df_c1 = df_c1.iloc[[i]]
                    df_d1 = df_d1.iloc[[i]]
                    
                    table_name = str(country)
                    if area is not None:
                        table_name = table_name + '_' + str(area)
                        
                    self.insert_new_data(df_c1, df_d1, table_name, 'world', initial_setup)
                           
            else:
                df_c1 = df_c.drop(columns=['Country/Region', 'Province/State'])
                df_d1 = df_d.drop(columns=['Country/Region', 'Province/State'])
                table_name = country
                self.insert_new_data(df_c1, df_d1, table_name, 'world', initial_setup)

            print('\r' + ' ' + str(count + 2) + ' of ' + str(total) + ' tables updated ', end='\r')


    def update_tables_data(self, initial_setup=False):
        print('------------------------------ INSERTING DATA -----------------------------')
        self.insert_world_level_data(initial_setup)
        self.insert_usa_state_level_data(initial_setup)
        self.insert_county_level_data(initial_setup)
        self.insert_overall_world_data(initial_setup)
        print('------------------------------ DONE INSERTING DATA -----------------------------')

    
    def create_user_table(self):
        while True:
            try:
                DbManagement.cursor.execute("DROP TABLE IF EXISTS " + "users")
                sql = "CREATE TABLE "+ "users " + f"(id INTEGER PRIMARY KEY {self.AUTO_INCREMENT},firstName VARCHAR(45) NOT NULL, lastName VARCHAR(45) NOT NULL,userName VARCHAR(45) NOT NULL UNIQUE, password VARCHAR(200) NOT NULL,country VARCHAR(45) NOT NULL, state VARCHAR(45) NULL, county VARCHAR(45) NULL);"
                DbManagement.cursor.execute(sql)
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
    
    def find_users(self, username=None):
        #Function to retrieve users from db (all and by id)
        if username is None:
            #Returns list of usernames and emails already registered
            query = "SELECT userName FROM users"

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
        query = "INSERT INTO `users` (`firstName`, `lastName`, `userName`, `password`,`country`, `state`, `county`) "
        values = f"VALUES ('{user['firstName']}', '{user['lastName']}',{user['userName']}', '{user['password']}','{user['country']}', '{user['state']}', '{user['county']}'); "
        
        while True:
            try:
                DbManagement.cursor.execute(query + values)
                DbManagement.db.commit()
                return True
            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def update_user(self, user:dict, change_password = False):
        #Function to updater user info
        query = f"UPDATE users SET firstName='{user['firstName']}', lastName= '{user['lastName']}', country='{user['country']}',"
        
        query_cont = None
        
        if change_password:
            query_cont = f" userName= '{user['userName']}', password='{user['password']}', county='{user['county']}', state ='{user['state']}' "
        else:
            query_cont = f" userName= '{user['userName']}', county='{user['county']}', state ='{user['state']}' "

        condition = f"WHERE id={user['id']};"
        full_query = query + query_cont + condition
        
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
        Function to get USA counties
        '''
        while True:
            try:
                query = f'SELECT county FROM counties_usa where state ="{state}";'
                DbManagement.cursor.execute(query)
                result  = DbManagement.cursor.fetchall()
                return result

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
    
    def get_all_state_county(self, states_only=False, counties_only = False):
        '''
        FOR USA
        '''
        query = "SELECT state, county, population, latitude, longitude FROM counties_usa;"
   
        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchall()
                
                states = []
                counties = []
                if states_only:
                    for state in result:
                        if state[0] not in states:
                            states.append(state[0])

                    return states     

                elif counties_only:
                     for county in result:
                        if county[1] not in counties:
                            counties.append(county[0])

                     return counties

                else:
                    return result

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def has_states(self, country):
        query = f'SELECT hasmore FROM countries WHERE country_name ="{country}";'
        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchone()
                
                if result is None:
                    return False
                
                elif result[0] == 0:
                    return False
                else:
                    return True

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

    def get_all_countries(self):
        query = "SELECT country_name, hasmore, population, latitude, longitude FROM countries;"
        result = None

        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchall()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

        return result

    def get_country_provs_states(self, country:str):

        if not self.has_states(country):
            return []

        table_name = country + '_' + 'prov_states'

        query = f"SELECT state_name, latitude, longitude FROM `{table_name}`;"
        result = []

        while True:
            try:
                DbManagement.cursor.execute(query)
                result = DbManagement.cursor.fetchall()
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()

        return result

    def get_lal_lon(self,country:str=None, state:str = None, county:str=None):
        '''
        Function to get latitude and longitude of locations
        '''
        query = None
        result = None

        if country is not  None:

            if state is not None:
                if country == 'US':
                    table_name = 'counties_usa'

                    if county is not None:
                        query = f"SELECT latitude, longitude FROM `{table_name}` WHERE state=`{state}` AND county=`{county}`"
                    
                    else:
                        query = f"SELECT latitude, longitude FROM `{table_name}` WHERE state=`{state}`"
                
                else:
                    table_name = country + '_prov_states'
                    query = f"SELECT latitude, longitude FROM `{table_name}` WHERE state_name=`{state}`"

            else:
                if country == 'US':
                    table_name = 'counties_usa'
                    query = f"SELECT latitude, longitude FROM `{table_name}`"

                else:
                    table_name = 'countries'
                    query = f"SELECT latitude, longitude FROM `{table_name}` WHERE country_name=`{country}`"

        else:
            table_name = 'countries'
            query = f"SELECT latitude, longitude FROM `{table_name}`"

        while True:
            try:
                DbManagement.cursor.execute(query)
                result  = DbManagement.cursor.fetchall()
                return result

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()


    def get_info(self, country:str=None, state:str = None, county:str=None,prediction:bool=False, days:int = None):
        '''
        Function to get information/data per county: 
        '''
        table_name = None
        if country is None:
            table_name = 'world'
        else:
            if state is None:
                table_name = str(country)
            else:
                if county is None:
                    table_name = str(country) + '_' + str(state)
                else:
                    table_name = str(country)+ '_' + str(state) + '_' + str(county)

        tmp_result = None
        query = None
        
        while True:
            try:
                if days is None:
                    query = f"SELECT * FROM `{table_name}`"
                  
                else:
                    query = f"SELECT * FROM `{table_name}` ORDER BY id DESC LIMIT {days}"
                    
                DbManagement.cursor.execute(query)
                tmp_result  = DbManagement.cursor.fetchall()
           
                break

            except DbException.DatabaseError as e:
                if e.args[0] == 2003:
                    self.connect_to_db()
        
        group_by_date = {}
        
        for res in tmp_result:
            
            date = res[-1]  
            if isinstance(date, datetime):
                #convert datetime to string
                date = date.strftime("%m/%d/%Y")
            
            #Date is key
            #May also help remove duplicates dates if there any - keeping the latest data
            group_by_date[date] = {"cases":res[1],"deaths":res[2]} 

        if prediction:
            result = []
            count = 1
            for values in group_by_date.items():
                data = [count, values[1]['cases'], values[1]['deaths']]
                result.append(data)
                count = count + 1
            return result

        return group_by_date
    
    def fetch_online_data(self):
        print('------------------------------ FETCHING DATA -----------------------------')
        #Data from John Hopkins Github repo
        url_us_cases = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
        url_us_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
        url_global_cases = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
        url_global_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
        
        try:
            r1 = requests.get(url_us_cases, allow_redirects=True)
            with open(self.filename_us_cases,'wb') as f1:
                f1.write(r1.content)
                f1.close()

            r2 = requests.get(url_us_deaths, allow_redirects=True)
            with open(self.filename_us_deaths,'wb') as f2:
                f2.write(r2.content)
                f2.close()
            
            r3 = requests.get(url_global_cases, allow_redirects=True)
            with open(self.filename_global_cases,'wb') as f3:
                f3.write(r3.content)
                f3.close()

            r4 = requests.get(url_global_deaths, allow_redirects=True)
            with open(self.filename_global_deaths,'wb') as f4:
                f4.write(r4.content)
                f4.close()

            print('------------------------------ DONE FETCHING DATA -----------------------------')
            return True

        except Exception as e:
            print('------------------------------ ERROR FETCHING DATA -----------------------------')
            print(e)
            return False
        

    def inital_set_up(self):
        '''
        RUN THIS FUNCTION TO SET UP THE DATABASE
        '''
        print('-------------------------- SETTING UP DATABASE -----------------------------')
        #Retrives data from Github repo
        try:
            self.fetch_online_data()
            #Creates all tables, drops existing one
            self.create_all_tables()
            #Inserts history data
            self.update_tables_data(initial_setup=True)
            print('-------------------------- DATABASE SETUP COMPLETE -----------------------------')
        except Exception as e:
            print(e)
            print('-------------------------- DATABASE SETUP FAILED -----------------------------')

        
    def update_db(self):
        '''
        RETRIVES LATEST DATA AND UPDATES THE DATABASE
        '''
        #Retrives data from Github repo
        self.fetch_online_data()
        #Updates db with latest records
        self.update_tables_data(initial_setup=False)
