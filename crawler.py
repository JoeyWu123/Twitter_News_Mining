from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterPager
from dateutil.parser import parse
import json
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import os
import time
from datetime import datetime,timezone,timedelta
from multiprocessing import Process,Lock
from text_processor import*
from Text_Analyzer.nltk_analyzer import*
def write_log(message):
    now_time=str(datetime.now())
    file=open("crawler_log.log",'a')
    to_write=now_time+" "+message+"\n"
    file.write(to_write)
    file.close()
def fetch_twitter(user,API_key,API_secret_key,Access_Token,Access_token_secret):

    api = TwitterAPI(consumer_key=API_key,
                     consumer_secret=API_secret_key,
                     access_token_key=Access_Token,
                     access_token_secret=Access_token_secret)
    SCREEN_NAME = user
    #the following request get the 200 most recent tweets from a user
    try:
        r = api.request('statuses/user_timeline', {'tweet_mode':"extended",'screen_name': SCREEN_NAME,'count':200,'exclude_replies':1})
        if(r.status_code != 200):
            print('PROBLEM: ' + r.text)
            write_log('PROBLEM while fetching data from '+user+' : ' + r.text)
            return -1
        else:
            data=r.json()
            return data
    except:
        print("API Error, check your network")
        write_log("API Error")
        return -1
def run_crawler(API_key,API_secret_key,Access_Token,Access_token_secret):
    print("The crawler is running")
    write_log("The crawler is running")
    try:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        info = myclient.server_info()
    except ServerSelectionTimeoutError:
        print("Mongo DB access error, break")
        write_log("Mongo DB access error, break")
        return -1
    mydb = myclient.get_database('Twitter_News')
    while(1):
        media_list = []
        file_list = os.listdir()
        if ('media_list.txt' not in file_list):
            media_list = ["@nytimes", "@CNN", "@washingtonpost", "@NBCNews", "@BBCWorld", "@SCMPNews",
                          "@CGTNOfficial"]
        else:
            file = open('media_list.txt', 'r')
            while (1):
                media = file.readline().strip()
                if (media == ""):
                    break
                media_list.append(media)
            file.close()
            #each time we start crawler, we check database, and delete tweets which are created 180 days ago (only keep data of 180 days)
        now_time = datetime.now(timezone.utc)
        half_year_ago = now_time - timedelta(days=180)
        myquery = {"time": {"$lt": half_year_ago}}
        all_table = mydb.list_collection_names()
        # on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
        if('system.indexes' in all_table):
            all_table.remove('system.indexes')
        for table in all_table:
            my_current_tb = mydb[table]
            my_current_tb.delete_many(myquery)  # we only keep data for 15 days
        for user in media_list:
            my_tb = mydb[user]
            print("Crawling data from "+user)
            write_log("Crawling data from "+user)
            data=fetch_twitter(user,API_key,API_secret_key,Access_Token,Access_token_secret)
            if(data==-1):
                return -1  #the fetch_twitter function already write log under this situation
            for i in data:
                id=i['id']
                text=i['full_text']
                like=i['favorite_count']
                retweet=i['retweet_count']
                t_time=parse(i['created_at'])
                if(my_tb.count_documents({"_id":id})!=0):    #if the tweets got is old posts (already in database)
                    my_tb.update_one({"_id": id}, {"$set":{"like": like,"retweet":retweet}})   #update like, retweet info
                    
                else:   #new tweets
                    tokenized_text=processText(text)
                    # some twitter only contains link, and the tokenized_text returned is []
                    #filter this data
                    if(len(tokenized_text)!=0):
                        vader_score = vader_analyzer(text)
                        naive_bayes_score=naive_bayes_analyzer(text)
                        my_tb.insert_one(
                        {"_id": id, "text": text, "like": like, "retweet": retweet,
                         "time": t_time, "VADER_Score": vader_score, "Naive_Bayes_Score":naive_bayes_score,"RNN_Score":None,"SVM_Score":None,"tokenized_text":tokenized_text})
        finish_time=datetime.now()
        print(finish_time," Finish data crawling today,sleeping for next 24 hours...")
        write_log("Finish data crawling")
        time.sleep(24*3600)
if __name__=='__main__':
    with open("setup.json", 'r') as f:
        data = json.load(f)
    API_key=data['Twitter API Key']
    API_secret_key=data['Twitter API Secret key']
    Access_Token=data['Twitter Access Token']
    Access_secret_token=data['Twitter Access Secret Token']
    backend=data['Keras Backend']
    run_crawler(API_key,API_secret_key,Access_Token,Access_secret_token)
