#Adds higher lever package to path directory
import sys, os
dirname = os.path.dirname(__file__)
app_package_dir = os.path.join(dirname, '..')
sys.path.append(dirname)
sys.path.append(app_package_dir)

import time
from sql_connector import SQLConnector
from git import Repo

class Initiate_Database():
    #Creates tables and inserts history data
    def __init__(self):
        
        self.sql = SQLConnector()

    def get_commits(self, count):
        '''
        Get commit history data, to insert history data into database
        '''
        dirname = os.path.dirname(__file__)
        git_repo = os.path.join(dirname, 'tmp')
        if not os.path.exists(git_repo):
            repo = Repo.clone_from('https://github.com/nytimes/covid-19-data.git', git_repo)
        else:
            repo = Repo(git_repo)
            o = repo.remotes.origin
            o.pull()

        temp_commits = list(repo.iter_commits('master', max_count=count))

        commits = [(commit.hexsha,time.strftime("%a, %d %b %Y %H:%M", time.gmtime(commit.committed_date))) for commit in temp_commits]

        return commits

    def set_initial_data_no_history(self):
        #Creates all tables, add list of counties
        
        self.sql.set_initial_data()

    def set_initial_data_and_history(self):
        #Creates all tables, add list of counties, add historic data
        print('-'*40)
        commits = self.get_commits(5) #1350
        print(commits[-1])
        #return
        print('GETTING COMMITS')
        print('-'*40)
        print('FINISHED GETTING COMMITS')
        print('-'*40)
        self.sql.insert_history_data(commits)
        
        

if __name__=="__main__":

    setup = Initiate_Database()
    
    #Perform setup here
    #setup.set_initial_data_no_history()
    #setup.set_initial_data_and_history()


    print('Setup Done')

 
    

    
