import pandas as pd
from itemadapter import ItemAdapter
import pymongo
import logging
from pdf_extraction import run_extraction


MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"



name_collection = 'fund_managers'
traversal_collection = 'site_traverse_data'

#client = None
#db = None
#mongo_uri = MONGO_URI
#mongo_db = MONGO_DB


class FundManagers:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def open_connection(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_connection(self):
        self.client.close()


    def find_or_create_document(self, collection_name_, data_object, overwrite=False):
        query = {'_id' : data_object['_id']}
        print(type(collection_name_))
        document = self.db[collection_name_].find_one(query)
        # If none create one
        if document == None:
            self.db[collection_name_].insert_one(data_object)
            document = self.db[collection_name_].find_one(query)
        elif overwrite == True:
            self.db[collection_name_].update_one(query, {"$set": data_object})
        # --
        return document



fund_manager = FundManagers(MONGO_URI, MONGO_DB)

fund_manager.open_connection()


fund_test_obj = {
    '_id': 'RFA0059AU',
    'name': 'Pendal Focus Australian Share Fund',
    'APIR_code': 'RFA0059AU',
    'metadata': {
        'site_traversal_id': 'trav',
        #'pdf_url': 'uehfaouefu.pdf',
    },
}

fund_document = fund_manager.find_or_create_document(name_collection, fund_test_obj, True)

fund_id = fund_document['_id']

site_traversal_id = fund_document['metadata']['site_traversal_id']

query = {'_id' : site_traversal_id}

traversal_document = fund_manager.db[traversal_collection].find_one(query)

filtered_file_urls = traversal_document['filtered_file_urls']

number_files = len(filtered_file_urls)

print('Number of urls to check: ', number_files)

for i in range(number_files):
    file_url = filtered_file_urls[i]
    print(f'-({i}/{number_files})- Url: {file_url}'.format())
    fee_value, investment_value = run_extraction(file_url)
    if len(fee_value) > 0 or len(investment_value) > 0:
        print('-FOUND-', fee_value, investment_value)
        break
# --


fund_manager.close_connection()



















































































# --
