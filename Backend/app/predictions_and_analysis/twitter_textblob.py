import tweepy
import re
import nltk
from textblob import TextBlob
from config import Config

class Twitter_Textblob(object):

    def __init__(self):
        #nltk.download()
        self.config_tweepy()

    def config_tweepy(self):
        #Set up connection to twitter api
        auth = tweepy.OAuthHandler(
            Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET_KEY)
        auth.set_access_token(Config.TWITTER_ACCESS_TOKEN,
                              Config.TWITTER_ACESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def clean_tweet(self, tweet):
            '''
            Cleans tweet text by removing links,
            special characters - using regex statements.
            '''
            return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        ''' 
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, geo_location, count=10):
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count, lang = 'en', tweet_mode='extended', geocode=geo_location)

            if len(fetched_tweets) == 0:
                #No tweets found in the area (get all)
                fetched_tweets = self.api.search(q=query, count=count, lang = 'en', tweet_mode='extended')

            
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
                
                # saving text of tweet
                parsed_tweet['text'] = tweet.full_text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(
                    tweet.full_text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            print(str(e))
            return []
            # print error (if any)
