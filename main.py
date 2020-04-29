import streamlit as st
import numpy as np
import altair as alt
import pandas as pd
pd.set_option('display.max_columns', 20)
from datetime import datetime,timezone,timedelta
import os
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
from Kmean import*
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
import time
import json
import multiprocessing
from Text_Analyzer.nltk_analyzer import*
def get_sentiment_score(id_list,plain_text_list,source_list,sentiment_score_list,semtiment_model,index,my_db):
    if (semtiment_model=="Vader(Rule Based)"):
        if(sentiment_score_list[index]!=None):
            to_return= sentiment_score_list[index]
        else:
            to_return=vader_analyzer(plain_text_list[index])
            my_tb=my_db[source_list[index]]
            my_tb.update_one({"_id": id_list[index]}, {"$set": {"VADER_Score":to_return}})
            sentiment_score_list[index]=to_return
        #notice vader model returns scores between -1 to 1(from negative to positive); we need to polarize the score to -1 or 1
        #in order to get better visualization effect. Otherwise, the mean sentiment score of all posts in a cluster is too close to 0
        if(to_return<0):
            return -1
        if(to_return>0):
            return 1
        return to_return
    elif (semtiment_model=="Naive Bayes"):
        if (sentiment_score_list[index]!=None):
            print(sentiment_score_list[index])
            return sentiment_score_list[index]
        else:
            to_return=naive_bayes_analyzer(plain_text_list[index])
            my_tb = my_db[source_list[index]]
            my_tb.update_one({"_id": id_list[index]}, {"$set": {"Naive_Bayes_Score": to_return}})
            sentiment_score_list[index] = to_return
            return to_return

def main():
    st.title('Twitter Hot-Spot News Topics Mining (Past 15 Days)')

    st.text("Author: Zhuoyi (Joey) Wu, Ziyao Sun from the George Washington University\nGithub: https://github.com/JoeyWu123/Twitter_News_Mining")

    search_key = st.sidebar.text_input(label='Search Box For Twitter (Leave it Blank to Search All)', value='')

    semtiment_model = st.sidebar.selectbox("Select Model to Predict Sentiment",('Vader(Rule Based)', 'Naive Bayes'))
    st.sidebar.markdown('-Select Sources of Tweets to Analyze-')
    media_list = []
    #read the file media_list
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
    check_box_list=[]
    for each_media in media_list:
        check_box=st.sidebar.checkbox(label=each_media)
        check_box_list.append(check_box)
    show_select_all=1
    select_all_box = False
    # if no check box of medias is chosen, show select_all box, otherwise, select_all box will not be shown
    for each_check_box in check_box_list:
        if(each_check_box==True):
            show_select_all=0
            break
    if(show_select_all==1):
        select_all_box=st.sidebar.checkbox('Select ALL',True)
        check_box_list.append(select_all_box)
    #k=st.number_input(label="Input Cluster Number",min_value=1,step=1)
    k=st.slider("Cluster Number K",min_value=1,max_value=30,step=1)
    st.info("While cluster number K is larger, each hot-spot cluster contains topics which are more general. While cluster number K is smaller,\
each hot-spot cluster contains topics which are more specific. There is no certain value of cluster number,\
try different numbers to find the best clustering result.")

    #after the button is click
    if st.button('run'):
        try:
            myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            info = myclient.server_info()
        except ServerSelectionTimeoutError:
            print("Mongo DB access error, break")
            return -1
        #make sure there is check box ticked before run
        all_false=1
        for each_check_box in check_box_list:
            if each_check_box==True:
                all_false=0
                break
        # if no check box is ticked
        if all_false==1:
            st.warning("Select Sources of Tweets on the Left Panel, to begin")
        # find out which medias are chosen
        media_to_search=[]
        if(select_all_box==True):
            media_to_search=media_list
        else:
            pos=0
            for each in check_box_list:
                if each==True:
                    media_to_search.append(media_list[pos])
                pos=pos+1
        my_db= myclient['Twitter_News']
        tokenized_text_list=[]
        plain_text_list=[]
        id_list=[]
        source_list=[]
        retweet_list=[]
        sentiment_score_list=[]
        now_time=datetime.now(timezone.utc)
        for each_source in media_to_search:
            my_tb=my_db[each_source]
            if search_key=="":
                result = my_tb.find({"time":{"$gte":now_time - timedelta(days=15)}})
            else:
                result=my_tb.find({ "$text": { "$search": search_key},"time":{"$gte":now_time - timedelta(days=15)}} )
            for each_row in result:
                plain_text_list.append(each_row['text'])
                tokenized_text_list.append(each_row['tokenized_text'])
                id_list.append(each_row['_id'])
                retweet_list.append(each_row['retweet'])
                source_list.append(each_source)
                if(semtiment_model=="Vader(Rule Based)"):
                    sentiment_score_list.append(each_row['VADER_Score'])
                elif (semtiment_model=="Naive Bayes"):
                    sentiment_score_list.append(each_row['Naive_Bayes_Score'])

        if len(id_list)==0 :
            st.markdown("No Result is Found to cluster, Try Changing Your Key Word or Media Sources")
            return
        if(len(id_list)<=k):
            k=len(id_list)
            st.markdown("Cluster Number K is Larger Than The Number of Tweets Found; K will be changed to "+str(k))
        st.text(str(len(id_list)) + " tweets are found")
        st.info("Notice we just want to show the real analysis result. It is not our responsibility to filter any offensive words")
        clusterOfIndex,center_tweets_index=kmeans_run(tokenized_text_list,k)   #clusterOfIndex is like {cluster 0{index1,index2...}}
        #cluster_retweet is a list; cluster_retweet[i]=total retweet number in cluster i
        cluster_retweet=[]
        # five columns "sentiment(ave)","attention(total retweet number in one cluster)","center_tweet",
        # "tweets number (total tweet number in one cluster)","cluster_number"
        cluster_matrix=[]
        cluster_tf_idf_mat=[]  #three column:term (hot word,tf-idf score, cluster number it belongs to)
        all_hot_topics = []
        all_cluster_number=list(clusterOfIndex.keys())
        all_cluster_number.sort()  #make sure cluster_name is listed as 0,1,2,3...
        for cluster_number in all_cluster_number:
            # wordcluster returns a dataframe, with columns terms and rank
            each_cluster_key_word=wordcluster(tokenized_text_list, clusterOfIndex, cluster_number)
            hot_words=list(each_cluster_key_word['term'])
            all_hot_topics.append(hot_words)
            tf_idf_score=list(each_cluster_key_word['rank'])

            for i in range(len(hot_words)):
                cluster_tf_idf_mat.append([hot_words[i],tf_idf_score[i],cluster_number])
            retweet_sum=0
            sentiment_score_sum=0
            for each_index in clusterOfIndex[cluster_number]:
                retweet_sum=retweet_sum+retweet_list[each_index]
                sentiment_score_sum=sentiment_score_sum+get_sentiment_score(id_list,plain_text_list,source_list,
                                                                            sentiment_score_list,semtiment_model,each_index,my_db)
            cluster_retweet.append(retweet_sum)
            ave_sentiment=sentiment_score_sum/len(clusterOfIndex[cluster_number])

            cluster_matrix.append([ave_sentiment,retweet_sum,plain_text_list[center_tweets_index[cluster_number]],
                                   len(clusterOfIndex[cluster_number]),cluster_number])
        cluster_matrix=pd.DataFrame(cluster_matrix,columns=["sentiment","attention","Center Tweet","Tweets Number in Cluster","cluster_number"])
        cluster_tf_idf_mat=pd.DataFrame(cluster_tf_idf_mat,columns=["term","tf_idf_score","cluster_number"])
        word_freq_dic={}  #key: all terms (hot words), value: the total retweet number of all clusters containing this key word
        for i in range(len(all_hot_topics)):
            for each_word in all_hot_topics[i]:
                if(each_word in word_freq_dic):
                    word_freq_dic[each_word]=word_freq_dic[each_word]+cluster_retweet[i]
                else:
                    word_freq_dic[each_word]=int(cluster_retweet[i])
        #draw wordcloud
        st.subheader("Overall Wordcloud Based on Search Result")
        wordcloud_graph=WordCloud(background_color='white',width=1700,height=1200).generate_from_frequencies(word_freq_dic)
        plt.imshow(wordcloud_graph, interpolation='bilinear')
        plt.axis("off")
        st.pyplot()
        #draw clustering result
        st.subheader("The Clustering Result With Key Words and Sentiment")
        st.text("Click Each Circle to See Specific Key Words in Each Cluster")
        selector = alt.selection_single(empty='all', fields=['cluster_number'])
        data=pd.merge(cluster_matrix, cluster_tf_idf_mat, on='cluster_number')
        base = alt.Chart(data).properties(
            width=400
        ).add_selection(selector)
        categorical_chart = base.mark_circle(size=800).encode(x=alt.X("sentiment",scale=alt.Scale(domain=(-1, 1)),
                axis=alt.Axis(title="Sentiment Score",labelFontSize=14,titleFontSize=18,labelFontStyle="Roman")),
        y=alt.Y("attention",axis=alt.Axis(title="Attention (Based on Retweet Number)",labelFontSize=14,titleFontSize=18,labelFontStyle="Roman")),
        color=alt.condition(selector, 'sentiment', alt.value('lightgray'),
        scale=alt.Scale(scheme="redyellowgreen",domain=(-1, 1))),tooltip=["Center Tweet","Tweets Number in Cluster"])
        key_word_histogram = base.mark_bar().encode(
            x=alt.X('tf_idf_score',aggregate="sum",axis=alt.Axis(title="Sum of TF-IDF Score",labelFontSize=14,titleFontSize=18,labelFontStyle="Roman")),
            y=alt.Y('term',sort='-x',axis=alt.Axis(title="Key Words",labelFontSize=14,
                                                   labelFontStyle="Italic",titleFontSize=18))).transform_filter(selector)
       # alt.layer(key_word_histogram,categorical_chart).configure_view(fontSize=20,fontStyle="Altair Regular").configure_title(fontSize=30)
        st.altair_chart(categorical_chart&key_word_histogram, use_container_width=True)
        #st.altair_chart(key_word_histogram, use_container_width=True)
if __name__=='__main__':
    multiprocessing.freeze_support()
    main()
