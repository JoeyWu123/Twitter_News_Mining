import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import multiprocessing
cores = multiprocessing.cpu_count()
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
def main():
    db_add = input("Input the IP address of your database: ")
    link = "mongodb://" + db_add + ":27017/"
    my_client = pymongo.MongoClient(link)
    try:
        info = my_client.server_info()  # Forces a call.
        print("Success in accessing the database")
    except ServerSelectionTimeoutError:
        print("server is down.")
        return
    my_db = my_client.get_database('Twitter_News')
    all_table = my_db.list_collection_names()
    # on some linux machine, system.indexes may be automatically created. It depends on os and version of mongodb
    if ('system.indexes' in all_table):
        all_table.remove('system.indexes')
    all_tokenized_text=[]
    for each_table in all_table:
        my_tb = my_db[each_table]
        rows=my_tb.find({}, {"tokenized_text":1})
        for each_row in rows:
            all_tokenized_text.append(each_row['tokenized_text'])
    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(all_tokenized_text)]
    doc2vec_model = Doc2Vec(documents, vector_size=100, min_count=1, workers=cores)
    doc2vec_model.train(documents, total_examples=doc2vec_model.corpus_count, epochs=20)
    doc2vec_model.save('doc2vec_model.pickle')
    print("done")

if __name__=="__main__":
    main()