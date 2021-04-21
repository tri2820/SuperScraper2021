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

        table_column_values = list(super_fund['super_offerings'].columns)

        for table_column_value in table_column_values:

            offering = self.check_for_offering_exist(super_fund, table_column_value, True)

            if offering == None:
                offering = self.create_new_offering(super_fund, table_column_value)
                if offering == None:
                    continue
                # --
            # --

            query = {'_id' : offering['_id']}

            value_obj_list = []
            value_obj_dict = super_fund['super_offerings'][table_column_value].to_dict()

            # TODO: Mabye use zip, but this is fine for now
            for key in value_obj_dict:
                #print(key, value_obj_dict[key])
                # Handle value conversions and format changes
                data_value = spiderdatautils.digit_value_format(value_obj_dict[key])
                # Apply lamda if needed
                if 'value_mutator' in super_fund:
                    data_value = super_fund['value_mutator'](data_value)
                # --
                value_object = {'Date' : key, 'Value' : data_value}
                value_obj_list.append(value_object)
            # --

            values = {'$addToSet': {super_fund['insert_cat'] : {'$each': value_obj_list}}}
            self.db[self.collection_name].update_many(query, values)

        # ---

        return item
    # --

    def check_offering(self, super_fund, table_column_value, offering_query):
        #offering_query = {'metadata.table_strings' : table_column_value}
        offering = self.db[self.collection_name].find_one(offering_query)
        # Ensure that this offering data is of the correct super fund
        if offering == None:
            return None
        if super_fund['_id'] != offering['fund_id']:
            return None
        return offering


    def check_for_offering_exist(self, super_fund, table_column_value, add_to_table = False):

        # Check if offering already exists using metadata table string
        offering_query = {'metadata.table_strings' : table_column_value}
        offering = self.check_offering(super_fund, table_column_value, offering_query)

        # Return offering if exists
        if offering != None:
            return offering

        # Check if offering of same id type already exists
        offering_id = super_fund['_id'] + '_' + table_column_value
        offering_id = spiderdatautils.lower_underscore(offering_id)

        offering_query = {'_id' : offering_id}
        offering = self.check_offering(super_fund, table_column_value, offering_query)
        #offering = self.db[self.collection_name].find_one(offering_query)

        if offering == None:
            return None
        else:
            # Ensure that this offering data is of the correct super fund
            #if super_fund['_id'] != offering['fund_id']:
            #    return None
            # If add_to_table, add string if offer exists
            if add_to_table:
                query = {'_id' : offering['_id']}
                values = {'$addToSet': {'metadata.table_strings' : {'$each': [offering_id]}}}
                self.db[self.collection_name].update_many(query, values)
            return offering
    # --


    def create_new_offering(self, super_fund, table_column_value):
        offering_id = super_fund['_id'] + '_' + table_column_value
        offering_id = spiderdatautils.lower_underscore(offering_id)
        new_offering = {
            '_id': offering_id,
            'fund_id': super_fund['_id'],
            'name': table_column_value,
            'monthly_performances': [],
            'historial_performances': [],
            'inception': 'N/A',
            'metadata': {'table_strings': [table_column_value]}
            }
        self.db[self.collection_name].insert_one(new_offering)
        offering_query = {'_id' : new_offering['_id']}
        queried_offering = self.check_offering(super_fund, table_column_value, offering_query)
        return queried_offering
    # --



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
