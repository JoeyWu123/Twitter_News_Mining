from text_processor import*
from flair.models import TextClassifier
from flair.data import Sentence
import pymongo
flair_classifier = TextClassifier.load('en-sentiment')
def flair_analyzer(message):  #based on rnn and word2vec
    #flair cannot run on raspberry pi, as it replies on Google's sentencepiece, which
    #isn't be compatible with arm so far
    message=preprocess_tweet(message)
    sentence = Sentence(message)
    flair_classifier.predict(sentence)
    result=sentence.labels[0]
    if(result.value=='NEGATIVE'):
        return -result.score
    else:
        return result.score
if __name__=='__main__':
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    my_db = my_client.get_database('Twitter_News')
    my_tb= my_db['@BBCWorld']
    result=my_tb.find({})
    i=0
    for post in result:
        print(post['text'])
        print(flair_analyzer(post['text']))