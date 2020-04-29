import pymongo
from pymongo import TEXT
def main():
    remote_db= input("Input the IP address of your database :")
    remote_link = "mongodb://" + remote_db + ":27017/"
    my_client = pymongo.MongoClient(remote_link)
    try:
        info = my_client.server_info()  # Forces a call.
        print("Success in accessing the database")
    except ServerSelectionTimeoutError:
        print("server is down.")
        return
    my_db=my_client.get_database('Twitter_News')
    all_table = my_db.list_collection_names()
    #on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
    if ('system.indexes' in all_table):
        all_table.remove('system.indexes')
    for each_table in all_table:
        my_tb=my_db[each_table]
        my_tb.create_index([('text', TEXT)])
        my_tb.create_index([('time', pymongo.ASCENDING)])
if __name__=='__main__':
    main()
