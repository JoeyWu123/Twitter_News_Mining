import pymongo
from pymongo.errors import ServerSelectionTimeoutError
def main():
    remote_db_to_backup=input("Input the IP address of your database to back up: ")
    remote_link="mongodb://"+remote_db_to_backup+":27017/"
    my_remote_client = pymongo.MongoClient(remote_link)
    try:
        info = my_remote_client.server_info()  # Forces a call.
        print("Success in accessing the database")
    except ServerSelectionTimeoutError:
        print("server is down.")
        return
    backup_db = input("Input the IP address of your backup database: ")
    backup_link = "mongodb://" + backup_db + ":27017/"
    backup_client=pymongo.MongoClient(backup_link)
    try:
        info = backup_client.server_info()  # Forces a call.
        print("Success in accessing the database")
    except ServerSelectionTimeoutError:
        print("server is down.")
        return
    choice=input("You are going to copy "+remote_db_to_backup+" to "+backup_db+"; input y to confirm: ")
    if(choice!='y'):
        print("Program ends")
        return
    back_up_db=backup_client.get_database('Twitter_News')
    remote_db=my_remote_client.get_database('Twitter_News')
    #delete unmatched rows in db of backup
    all_backup_table = back_up_db.list_collection_names()
    # on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
    if ('system.indexes' in all_backup_table):
        all_backup_table.remove('system.indexes')
    for each_table in all_backup_table:
        current_backup_table=back_up_db[each_table]
        current_remote_table=remote_db[each_table]
        search_result=current_backup_table.find({})
        for each_row in search_result:
            row_id=each_row['_id']
            if(current_remote_table.count_documents({"_id": row_id}) == 0):
                current_backup_table.delete_one({"_id":row_id})
    #get new rows from db to back up
    all_remote_table=remote_db.list_collection_names()
    if ('system.indexes' in all_remote_table):
        all_remote_table.remove('system.indexes')
    for each_table in all_remote_table:
        current_backup_table=back_up_db[each_table]
        current_remote_table=remote_db[each_table]
        search_result = current_remote_table.find({})
        for each_row in search_result:
            row_id = each_row['_id']
            current_backup_table.update_one({"_id":row_id}, {"$set": each_row}, upsert=True)
    print("Done")

if __name__=='__main__':
    main()
