import pymongo
import pandas as pd



MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"
MONGO_COLLECTIONS = ["funds","offerings"]


fields_to_empty = ['monthly_performances','historial_performances']

collection_name = 'offerings'



class DatabaseMaintenanceHandler:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db


    def open_connection(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_connection(self):
        self.client.close()

    def clear_collection(self,fields_list, collection_name):

        for field_value in fields_list:
            # If the field exists
            query = {field_value: {'$exists': True} }
            update = {'$set': {field_value : []} }
            self.db[collection_name].update_many(query,update)
# --



db_connection = DatabaseMaintenanceHandler(MONGO_URI, MONGO_DB)
db_connection.open_connection()

db_connection.clear_collection(fields_to_empty, collection_name)

db_connection.close_connection()















# plz no delete yet
'''
query = {'$or': []}
for field_value in fields_list:
    additional_field = {field_value: {'$exists': True} }
    query['$or'].append(additional_field)
# --

# Set any passed arrays to empty
update = { '$set': { '$element' : [] } }
# Filters for any fields specified in fields_list
arrayFilters = [ { 'element': { '$in': fields_list } } ]
modify = { 'query': query, 'update': update, 'arrayFilters': arrayFilters}
print(modify)
self.db[self.collection_name].find_and_modify(query = query, update = update, arrayFilters = arrayFilters)
'''






























# --
