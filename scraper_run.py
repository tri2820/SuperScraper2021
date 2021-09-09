from Scraper import settings

#from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from scrapy.linkextractors import IGNORED_EXTENSIONS


import pymongo
import logging
import pandas as pd

import re



MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"
MONGO_COLLECTIONS = ["funds","offerings"]

DENY_EXTENSIONS = []



def configure_extension_requests(dny_ext,remove_extensions, add_extensions):
    dny_ext = IGNORED_EXTENSIONS.copy()
    for extension in remove_extensions:
        if extension in dny_ext:
            dny_ext.pop(dny_ext.index(extension))
    for extension in add_extensions:
        dny_ext.append(extension)
    # --
    return dny_ext
# --


DENY_EXTENSIONS = configure_extension_requests(DENY_EXTENSIONS,['pdf'],[])#'html'



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
    
    def get_collection_ids(self, collection_name_):
        ids_list = [str(x) for x in self.db[collection_name_].find().distinct('_id')]
        return ids_list


# data-csv-url


# spider handler class
class SpiderHandler:
    fund_data_list = ["hesta", "telstra","future", "aware"]
    spider_crawl_list = ['Hesta','Telstra', 'Future', 'Aware']

    def run_scraper(self):
        db_connection = DatabaseHandler(MONGO_URI, MONGO_DB)
        db_connection.open_connection()
        fund_datas = []
        for i in range(len(self.fund_data_list)):
            fund_datas.append(db_connection.retrieve_fund_data(self.fund_data_list[i]))
        db_connection.close_connection()

        #configure_logging()

        #process = CrawlerProcess(get_project_settings())#get_project_settings()#{'SPIDER_MODULES': 'Scraper.Scraper.spiders'}
        runner = CrawlerRunner(get_project_settings())

        @defer.inlineCallbacks
        def crawl():
            for i in range(len(fund_datas)):
                yield runner.crawl(self.spider_crawl_list[i], fund_data = fund_datas[i])
            reactor.stop()

        crawl()

        reactor.run()

        print("Crawl Completed")
# --






"""
example_traversal_document = {
    '_id': 'hyperion_site_traversal',
    'file_extraction_rules': {
        # Only allows certain file types
        'deny_extensions': DENY_EXTENSIONS,
        # Regex that the url must match during extraction
        'allow': [
            #'.+\.pdf.+',
            #'.+\.pdf'
        ],
        # Page content types that must apply for file type urls
        'content_types': [
            "application/pdf"
        ],
    },
    "file_filters": {
        "PDS": {
            # The following are now pipeline filters (after extraction)
            # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
            'restrict_text': [
            '.+product.disclosure.statement.+',
            '.+pds.+',
            '.+PDS.+',
            ],
            # Filters applied to urls after extraction and before entering into DB
            'filters': [
                '.+product.disclosure.statement.+',
                '.+pds.+',
                '.+PDS.+',
            ]
        }
    },
    "traversal_filters": {
    },
    'domain': {
        'domain_file': 'hyperion',
        'domain_name': 'www.hyperion.com.au',
        'start_url': 'https://www.hyperion.com.au',
        'parse_select':'traverse',
        # All of the strings in the list of each item must be found for this to be added as filtered page
        'page_filters': {
            'BNT0003AU': ['BNT0003AU'],
        },
    },
    "filtered_file_urls": {

    },
    "schedule_data" = {
        "last_traversed": 0,
        "should_traverse": False,
    }
}
#"""


"""
# EXAMPLE OF filtered_traverse_urls:
"filtered_traverse_urls": {
    "VAN0002AU": {
        "name": "VAN0002AU",
        "url": "https://www.vanguard.com.au/personal/home/en",
        "page_filter": [
        "VAN0002AU"
        ],
        "file_urls": [
        "https://www.vanguard.com.au/personal/en/open-an-account",
        "https://www.vanguard.com.au/personal/vanguardonline"
        ]
    }
},

"""

#novaport_site_traversal



def run_scraper_traversal():

    configure_logging()

    runner = CrawlerRunner(get_project_settings())

    test_handler = DatabaseHandler(MONGO_URI, MONGO_DB)

    test_handler.open_connection()
    traversal_ids = test_handler.get_collection_ids('site_traverse_data')

    traversal_documents = []

    prog_count = 0

    for trav_id in traversal_ids:
        print(prog_count)
        prog_count += 1
        traversal_document = test_handler.find_or_create_document('site_traverse_data', {'_id': trav_id}, False)
        if not 'schedule_data' in traversal_document:
            traversal_document['schedule_data'] = {
                "last_traversed": 0,
                "should_traverse": False
            }
        #traversal_document['filtered_file_urls']['FeesCosts'] = {}
        #if 'filtered_file_urls' in traversal_document:
            #if 'Fees&Costs' in traversal_document['filtered_file_urls']:
            #    traversal_document['filtered_file_urls']['FeesCosts'] = traversal_document['filtered_file_urls'].pop('Fees&Costs', [])
            #if not 'Report' in traversal_document['filtered_file_urls']:
            #    traversal_document['filtered_file_urls']['Report'] = []
        # traversal_document['schedule_data']['should_traverse'] = True
        #traversal_document['schedule_data']['should_traverse'] = True

        if traversal_document['schedule_data']['should_traverse'] == "False" or traversal_document['schedule_data']['should_traverse'] == False:
            continue

        #traversal_document['schedule_data']['should_traverse'] = True
        # Fix domain slash issue
        domain_string = traversal_document['domain']['domain_name']
        if domain_string[-1] == "/":
            traversal_document['domain']['domain_name'] = domain_string[:-1]
        traversal_document["file_filters"] = {
            "PDS": {
                # The following are now pipeline filters (after extraction)
                # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
                'restrict_text': [
                    '.+product.disclosure.statement.+',
                    '.+pds.+',
                    '.+PDS.+',
                ],
                # Filters applied to urls after extraction and before entering into DB
                'filters': [
                    '.+product.disclosure.statement.+',
                    '.+pds.+',
                    '.+PDS.+',
                ]
            },
            "Investment": {
                # The following are now pipeline filters (after extraction)
                # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
                'restrict_text': [
                    '.+Investment.+',
                    '.+investment.+',
                ],
                # Filters applied to urls after extraction and before entering into DB
                'filters': [
                    '.+Investment.+',
                    '.+investment.+',
                ]
            },
            "FeesCosts": {
                # The following are now pipeline filters (after extraction)
                # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
                'restrict_text': [
                    '.+fees.costs.+',
                    '.+Fees.Costs.+',
                    '.+fees.+',
                    '.+costs.+',
                ],
                # Filters applied to urls after extraction and before entering into DB
                'filters': [
                    '.+fees.costs.+',
                    '.+Fees.Costs.+',
                    '.+fees.+',
                    '.+costs.+',
                ]
            },
            "Performance": {
                # The following are now pipeline filters (after extraction)
                # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
                'restrict_text': [
                    '.+performance.+',
                    '.+Performance.+',
                ],
                # Filters applied to urls after extraction and before entering into DB
                'filters': [
                    '.+performance.+',
                    '.+Performance.+',
                ]
            },
            "FactSheet": {
                # The following are now pipeline filters (after extraction)
                # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
                'restrict_text': [
                    '.+FactSheet.+',
                    '.+Fact Sheet.+',
                    '.+fact.sheet.+',
                    '.+fact.+',
                ],
                # Filters applied to urls after extraction and before entering into DB
                'filters': [
                    '.+FactSheet.+',
                    '.+Fact Sheet.+',
                    '.+fact.sheet.+',
                    '.+fact.+',

                ]
            },
            "Report": {
                # The following are now pipeline filters (after extraction)
                # Regex that the text in the </a> anchor can match (this accounts for urls that say nothing)
                'restrict_text': [
                    '.+Report.+',
                    '.+report.+',
                    '.+FR.+',
                    '.+fr.+',
                ],
                # Filters applied to urls after extraction and before entering into DB
                'filters': [
                    '.+Report.+',
                    '.+report.+',
                    '.+FR.+',
                    '.+fr.+',
                ]
            },
        }
        #"""
        test_handler.find_or_create_document('site_traverse_data',traversal_document, True)

        traversal_document = test_handler.find_or_create_document('site_traverse_data', {'_id': trav_id}, False)
        traversal_documents.append(traversal_document)
    # --
    test_handler.close_connection()

    print("Start Crawl")
    print('tav no. ', len(traversal_documents))

    #return

    # Sequential
    @defer.inlineCallbacks
    def crawl():

        print("---")

        #document = test_handler.find_or_create_document('site_traverse_data', {'_id': "novaport_site_traversal"}, False)
        #yield runner.crawl('Traversal', traverse_data = document)
        for document in traversal_documents:
            if document['schedule_data']['should_traverse']:
                print('CRAWLING - ',document['_id'])
                yield runner.crawl('Traversal', traverse_data = document)

        reactor.stop()
    # --

    '''
    # Parrallal
    for document in traversal_documents:
        if document['schedule_data']['should_traverse']:
            print('CRAWLING - ',document['_id'])
            runner.crawl('Traversal', traverse_data = document)
    # --

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    '''

    crawl()

    reactor.run()

    print("Crawl Completed")
# --

#print(DENY_EXTENSIONS)

#run_scraper_traversal()

#new_trav = SpiderHandler()

#new_trav.run_scraper()

#run_scraper()

#     print("Crawl Completed")


from Scraper.DocHanding import Something

new_something = Something()

new_something.extract_data_from_documents('fund_managers',"CSA0038AU")#CSA0038AU #BFL0004AU

#new_something.find_item_file_urls()
#new_something.extract_data_from_documents()

#new_something.extract_data_from_documents()
















# --
