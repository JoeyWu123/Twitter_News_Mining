import numpy as np
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import pickle
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import matplotlib.pyplot as plt
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from Text_Analyzer.text_processor import*
import pymongo
import streamlit as st
doc2vec_model= Doc2Vec.load("doc2vec_model.pickle")
def tfidf(lists):

    tfidf_vectorizer = TfidfVectorizer( lowercase=True, ngram_range=(1, 3))
    tfidf_matrix = tfidf_vectorizer.fit_transform(lists)
    features=tfidf_vectorizer.get_feature_names()

    sums = tfidf_matrix.sum(axis=0)
    data1 = []
    for col, term in enumerate(features):
        data1.append((term, sums[0, col]))
    ranking = pd.DataFrame(data1, columns=['term', 'rank'])
    words = (ranking.sort_values('rank', ascending=False))
    return words.head(15)



#add st.cache to speed up (see streamlit's document about cache)
@st.cache(show_spinner=False,ttl=12*3600)
def wordcluster(sentense,clusterOfIndex,clusterNumber):
    # tfIdf(not used by now)
    clusterText = [sentense[i] for i in clusterOfIndex[clusterNumber]]
    result= tfidf([' '.join(l) for l in clusterText])
    return result  #a dataframe with key words extracted and its tf-idf score

@st.cache(show_spinner=False,ttl=12*3600)
def kmeans_run(tokenized_tweets,k):

    infered_sentence_Matrix =[]
    for each_tokenized_tweet in tokenized_tweets:
        vector = doc2vec_model.infer_vector(each_tokenized_tweet)
        infered_sentence_Matrix.append(vector)
    model_kmeans =  KMeans(n_clusters=k, max_iter=400, n_init=10, init='k-means++', random_state=10, n_jobs=-1)
    # get vector data
    model_kmeans.fit(infered_sentence_Matrix)
    # get labels
    labels = model_kmeans.labels_   #labels are like [0,1,0,3...] with label [0] representing the cluster that vec[0] belongs to
    # find the index of twitter posts which are closest to centroid of each cluster
    center_tweets_index,_=pairwise_distances_argmin_min(model_kmeans.cluster_centers_,infered_sentence_Matrix)
    clusterofIndex = {}
    index=0
    for cluster_label in labels:
        if cluster_label not in clusterofIndex.keys():
            clusterofIndex[cluster_label]=[index]
        else:
            clusterofIndex[cluster_label].append(index)
        index=index+1
    return clusterofIndex,center_tweets_index





# if __name__ == '__main__':
#
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     my_db = myclient['Twitter_News']
#     text_list = []
#     id_list = []
#     source_list = []
#     my_tb=my_db["@CNN"]
#     result=my_tb.find({})
#     for each_row in result:
#         print(each_row['tokenized_text'])
#         text_list.append(each_row['tokenized_text'])
#         id_list.append(each_row['_id'])
#         source_list.append("@CNN")
#     print(text_list)
#     clusterOfIndex,cluster=kmeans_run(text_list,  3)
#     print(cluster)

    #clusterOfIndex,cluster=run(tweets, tweetsID, tweetsSource)
    #print("clusterofID: ", cluster)






