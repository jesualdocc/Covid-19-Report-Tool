import tweepy
import joblib
import os
import json
import datetime
import pandas as pd
import numpy as np
import re
import string
from configuration.config import Config

#For word processing
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
# ML Libraries
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC


class TwitterFeed(object):
    def __init__(self):
        #nltk.download('stopwords')
        #nltk.download('punkt')

        #Global paramters
        self.stop_words = set (stopwords.words('english'))
        dirname = os.path.dirname(__file__)
        self.filename_data = os.path.join(dirname, 'twitter_model/twitter_training.csv')
        self.filename_model = os.path.join(dirname, 'twitter_model/trained_twitter_model')

        #Load dataseet for training
        df = pd.read_csv(self.filename_data, encoding='latin-1') 
        df.columns = ['target', 't_id', 'created_at', 'query', 'user', 'text']
        
        #Removing columns that are not needed
        self.dataset = df.drop(columns=['user', 't_id', 'created_at', 'query'])

        #Set up connection to twitter api
        self.config_tweepy()

        #Same tf vector will be used for Testing sentiments on unseen trending data
        self.tf_vector = self.get_feature_vector(np.array(self.dataset.iloc[:, 1]).ravel())
        print(self.tf_vector)
        

    def preprocess_tweet_text(self, tweet):
        tweet.lower()
        # Remove urls
        tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)
        # Remove user @ references and '#' from tweet
        tweet = re.sub(r'\@\w+|\#','', tweet)
        # Remove punctuations
        tweet = tweet.translate(str.maketrans('', '', string.punctuation))
        # Remove stopwords
        tweet_tokens = word_tokenize(tweet)
        filtered_words = [w for w in tweet_tokens if not w in self.stop_words]
                
        return " ".join(filtered_words)
    
    def get_feature_vector(self, train_fit):
        '''
        vectorization using tf-idf
        '''
        vector = TfidfVectorizer(sublinear_tf=True)
        vector.fit(train_fit)
        return vector
    
    def int_to_string(self, sentiment):
        '''
        The target column is comprised of the integer values 0, 2, and 4. 
        But users do not usually want their results in this form.
        To convert the integer results to be easily understood by users, you can implement a small script.
        '''

        if sentiment == 0:
            return "Negative"
        elif sentiment == 2:
            return "Neutral"
        else:
            return "Positive"

    def train_model(self):
        #Preprocess data
        self.dataset.text = self.dataset['text'].apply(self.preprocess_tweet_text)
        
        # Split dataset into Train, Test
        X = self.tf_vector.transform(np.array(self.dataset.iloc[:, 1]).ravel())
        y = np.array(self.dataset.iloc[:, 0]).ravel()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=30)

        # Training Logistics Regression model
        LR_model = LogisticRegression(solver='lbfgs')
        LR_model.fit(X_train, y_train)
        y_predict_lr = LR_model.predict(X_test)
        print(accuracy_score(y_test, y_predict_lr))

        #Save model
        joblib.dump(LR_model, self.filename_model)
    
    
    def config_tweepy(self):
        auth = tweepy.OAuthHandler(Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET_KEY)
        auth.set_access_token(Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def isEnglish(self, text):
        try:
            text.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True
    
        '''
    Getting Tweets for the given hashtag with max of 1000 popular tweets with english dialect
    '''
    def get_tweets(self, query, num_of_tweets):
        
        tweets = []
        for status in tweepy.Cursor(self.api.search,
                        q=query,
                        count=num_of_tweets,
                        result_type='popular',
                        include_entities=True,
                        monitor_rate_limit=True, 
                        wait_on_rate_limit=True,
                        lang="en").items():
        
            # Getting only tweets which has english dialects
            if self.isEnglish(status.text) == True:
                '''
                status.id_str
                status.created_at.strftime('%d-%m-%Y %H:%M'),
                status.user.screen_name,
                '''
                tweets.append([ query, status.text])
        return tweets

    def perform_analysis(self):
        LR_model = joblib.load(self.filename_model)

        tweets = self.get_tweets('covid', 10)

        dff = pd.DataFrame(tweets, columns=['hashtag', "text"])
        test_ds = dff["text"].apply(self.preprocess_tweet_text)

        tf_vector = self.get_feature_vector(np.array(test_ds.iloc[:]).ravel())
        test_feature = tf_vector.transform(np.array(test_ds.iloc[:]).ravel())
        
        # Using Logistic Regression model for prediction
        test_prediction_lr = LR_model.predict(test_feature)

        # Averaging out the hashtags result
        test_result_ds = pd.DataFrame({'hashtag': test_ds.hashtag, 'prediction':test_prediction_lr})
        test_result = test_result_ds.groupby(['hashtag']).max().reset_index()
        test_result.columns = ['heashtag', 'predictions']
        test_result.predictions = test_result['predictions'].apply(self.int_to_string)

        print(test_result)
        

tw = TwitterFeed()
tw.perform_analysis()







# # Using Logistic Regression model for prediction
# test_prediction_lr = LR_model.predict(test_feature)

# # Averaging out the hashtags result
# test_result_ds = pd.DataFrame({'hashtag': test_ds.hashtag, 'prediction':test_prediction_lr})
# test_result = test_result_ds.groupby(['hashtag']).max().reset_index()
# test_result.columns = ['heashtag', 'predictions']
# test_result.predictions = test_result['predictions'].apply(int_to_string)

# print(test_result)



