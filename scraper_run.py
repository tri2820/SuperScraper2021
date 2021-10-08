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

import argparse

import ssl
# Detect OS
import os
import platform





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

# UNGO23
DENY_EXTENSIONS = configure_extension_requests(DENY_EXTENSIONS,['pdf'],[])#'html'



def system_type():

    system_name = platform.system()

    print(f" System detected as {system_name}")
    return system_name
# --

def set_chrome_driver_path():
    chrome_driver_path_ = "install/chrome_driver/chromedriver"
    system_name = system_type()
    if system_name == "Windows":
        chrome_driver_path_ += ".exe"
    return chrome_driver_path_
# --


CHROME_DRIVER_PATH = set_chrome_driver_path()


class DatabaseHandler:

    collection_name = 'funds'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db


    def open_connection(self):
        self.client = pymongo.MongoClient(self.mongo_uri, ssl=True,ssl_cert_reqs=ssl.CERT_NONE)#, ssl=True,ssl_cert_reqs=ssl.CERT_NONE
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
        #print(type(collection_name_))
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

    #configure_logging()

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
        '''
        if not 'schedule_data' in traversal_document:
            traversal_document['schedule_data'] = {
                "last_traversed": 0,
                "should_traverse": True
            }
        traversal_document['schedule_data'] = {
            "last_traversed": 0,
            "should_traverse": True
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
        '''

        if not 'filtered_file_urls' in traversal_document:
            traversal_document['filtered_file_urls'] = {
                "PDS": [],
                "Investment": [],
                "Performance": [],
                "FactSheet": [],
                "FeesCosts": [],
                "Report": []
            }
        
        print(traversal_document['schedule_data']['should_traverse'])

        if traversal_document['schedule_data']['should_traverse'] == "False":
            traversal_document['schedule_data']['should_traverse'] = False
        
        if traversal_document['schedule_data']['should_traverse'] == "True":
            traversal_document['schedule_data']['should_traverse'] = True

        test_handler.find_or_create_document('site_traverse_data',traversal_document, True)

        if traversal_document['schedule_data']['should_traverse'] == "False" or traversal_document['schedule_data']['should_traverse'] == False:
            continue

        #test_handler.find_or_create_document('site_traverse_data',traversal_document, True)

        traversal_document = test_handler.find_or_create_document('site_traverse_data', {'_id': trav_id}, False)
        traversal_documents.append(traversal_document)
    # --
    test_handler.close_connection()

    print("Start Crawl")
    print('tav no. ', len(traversal_documents))

    #return scipy==1.7.1

    '''
    # Sequential
    @defer.inlineCallbacks
    def crawl():

        print("---")

        #document = test_handler.find_or_create_document('site_traverse_data', {'_id': "novaport_site_traversal"}, False)
        #yield runner.crawl('Traversal', traverse_data = document)
        for document in traversal_documents:
            try:
                if document['schedule_data']['should_traverse']:
                    print('CRAWLING - ',document['_id'])
                    yield runner.crawl('Traversal', traverse_data = document)
            except:
                print('\n\n\n\n\n\n\n\n\n\n------------------- A-SPIDER-FAILED -------------------\n\n\n\n\n\n\n\n\n\n')

        reactor.stop()
    # --

    '''
    '''

    #traversal_documents = [traversal_documents[1]]

    # Parrallal
    for document in traversal_documents:
        if document['schedule_data']['should_traverse']:
            print('CRAWLING - ',document['_id'])
            runner.crawl('Traversal', traverse_data = document)
    # --

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    #'''

    # RUN 10 AT A TIME
    print(" crawl ")

    @defer.inlineCallbacks
    def crawl():

        print("---")
        max_parallel = 10
        cur_parallel = 0


        for document in traversal_documents:
            if document['schedule_data']['should_traverse']:
                cur_parallel += 1
                if cur_parallel >= max_parallel:
                    d = runner.join()
                    d.addBoth(lambda _: reactor.stop())
                    cur_parallel = 0
                    #reactor.run()
                    yield runner.crawl('Traversal', traverse_data = document)
                else:
                    runner.crawl('Traversal', traverse_data = document)

        #reactor.run()
        #reactor.stop()
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
    # --

    crawl()
    reactor.run()

    print("Crawl Completed")
# --



from Scraper.DocHanding import Something


def showcase(fund_id = "CSA0038AU"):
    new_something = Something()
    print("FINDING FILE ITEMS")
    new_something.find_item_file_urls('fund_managers', fund_id)
    print("\n-----\n")
    print('DATA EXTRACTION')
    new_something.extract_data_from_documents('fund_managers', fund_id)
    return


def populate_funds():
    dbHandler = DatabaseHandler(MONGO_URI, MONGO_DB)
    dbHandler.open_connection()

    fund_managers_ids = dbHandler.get_collection_ids('fund_managers')
    site_traverse_data_ids = dbHandler.get_collection_ids('site_traverse_data')

    for site_id in site_traverse_data_ids:
        traversal_obj = dbHandler.find_or_create_document('site_traverse_data', {'_id': site_id}, False)
        if not traversal_obj:
            continue
        page_filters = traversal_obj['domain']['page_filters']
        for page_filter in page_filters:
            new_manager = {
                '_id': page_filter,
                'name': 'N/A',
                'APIR_code': page_filter,
                'metadata': {
                    'site_traversal_id': traversal_obj['_id'],
                    "pdf_url": None,
                    "pdf_url_list": []
                },
                "data": {
                    "_c": {},
                    "_values": []
                }
            }
            new_manager = dbHandler.find_or_create_document('fund_managers', new_manager, overwrite=False)
    # --
    dbHandler.close_connection()



def main(options):
    if options.pop_funds:
        populate_funds()
    if options.run_webtrav:
        run_scraper_traversal()
    
    if options.showcase:
        showcase()
    else:
        new_something = Something()
        if options.run_funds_file_check:
            new_something.find_item_file_urls()
        if options.run_funds_file_extract:
            new_something.extract_data_from_documents()
    
    if options.reset_webtrav:
        print("Next web traversal will rescrape all websites")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_webtrav", type=bool, default=True, help="Should run website traversal")
    parser.add_argument("--run_funds_file_check", type=bool, default=True, help="Seach file urls for each fund")
    parser.add_argument("--run_funds_file_extract", type=bool, default=True, help="Extract data from pdfs")
    parser.add_argument("--pop_funds", type=bool, default=False, help="Populate new funds")
    parser.add_argument("--run_super", type=bool, default=False, help="Run old site data extraction")
    parser.add_argument("--showcase", type=bool, default=False, help="Showcase mode")


    parser.add_argument("--reset_webtrav", type=bool, default=False, help="Set schedule data to run again")
    parser.add_argument("--reset_funds_data", type=bool, default=False, help="Clear out the collected data from all funds_manager objects")
    parser.add_argument("--reset_funds_file_urls", type=bool, default=False, help="Clear out the file urls for all funds_manager objects")


    options = parser.parse_args()
    main(options)




# pip install pyyaml




# --
