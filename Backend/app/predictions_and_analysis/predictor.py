import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model

dirname = os.path.dirname(__file__)
class Covid_Predictor(object):
    def __init__(self, sql_instance, country:str, state:str, county:str):
        self.sql = sql_instance
        self.country = country
        self.county = county
        self.state = state
        self.degree_cases = 3 #10
        self.degree_deaths = 3 #6


    #Function to train and save model
    def train_models(self):
      #get data
      try:
        
        data = self.sql.get_info(country = self.country, state=self.state, county=self.county, prediction=True)
        
      except Exception as e:
        print(e)
        return False
      
      #Preparing data for model
      df = pd.DataFrame(data, columns=['id','cases', 'deaths'])
      x = np.array(df['id']).reshape(-1, 1)
      y_cases = np.array(df['cases']).reshape(-1, 1)
      y_deaths = np.array(df['deaths']).reshape(-1, 1)

      #Preparing polynomial regression by setting degree > 1
      poly_features_cases = PolynomialFeatures(degree=self.degree_cases)
      poly_features_deaths = PolynomialFeatures(degree=self.degree_deaths)
      x_cases = poly_features_cases.fit_transform(x)
      x_deaths = poly_features_deaths.fit_transform(x)
     

      #Training the data
   
      model_cases = linear_model.LinearRegression()
      model_cases.fit(x_cases, y_cases) 

      model_deaths = linear_model.LinearRegression()
      model_deaths.fit(x_deaths, y_deaths)

      #Save models by unique identifier 
      uid = None
      if self.country is None:
            uid = 'world'
      else:
          if '*' in self.country:
            self.country = self.country.replace('*', '')

          if self.state is None:
                uid = self.country

          else:
                if self.county is None:
                    uid = self.country + '_' + self.state
                else:
                    uid = self.country + '_' + self.state + '_' + self.county

      filename_c = os.path.join(dirname, f'trained_models/Cases {uid}')
      filename_d = os.path.join(dirname, f'trained_models/Deaths {uid}')
              
      #Serialize data and save it for prediction
      joblib.dump(model_cases, filename_c)
      joblib.dump(model_deaths, filename_d)

      #Models accuracy
      accuracy_c = model_cases.score(x_cases, y_cases)
      #print(f'Model Accuracy - Cases: {round(accuracy_c*100, 3)} %')

      accuracy_d = model_deaths.score(x_deaths, y_deaths)
      #print(f'Model Accuracy - Deaths: {round(accuracy_d*100, 3)} %')


  #Function to perform prediction
    def predict(self, days:int):
      poly_features_cases = PolynomialFeatures(degree=self.degree_cases)
      poly_features_deaths = PolynomialFeatures(degree=self.degree_deaths)


      #Loading saved model
      uid = None
      if self.country is None:
            uid = 'world'
      else:
          if '*' in self.country:
            self.country = self.country.replace('*', '')
            
          if self.state is None:
                uid = self.country
          else:
                if self.county is None:
                    uid = self.country + '_' + self.state
                else:
                    uid = self.country + '_' + self.state + '_' + self.county

      filename_c = os.path.join(dirname, f'trained_models/Cases {uid}')
      filename_d = os.path.join(dirname, f'trained_models/Deaths {uid}')

      model_cases = joblib.load(filename_c)
      model_deaths = joblib.load(filename_d)

      predictions = []
      total_count = 0

      try:
        #Number of records for each county in the database
        data = self.sql.get_info(country = self.country, state=self.state, county=self.county, prediction=True)
        total_count = len(data)
      except:
        return predictions

      prediction_c = []
      prediction_d = []
     
      #Predict the next {days} days
      for i in range(1, days):
        
        #To predict next days, add days to total records
        days_to_predict = int(total_count + i)

        tmp1 = model_cases.predict(poly_features_cases.fit_transform([[days_to_predict]]))
        prediction_c.append(int(tmp1))

        tmp2 = model_deaths.predict(poly_features_deaths.fit_transform([[days_to_predict]]))
        prediction_d.append(int(tmp2))

      #[[cases...], [deaths...]]      
      predictions.append(prediction_c)
      predictions.append(prediction_d)

      return predictions
