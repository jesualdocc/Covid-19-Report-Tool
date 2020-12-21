import os
import joblib
import numpy as np
import pandas as pd
from sql_connector import SQLConnector
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


class Covid_Predictor(object):
    def __init__(self, sql_instance:SQLConnector, county:str, state:str, polynomial_degree:int=7):
        self.sql = sql_instance
        self.county = county
        self.state = state
        self.degree = polynomial_degree


    #Function to train and save model
    def train_models(self):
      #get data
      try:
        data = self.sql.get_all_data_per_county(self.county, self.state)
      except Exception as e:
        return False
      
      
      #Preparing data for model
      df = pd.DataFrame(data, columns=['id','cases', 'deaths'])
      x = np.array(df['id']).reshape(-1, 1)
      y_cases = np.array(df['cases']).reshape(-1, 1)
      y_deaths = np.array(df['deaths']).reshape(-1, 1)

      poly_features = PolynomialFeatures(degree=self.degree)
      x = poly_features.fit_transform(x)

      #Training the data

      model_cases = linear_model.LinearRegression()
      model_cases.fit(x, y_cases)

      model_deaths = linear_model.LinearRegression()
      model_deaths.fit(x, y_deaths)

      fips = self.sql.get_fips(self.state, self.county)
      dirname = os.path.dirname(__file__)
      filename_c = os.path.join(dirname, f'trained models/Cases {fips}')
      filename_d = os.path.join(dirname, f'trained models/Deaths {fips}')
      
      joblib.dump(model_cases, filename_c)
      joblib.dump(model_deaths, filename_d)

      accuracy_c = model_cases.score(x, y_cases)
      print(f'Accuracy: {round(accuracy_c*100, 3)} %')

      accuracy_d = model_deaths.score(x, y_deaths)
      print(f'Accuracy: {round(accuracy_d*100, 3)} %')


  #Function to perform prediction
    def predict(self, days:int):
      poly_features = PolynomialFeatures(degree=self.degree)

      fips = self.sql.get_fips(self.state, self.county)
      dirname = os.path.dirname(__file__)
      filename_c = os.path.join(dirname, f'trained models/Cases {fips}')
      filename_d = os.path.join(dirname, f'trained models/Deaths {fips}')

      model_cases = joblib.load(filename_c)
      model_deaths = joblib.load(filename_d)

      predictions = []
      total_count = 0
      try:
        total_count = self.sql.get_total_per_county(self.county, self.state)
      except:
        return predictions

      prediction_c = []
      prediction_d = []
     
      #Predict the next {days} days
      for i in range(1, days+1):

        days_to_predict = int(total_count[0] + i)

        tmp1 = model_cases.predict(poly_features.fit_transform([[days_to_predict]]))
        prediction_c.append(int(tmp1))

        tmp2 = model_deaths.predict(poly_features.fit_transform([[days_to_predict]]))
        prediction_d.append(int(tmp2))

      
      predictions.append(prediction_c)
      predictions.append(prediction_d)

      return predictions
                



