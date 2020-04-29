import pymongo
from pymongo.errors import ServerSelectionTimeoutError
from text_processor import*
def main():
    choice=eval(input("Input 1 to delete the field;Input 2 to update the rows without field tokenized_text;\
Input 3 to delete the rows whose text is only a link: "))
    if(choice==1):
        db_add=input("Input the IP address of your database: ")
        link="mongodb://"+db_add+":27017/"
        my_client = pymongo.MongoClient(link)
        try:
            info = my_client.server_info()  # Forces a call.
            print("Success in accessing the database")
        except ServerSelectionTimeoutError:
            print("server is down.")
            return
        my_db=my_client.get_database('Twitter_News')
        all_table = my_db.list_collection_names()
        # on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
        if ('system.indexes' in all_table):
            all_table.remove('system.indexes')
        field=input("Input the field name to delete: ")
        for each_table in all_table:
            my_tb=my_db[each_table]
            my_tb.update_many({},{"$unset":{field:""}})
    if(choice==2):
        db_add=input("Input the IP address of your database: ")
        link="mongodb://"+db_add+":27017/"
        my_client = pymongo.MongoClient(link)
        try:
            info = my_client.server_info()  # Forces a call.
            print("Success in accessing the database")
        except ServerSelectionTimeoutError:
            print("server is down.")
            return
        my_db=my_client.get_database('Twitter_News')
        all_table = my_db.list_collection_names()
        # on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
        if ('system.indexes' in all_table):
            all_table.remove('system.indexes')
        for each_table in all_table:
            my_tb=my_db[each_table]
            rows=my_tb.find({"tokenized_text":None})
            for each_row in rows:
                to_write=processText(each_row['text'])
                id_get=each_row['_id']
                my_tb.update_one({"_id":id_get},{"$set":{"tokenized_text": to_write}})
    if(choice==3):
        db_add=input("Input the IP address of your database: ")
        link="mongodb://"+db_add+":27017/"
        my_client = pymongo.MongoClient(link)
        my_db=my_client.get_database('Twitter_News')
        all_table = my_db.list_collection_names()
        # on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
        if ('system.indexes' in all_table):
            all_table.remove('system.indexes')
        for each_table in all_table:
            my_tb=my_db[each_table]
            rows=my_tb.find({"tokenized_text":[]})
            for each_row in rows:
                row_id=each_row['_id']
                my_tb.delete_one({"_id": row_id})
if __name__=="__main__":
    main()
