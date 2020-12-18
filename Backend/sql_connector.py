import mysql.connector
import pandas as pd
import requests
import filecmp
import logging
import os
import time

from git import Repo, Commit

class SQLConnector(object):
    """docstring fo SQLConnector."""

    def __init__(self, host,user,password,database):
        self.db = mysql.connector.connect(host=host,user=user,password=password,database = database)
        self.cursor = self.db.cursor()

    def get_tables(self):
        self.cursor.execute("SHOW TABLES")
        tables = [x for x in self.cursor]
    

    def create_user_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS " + "users")
        sql = "CREATE TABLE "+ "users " +"(id int NOT NULL AUTO_INCREMENT,firstName VARCHAR(45) NOT NULL, lastName VARCHAR(45) NOT NULL,email VARCHAR(45) NOT NULL,userName VARCHAR(45) NOT NULL, password VARCHAR(200) NOT NULL,county VARCHAR(45) NOT NULL, state VARCHAR(45) NOT NULL,PRIMARY KEY (id), UNIQUE(userName), UNIQUE(email));"
        self.cursor.execute(sql)

    def create_county_table(self,table_name,data,force_drop = True):
        county_info = data #self.get_initial_data()
        self.cursor.execute("DROP TABLE IF EXISTS " + table_name)
        sql = "CREATE TABLE "+ table_name +"( fips VARCHAR(45) NOT NULL,state VARCHAR(45) NULL,county VARCHAR(45) NULL, PRIMARY KEY (fips));"
        self.cursor.execute(sql)

        sql = "INSERT INTO "+ table_name +" (fips, state, county) VALUES (%s, %s, %s)"
        print(county_info[:5])
        self.cursor.executemany(sql, county_info)
        self.db.commit()


    def create_stat_table(self,table_name,columns,force_drop = False):

        if force_drop:
            self.cursor.execute("DROP TABLE IF EXISTS " + table_name)
        sql = "CREATE TABLE IF NOT EXISTS " + table_name + " ( id INT AUTO_INCREMENT PRIMARY KEY"
        start = True
        for column_name,column_type in columns:
            sql = sql + "," + column_name + " " + column_type

        sql = sql + ")"

        self.cursor.execute(sql)

    def set_initial_data(self, username):
        '''
            Function to setup the schema for the database
        '''
        df = pd.read_csv("current_data.csv")
        df = df.dropna(subset=['fips'])
        df["fips"] = df.fips.apply(lambda x: "fips_" + str(int(x)))
        county_info = list(zip(df.fips,df.state,df.county))
        stat_columns = [(column,"INT") for column in df.columns if column not in ['fips','county','state','date']]
        self.create_county_table("counties",county_info)
        self.create_user_table()
        stat_columns.append(('time','DATETIME'))
        print(len(stat_columns))
        print("STAT_COLUMNS: ", stat_columns)
        for fips in df["fips"]:
            self.create_stat_table(fips,stat_columns,force_drop = True)

    def find_users(self, username=None):
        #Function to retrieve users from db (all and by id)
        if username is None:
            #Returns list of usernames and emails already registered
            query = "SELECT email, userName FROM users"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result

        else:
            query = "SELECT * FROM users WHERE userName='" + str(username) + "'"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result

    def add_user(self, user:dict):
        #Function to add new user
        query = "INSERT INTO `users` (`firstName`, `lastName`, `email`, `userName`, `password`, `county`, `state`) "
        values = f"VALUES ('{user['firstName']}', '{user['lastName']}', '{user['email']}', '{user['userName']}', '{user['password']}', '{user['county']}', '{user['state']}'); "
        
        try:
            self.cursor.execute(query + values)
            self.db.commit()
            return True
        except:
            logging.exception("FAILED TO INSERT DATA")
            return False

    def update_user(self, user:dict):
        #Function to updater user info
        query = f"UPDATE `users` SET 'firstName' ='{user['firstName']}', 'lastName' = '{user['lastName']}'', `email`='{user['email']}',"
        queryCont = f" `userName`= '{user['userName']}', `password`='{user['password']}', `county`='{user['county']}', `state` ='{user['state']}' "
        condition = f"WHERE 'id'='{user['id']}'"

        full_query = query + queryCont + condition
        print(full_query)
        try:
            self.cursor.execute(full_query)
            self.db.commit()
            return True
        except:
            logging.exception("FAILED TO UPDATE DATA")
            return False



    def insert_new_data(self):
        print("*********** INSERTING THE LATEST DATA *************************")
        df = pd.read_csv("current_data.csv")
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
        print(stat_columns)
        print(stat_df.head())

        for index, row in df.iterrows():
            values = row[stat_columns].values.tolist()
            values = [str(x) for x in values]
            value_str = ",".join(values)
            value_str = value_str.replace("nan","0")
            sql = "INSERT INTO "+ row["fips"] + " " + stat_str + " VALUES (" + value_str + ")"
            #print(sql)
            self.cursor.execute(sql)
            self.db.commit()

    def fetch_online_data(self,commit = None):
        if commit is None:
            link = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv"
        else:
            link = "https://raw.githubusercontent.com/nytimes/covid-19-data/" + commit + "/live/us-counties.csv"

        print("LINK: ", link)
        try:
            r = requests.get(link,allow_redirects=True)
            with open('latest.csv','wb') as f:
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

        current_data = os.path.join(os.getcwd(),"current_data.csv")
        if os.path.exists(current_data) and filecmp.cmp("current_data.csv","latest.csv",False):
            print("DATA ALREADY EXISTS")
            return

        if os.path.exists(current_data):
            os.remove("current_data.csv")

        os.rename("latest.csv","current_data.csv")

        self.insert_new_data()

    def get_counties(self):
        '''
        Function to get counties
        '''
        self.cursor.execute("SELECT * FROM counties")
        result  = self.cursor.fetchall()
        return result

    def get_county_info(self,fips,days = None):
        '''
        Function to get info per county: fips = fips_8055
        '''
        print("FIPS: ", fips, " DAYS: ", days)
        if days is None:
            self.cursor.execute("SELECT * FROM " + fips)
        else:
            self.cursor.execute("SELECT * FROM " + fips + " WHERE time>CURRENT_DATE - INTERVAL " + str(days) + " DAY")
        result  = self.cursor.fetchall()
        
        refined_result = {}
        for res in result:
            refined_result[res[-1].strftime("%d-%b-%Y")] = {"cases":res[1],"deaths":res[2],"confirmed_cases":res[3],"confirmed_deaths":res[4]}
        return refined_result

    def get_fips(self,state,county):
        query = "SELECT fips FROM counties WHERE state='" + str(state) +"' AND county='" + str(county) + "';"
        print("QUERY: " + query)
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        print(result)
        if len(result) == 0:
            return None
        else:
            return result[0][0]
        return result

    def get_commits(self):
        git_repo = os.path.join(os.getcwd(),'tmp')
        if not os.path.exists(git_repo):
            repo = Repo.clone_from('https://github.com/nytimes/covid-19-data.git', git_repo)
        else:
            repo = Repo(git_repo)

        temp_commits = list(repo.iter_commits('master', max_count=200))

        commits = [(commit.hexsha,time.strftime("%a, %d %b %Y %H:%M", time.gmtime(commit.committed_date))) for commit in temp_commits]

        return commits

    def insert_history_data(self):
        commits = self.get_commits()
        i = len(commits) - 1
        while i > 0:
            commit = commits[i]
            print(commit)
            self.update_db(commit[0])
            i = i - 1


if __name__=="__main__":
    pass
    sql = SQLConnector("localhost","root","Jesualdo2020","coviddb")
    #sql.create_user_table()
    
   
    #sql.insert_history_data()
   
    #sql.update_db()
    #sql.insert_new_data()
    #sql.set_initial_data()
    
    #sql.get_initial_data()
    
