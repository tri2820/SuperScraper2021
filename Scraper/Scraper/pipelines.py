# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging
import pandas as pd

import numpy as np

from collections import defaultdict


class ScraperPipeline:
    def process_item(self, item, spider):
        return item


# TODO: Partition database for names, id, ect .. |\ then format data

class SuperDataArange:

    def process_item(self, item, spider):
        return item
# --

# TODO: Clean data

class SuperDataClean:

    def process_item(self, item, spider):
        return item
# --




class SuperDataMongodb:#object

    collection_name = 'offerings'
    #monthly_performances
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        #self.db[self.collection_name].insert_one({'hmmmm':123})
        #self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())

        #logging.debug('--------------------------||-------------------------------')

        super_fund = ItemAdapter(item)

        table_string_values = list(super_fund['super_offerings'].columns)

        for table_string_value in table_string_values:
            #metadata.table_string
            offering_query = {'metadata.table_strings' : table_string_value}

            offering = self.db[self.collection_name].find_one(offering_query)

            #logging.debug('---------------------------------------------------------')
            #logging.debug(table_string_value)
            if offering == None:
                continue
            #logging.debug(offering)
            #logging.debug(type(offering))

            query = {'_id' : offering['_id']}

            cons_list = []
            cons_dict = super_fund['super_offerings'][table_string_value].to_dict()
            for key in cons_dict:
                value_object = {'Date' : key, 'Value' : cons_dict[key]}
                cons_list.append(value_object)
            values = {'$addToSet': {super_fund['insert_cat'] : {'$each': cons_list}}}
            self.db[self.collection_name].update_many(query, values)

        # ---

        return item
# --
















































# --
