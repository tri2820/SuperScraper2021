from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import pymongo
import logging
import pandas as pd




MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"
MONGO_COLLECTIONS = ["funds","offerings"]



class DatabaseHandler:

    collection_name = 'funds'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db


    def open_connection(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_connection(self):
        self.client.close()


    def retrieve_fund_data(self, fund_id):
        query = {'_id' : fund_id}
        #ommit = {'_id' : 0, 'metadata' : 1, 'name' : 0, 'type' : 0, 'website' : 0, 'super_performance' : 0}
        fund_data = self.db[self.collection_name].find_one(query)

        return fund_data




# data-csv-url


#'''
process = CrawlerProcess(get_project_settings())

db_connection = DatabaseHandler(MONGO_URI, MONGO_DB)
db_connection.open_connection()
hesta_fund_data = db_connection.retrieve_fund_data("hesta")
aware_fund_data = db_connection.retrieve_fund_data("aware")
telstra_fund_data = db_connection.retrieve_fund_data("telstra")
db_connection.close_connection()

process.crawl('Aware', fund_data = aware_fund_data)

#process.crawl('Telstra', fund_data = telstra_fund_data)

#process.crawl('Hesta', fund_data = hesta_fund_data)

process.start()
#'''

print("Crawl Completed")















































# --
