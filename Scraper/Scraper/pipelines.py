# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


'''
# Refactor the pipline

'''


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging
import pandas as pd

import numpy as np

from collections import defaultdict

from Scraper import spiderdatautils


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

        super_fund = ItemAdapter(item)

        # NOTE: There is probably a better way to do this, however that is something that can be done in a future refactor

        # TODO: (Maybe) Loop through all fields in superfund item and if they are not there set them to None

        # Handles changing indecies
        if super_fund['format_time']:
            if 'year_value' in super_fund:
                super_fund['super_offerings'].set_index(pd.Index(spiderdatautils.month_format(list(super_fund['super_offerings'].index), year_value = super_fund['year_value'])),inplace=True)
            else:
                super_fund['super_offerings'].set_index(pd.Index(spiderdatautils.month_format(list(super_fund['super_offerings'].index), parse_order = 'DMY')),inplace=True)
        # --

        print(super_fund['super_offerings'])

        table_string_values = list(super_fund['super_offerings'].columns)

        for table_string_value in table_string_values:
            offering_query = {'metadata.table_strings' : table_string_value}

            offering = self.db[self.collection_name].find_one(offering_query)

            if offering == None:
                continue

            # Ensure that this offering data is of the correct super fund
            if super_fund['_id'] != offering['fund_id']:
                print("--------",spider.name,"--------",table_string_value,"---------")
                continue

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










'''
# NOTE: I WILL CLEAN THIS UP LATER - I promise
#super_fund['super_offerings'].reindex(spiderdatautils.month_format(list(super_fund['super_offerings'].index)))
#super_fund['super_offerings'].index._data = spiderdatautils.month_format(list(super_fund['super_offerings'].tolist()))
#print(super_fund['super_offerings'])

#print(spiderdatautils.month_format(super_fund['super_offerings'].index, year_value = super_fund['year_value']))
#super_fund['super_offerings'].reindex(spiderdatautils.month_format(list(super_fund['super_offerings'].index), year_value = super_fund['year_value']))
#super_fund['super_offerings'].index._data = spiderdatautils.month_format(list(super_fund['super_offerings'].tolist()), year_value = super_fund['year_value'])
#print(super_fund['super_offerings'].reindex(spiderdatautils.month_format(list(super_fund['super_offerings'].index), year_value = super_fund['year_value'])))

'''











































# --
