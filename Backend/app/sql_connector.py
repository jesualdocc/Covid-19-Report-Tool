import mysql.connector
import pandas as pd
import requests
import filecmp
import logging
import os
import time
from config import Config

class SQLConnector(object):
    """docstring fo SQLConnector."""

    #Class variable for sharing across all SQLCOnnector instances
    db = mysql.connector.connect(host=Config.sql_server,user=Config.sql_user,password=Config.sql_password,database = Config.sql_db, port = 3306, connection_timeout = 220 ,ssl_ca = Config.sql_ssl_ca, ssl_verify_cert=True )
    cursor = db.cursor()

    def __init__(self):
        self.counter = 0 #Insert Data (Num of days inserted (history)

    def reconnect_to_db(self):
        i = 0
        while True:
            i = i + 1
        #Retry until db is up and running
            try:
                SQLConnector.db = mysql.connector.connect(host=Config.sql_server,user=Config.sql_user,password=Config.sql_password,database = Config.sql_db, port = 3306, connection_timeout = 220 ,ssl_ca = Config.sql_ssl_ca, ssl_verify_cert=True )
                SQLConnector.cursor = SQLConnector.db.cursor()
                #print('Reconnecting to DB')
                break

            except Exception as e:
                print('Attempting to Connect')
                print(e)
                time.sleep(1) #Waiting before retrying

                if i > 2: #3 attemps
                    break
    
  
    def set_initial_data(self):
        '''
            Function to setup the schema for the database
        '''
        print('-'*40); print('SETTING UP TABLES');print('-'*40)

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'current_data.csv')

        df = pd.read_csv(filename)
        df = df.dropna(subset=['fips'])
        df["fips"] = df.fips.apply(lambda x: "fips_" + str(int(x)))
        county_info = list(zip(df.fips,df.state,df.county))
        stat_columns = [(column,"INT") for column in df.columns if column not in ['fips','county','state','date']]
        self.create_county_table("counties",county_info)
        self.create_user_table()
        stat_columns.append(('time','DATETIME'))
        
        length = len(df["fips"]) + 2
        for i, fips in enumerate(df["fips"]):
            self.create_stat_table(fips,stat_columns,force_drop = True)
            print('\r' + str(i + 2) + ' of ' + str(length) + ' tables created', end='\r')

        print("")
        print('-'*40); print('DONE SETTING UP TABLES');print('-'*40)

    def create_user_table(self):
        while True:
            try:
                SQLConnector.cursor.execute("DROP TABLE IF EXISTS " + "users")
                sql = "CREATE TABLE "+ "users " +"(id int NOT NULL AUTO_INCREMENT,firstName VARCHAR(45) NOT NULL, lastName VARCHAR(45) NOT NULL,email VARCHAR(45) NOT NULL,userName VARCHAR(45) NOT NULL, password VARCHAR(200) NOT NULL,county VARCHAR(45) NOT NULL, state VARCHAR(45) NOT NULL,PRIMARY KEY (id), UNIQUE(userName), UNIQUE(email));"
                SQLConnector.cursor.execute(sql)
                break

            except Exception as e:
                self.reconnect_to_db()
            
    def create_county_table(self,table_name,data,force_drop = True):
        '''
        List of counties with state and fips identifier
        '''
        while True:
            try:
                county_info = data 
                SQLConnector.cursor.execute("DROP TABLE IF EXISTS " + table_name)
                sql = "CREATE TABLE "+ table_name +"( fips VARCHAR(45) NOT NULL,state VARCHAR(45) NULL,county VARCHAR(45) NULL, latitude FLOAT NULL, longitude FLOAT NULL, PRIMARY KEY (fips));"
                SQLConnector.cursor.execute(sql)

                sql = "INSERT INTO "+ table_name +" (fips, state, county) VALUES (%s, %s, %s)"
               
                SQLConnector.cursor.executemany(sql, county_info)
                SQLConnector.db.commit()
                break

            except Exception as e:
                self.reconnect_to_db()

    
    def set_lat_lon(self):
        '''
        Todo - 
        '''
        counties = self.get_all_state_county()

        for c in counties:
            location = c[0] + ', ' + c[1]
            url = 'https://maps.googleapis.com/maps/api/geocode/json'
            params = {'sensor': 'false', 'address': location, 'key':Config.GOOGLE_MAPS_API_KEY}
            r = requests.get(url, params=params)
            results = r.json()['results']
            location = results[0]['geometry']['location']
            lat = location['lat'] 
            lon = location['lng']

            query = f"INSERT INTO counties (latitude, longitude) VALUES ({lat}, {lon}) "
            condition = f"where (county='{c[0]}' and state='{c[1]}') ;"
     
        
  
    def create_stat_table(self,table_name,columns,force_drop = False):
        '''
        Creates each county table with uniques fips identifier as table name
        '''
        while True:
            try:
                if force_drop:
                    SQLConnector.cursor.execute("DROP TABLE IF EXISTS " + table_name)
                sql = "CREATE TABLE IF NOT EXISTS " + table_name + " ( id INT AUTO_INCREMENT PRIMARY KEY"
                start = True
                for column_name,column_type in columns:
                    sql = sql + "," + column_name + " " + column_type

                sql = sql + ")"

                SQLConnector.cursor.execute(sql)
                break

            except Exception as e:
                self.reconnect_to_db()
    
    def insert_new_data(self):
        '''
        Inserts data into county tables
        '''
        self.counter = self.counter + 1 #Keeping track of number of records inserted
        print(f"**** INSERTING DATA - Count = {self.counter} ****")
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'current_data.csv')

        df = pd.read_csv(filename)
        df = df.dropna(subset=['fips'])
        df["fips"] = df.fips.apply(lambda x: "fips_" + str(int(x)))
        df["date"] = df.date.apply(lambda x: "\'" + x +"\'")
        tables = df["fips"]
        stat_columns = [column for column in df.columns if column not in ['fips','county','state']]
        stat_df = stat_columns + ["fips"]
        stat_df = df[stat_df]
        stat_str = ",".join(stat_columns)
        stat_str = "(" + stat_str + ")"
        stat_str = stat_str.replace('date','time')
        
        length = len(df["fips"])
        for index, row in df.iterrows():
            values = row[stat_columns].values.tolist()
            values = [str(x) for x in values]
            value_str = ",".join(values)
            value_str = value_str.replace("nan","0")

            print('\r' + str(index) + ' of ' + str(length) + ' county tables updated', end='\r')

            sql = "INSERT INTO "+ row["fips"] + " " + stat_str + " VALUES (" + value_str + ")"

            while True:
                try:
                    SQLConnector.cursor.execute(sql)
                    SQLConnector.db.commit() 
                    break
                except mysql.connector.errors.ProgrammingError as e:
                    print (e)
                    break
                except Exception as e:
                    print(e)
                    self.reconnect_to_db()
                    
        print("")

    def get_tables(self):
        while True:
            try:
                SQLConnector.cursor.execute("SHOW TABLES")
                tables = [x for x in SQLConnector.cursor]
                break

            except Exception as e:
                self.reconnect_to_db()
    

    def find_users(self, username=None):
        #Function to retrieve users from db (all and by id)
        if username is None:
            #Returns list of usernames and emails already registered
            query = "SELECT email, userName FROM users"

            while True:
                try:
                    SQLConnector.cursor.execute(query)
                    result = SQLConnector.cursor.fetchall()
                    return result

                except Exception as e:
                    self.reconnect_to_db()

        else:
            query = "SELECT * FROM users WHERE userName='" + str(username) + "'"
            
            while True:
                try:
                    SQLConnector.cursor.execute(query)
                    result = SQLConnector.cursor.fetchone()
                    return result
                
                except Exception as e:
                    self.reconnect_to_db()

    def add_user(self, user:dict):
        #Function to add new user
        query = "INSERT INTO `users` (`firstName`, `lastName`, `email`, `userName`, `password`, `county`, `state`) "
        values = f"VALUES ('{user['firstName']}', '{user['lastName']}', '{user['email']}', '{user['userName']}', '{user['password']}', '{user['county']}', '{user['state']}'); "
        
        while True:
            try:
                SQLConnector.cursor.execute(query + values)
                SQLConnector.db.commit()
                return True
            except Exception as e:
                logging.exception("FAILED TO INSERT DATA")
                return False

    def update_user(self, user:dict):
        #Function to updater user info
        query = f"UPDATE users SET firstName='{user['firstName']}', lastName= '{user['lastName']}', email='{user['email']}',"
        queryCont = f" userName= '{user['userName']}', password='{user['password']}', county='{user['county']}', state ='{user['state']}' "
        condition = f"WHERE id={user['id']};"

        full_query = query + queryCont + condition
        
        while True:
            try:
                SQLConnector.cursor.execute(full_query)
                SQLConnector.db.commit()
                return True
            except Exception as e:
                logging.exception("FAILED TO UPDATE DATA")
                self.reconnect_to_db()

    def get_counties(self, state):
        '''
        Function to get counties
        '''
        while True:
            try:
                query = f'SELECT county FROM counties where state ="{state}";'
                SQLConnector.cursor.execute(query)
                result  = SQLConnector.cursor.fetchall()
                return result

            except Exception as e:
                self.reconnect_to_db()


    def get_all_data_per_county(self, county:str, state:str):
        fips = self.get_fips(state, county)
        query = "SELECT * FROM " + fips +";"
        
        tmp = None
        while True:
            try:
                SQLConnector.cursor.execute(query)
                tmp = SQLConnector.cursor.fetchall()
                
                break
            except Exception as e:
                print(e)
                self.reconnect_to_db()
        
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


    def get_county_info(self,fips,days = None):
        '''
        Function to get info per county: fips = fips_8055
        '''
        while True:
            try:
                if days is None:
                    SQLConnector.cursor.execute("SELECT * FROM " + fips)
                else:
                    SQLConnector.cursor.execute("SELECT * FROM " + fips + " WHERE time>CURRENT_DATE - INTERVAL " + str(days + 1) + " DAY")
                result  = SQLConnector.cursor.fetchall()
                break

            except Exception as e:
                self.reconnect_to_db()
        
        refined_result = {}
        for res in result:
            refined_result[res[-1].strftime("%m/%d/%Y")] = {"cases":res[1],"deaths":res[2],"confirmed_cases":res[3],"confirmed_deaths":res[4]}
        return refined_result

    def get_all_state_county(self):
        query = "SELECT county, state FROM counties;"
        result = None

        while True:
            try:
                SQLConnector.cursor.execute(query)
                result = SQLConnector.cursor.fetchall()
                break

            except Exception as e:
                self.reconnect_to_db()

        if len(result) == 0:
            return None
        else:
            return result


    def get_fips(self,state,county):
        '''
        Unique county identifier
        '''
        query = 'SELECT fips FROM counties WHERE state="' + str(state) +'" AND county="' + str(county) + '";'
        
        result = None
        while True:
            try:
                SQLConnector.cursor.execute(query)
                result = SQLConnector.cursor.fetchall()
                break

            except Exception as e:
                self.reconnect_to_db()

        if len(result) == 0:
            return None
        else:
            return result[0][0]

    def fetch_online_data(self,commit = None):
        '''
        Get data from NY Times repo, needs to access commit history to get history
        Repo only shows one day
        '''
        link = None
        if commit is None:
            link = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv"
        else:
            link = "https://raw.githubusercontent.com/nytimes/covid-19-data/" + commit + "/live/us-counties.csv"

        dirname = os.path.dirname(__file__)
        latest = os.path.join(dirname, 'latest.csv')

        try:
            r = requests.get(link,allow_redirects=True)
            with open(latest,'wb') as f:
                f.write(r.content)
                f.close()

            return True
        except:
            logging.exception("FAILED TO GET LATEST DATA")
            return False

    
    def update_db(self,commit = None):
        '''
         Function fetches data and updates DB
        '''
        fetched = self.fetch_online_data(commit = commit)
        if not fetched:
            print("FAILED TO GET DATA")
            return
        #Current - data already in the data base
        dirname = os.path.dirname(__file__)

        current_data = os.path.join(dirname, 'current_data.csv')
        latest = os.path.join(dirname, 'latest.csv')

        if os.path.exists(current_data) and filecmp.cmp(current_data,latest,False):
            print("DATA ALREADY EXISTS")
            return

        if os.path.exists(current_data):
            os.remove(current_data)

        os.rename(latest, current_data)
        
        self.insert_new_data()


    def insert_history_data(self, commits):
        '''
        Gets all the data from commits history and seeds the db
        '''
        
        print(str(len(commits)) + 'commits retrieved')
        i = len(commits) - 1
        print('INSERTING COMMITS DATA')
        print('-'*40)
        while i > 0:
            print('\r' + str(i) + ' commits left', end='\r')
            print("")

            commit = commits[i]
           
            self.update_db(commit[0])
            i = i - 1

            
    
  
   
