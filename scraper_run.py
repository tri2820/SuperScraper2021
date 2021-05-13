#from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


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

        configure_logging()

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

#spider = SpiderHandler()
#print(spider.fund_data_list)
#spider.run_scraper()


# #run_scraper()
# #def run_scraper():
#     #'''

#     db_connection = DatabaseHandler(MONGO_URI, MONGO_DB)
#     db_connection.open_connection()
#     hesta_fund_data = db_connection.retrieve_fund_data("hesta")
#     telstra_fund_data = db_connection.retrieve_fund_data("telstra")
#     future_fund_data = db_connection.retrieve_fund_data("future")
#     aware_fund_data = db_connection.retrieve_fund_data("aware")
#     db_connection.close_connection()


#     configure_logging()

#     #process = CrawlerProcess(get_project_settings())#get_project_settings()#{'SPIDER_MODULES': 'Scraper.Scraper.spiders'}
#     runner = CrawlerRunner(get_project_settings())

#     @defer.inlineCallbacks
#     def crawl():

#         yield runner.crawl('Aware', fund_data = aware_fund_data)

#         yield runner.crawl('Hesta', fund_data = hesta_fund_data)

#         yield runner.crawl('Telstra', fund_data = telstra_fund_data)

#         yield runner.crawl('Future', fund_data = future_fund_data)

#         reactor.stop()a


def run_scraper_traversal():

    configure_logging()

    runner = CrawlerRunner(get_project_settings())


    @defer.inlineCallbacks
    def crawl():

        traverse_data_1 = {
            '_id': 'pendal_site_traversal',
            'file_extraction_rules': {
                'allow': [
                    '.+\.pdf.+',
                    '.+\.pdf',
                ],
                'filters': [
                    '.+product.disclosure.statement.+',
                    '.+pds.+',
                    '.+PDS.+',
                ]
            },
            'domain': {
                'domain_file': 'pendal',
                'domain_name': 'www.pendalgroup.com',
                'start_url': 'https://www.pendalgroup.com/',
                'parse_select':'traverse',
                'page_filters': {
                    'RFA0059AU': ['RFA0059AU'],
                    'BTA0061AU': ['BTA0061AU'],
                    'WFS0377AU': ['WFS0377AU'],
                },
            },
        }

        yield runner.crawl('Traversal', traverse_data = traverse_data_1)

        traverse_data_2 = {
            '_id': 'hyperion_site_traversal',
            'file_extraction_rules': {
                'allow': [
                    '.+\.pdf.+',
                    '.+\.pdf'
                ],
                'filters': [
                    '.+product.disclosure.statement.+',
                    '.+pds.+',
                    '.+PDS.+',
                ]
            },
            'domain': {
                'domain_file': 'hyperion',
                'domain_name': 'www.hyperion.com.au',
                'start_url': 'https://www.hyperion.com.au',
                'parse_select':'traverse',
                'page_filters': {
                    'BNT0003AU': ['BNT0003AU'],
                },
            },
        }

        yield runner.crawl('Traversal', traverse_data = traverse_data_2)

        reactor.stop()

    crawl()

    reactor.run()

    print("Crawl Completed")
# --

run_scraper_traversal()

#run_scraper()

#     print("Crawl Completed")






'''
fund_test_obj = {
    '_id': 'RFA0059AU',
    'name': 'Pendal Focus Australian Share Fund',
    'APIR_code': 'RFA0059AU',
    'metadata': {
        'site_traversal_id': 'trav',
        'pdf_url': 'uehfaouefu.pdf',
    },
}
'''



'''
traverse_data = {
    '_id': 'trav',
    'file_extraction_rules': {
        'allow': [
            '.+\.pdf.+',#.+\.pdf
            '.+\.pdf',
        ],
        'filters': [
            '.+product.disclosure.statement.+',#%
            '.+pds.+',
            '.+PDS.+',
        ]
    },
    'domain': {
        'domain_file': 'pendal',
        'domain_name': 'www.pendalgroup.com',
        'start_url': 'https://www.pendalgroup.com/',
        'parse_select':'traverse',
        'page_filters': {
            'RFA0059AU': ['RFA0059AU'],#RFA0059AU
            'BTA0061AU': ['BTA0061AU'],#'APIR',
            'WFS0377AU': ['WFS0377AU'],
        },
    },
}
'''








'''
'domains': [
    'www.pendalgroup.com'
],
'page_filters': [
    ['RFA0818AU'],
    ['RFA0059AU'],
    ['RFA0818AU'],
    ['BNT0003AU']
]
'''

























# --
