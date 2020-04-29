Read this file carefully before you start running this project. Make sure you totally understand the followings. The wrong actions may cause unforeseen error!!!
1. Edit setup.json first, before you start running this program.
2. If you want to run with crawler (update your database per day), you must fill Twitter API Info in setup.json, and run crawler.py independently. Notice as MongoDB already has lock, we don't have to worry about data consistency. 
3. If you want to use the data we provide (in data folder). Remember to name your database as "Twitter_News" . The name of each collection under "Twitter_News" should be the same to the name of data file you are going to imported (such as "@CNN"). You can import data using MongoDB Compass.
4. Remember to run DB_Index.py under Utility folder to create indexes for your database (if you haven't done). It is NECESSARY before you execute main.py for the first time.
5. In setup.json. the default Keras Backend is tensorflow. There are three options: theano,tensorflow,cntk. Just choose the one you like (In this version we haven't used Keras to analyze sentiment yet)
4. You can edit media_list.txt, to add more media sources as you like. The crawler will check the target in media_list.txt every day, before fetching data. Notice you must input correct twitter username (case sensitive) with symbol @. Otherwise the crawler may crash.
5. If you want to deploy this project on Raspberry Pi. We recommend to set your environment as Ubuntu 20 +xfce4 (desktop environment)+MongoDB 3.6.8. The build in python version in Ubuntu 20 is Python 3.8, which is compatible with only theano as backend.
6. In Utility forder each script can be executed independently. They contain functions which may be helpful for you to do some management work. For example, in order to improve the performance of Doc2Vec, we recommend you to run Train_Doc2Vec.py regularly with tweets accumulating in database, and use the new pickle file of model generated to replace the old file.
7. In console, input streamlit run main.py to execute this project.

Package/Software requirements: MongoDB (3.4 or above), MongoDB Compass(optional), Python3, numpy, pandas, scikit-learn, keras (tensorflow), nltk, gensim, matplotlib, wordcloud, altair, streamlit, TwitterAPI, pymongo, pickle...

