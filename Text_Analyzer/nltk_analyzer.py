import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re,string
import pymongo
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
import pickle
from text_processor import*
#load the trained naive bayes model
f = open('naive_bayes_model.pickle', 'rb')
naive_bayes_classifier = pickle.load(f)
f.close()
def vader_analyzer(message):    #rule based
    message=preprocess_tweet(message)
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(message)['compound']

def naive_bayes_analyzer(message):


    message_tokens = remove_noise(word_tokenize(message))
    if naive_bayes_classifier.classify(dict([token, True] for token in message_tokens))=="Positive":
        return 1
    else:
        return -1

if __name__=='__main__':
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    my_db = my_client.get_database('Twitter_News')
    my_tb= my_db['@BBCWorld']
    result=my_tb.find({})
    i=0
    for post in result:
        print(post['text'])
        print(vader_analyzer(post['text']))

    #nltk.download('twitter_samples')
