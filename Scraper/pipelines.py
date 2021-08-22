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

from requests.api import request

from Scraper import spiderdatautils

import re

import json
import csv

from Scraper.spiderdatautils import requests_session_handler



'''
SuperDataClean

This is the class that cleans and formats data.

 --- process_item ---
Function that peforms cleaning and formating logic

Parameters:
 - item[object(dict-like)]: object that contains scraped data and cleaning and formatting metadata (Refer to 'items.py').
 - spider[scrapy spider]: contains spider metadata and functions

'''


# TODO: Clean data
class SuperDataClean:

    def process_item(self, item, spider):

        super_fund = item

        # If supplied sets the names for the values that will be stored in the database
        value_object_keys = ['Date','Value']
        if 'value_object_keys' in super_fund:
            value_object_keys = super_fund['value_object_keys']
        # --

        # Handles changing indecies
        if 'format_time' in super_fund:
            if super_fund['format_time']:
                if 'year_value' in super_fund:
                    super_fund['scraped_data'].set_index(pd.Index(spiderdatautils.month_format(list(super_fund['scraped_data'].index), year_value = super_fund['year_value'])),inplace=True)
                else:
                    super_fund['scraped_data'].set_index(pd.Index(spiderdatautils.month_format(list(super_fund['scraped_data'].index), parse_order = 'DMY')),inplace=True)
        # --

        # Go through all data columns and fomat values for use
        value_obj_lists = {}
        table_column_values = list(super_fund['scraped_data'].columns)
        for table_column_value in table_column_values:

            value_obj_list = []
            value_obj_dict = super_fund['scraped_data'][table_column_value].to_dict()

            for key in value_obj_dict:
                # Handle value conversions and format changes
                data_value = spiderdatautils.digit_value_format(value_obj_dict[key])
                # Apply lamda if needed
                if 'value_mutator' in super_fund:
                    data_value = super_fund['value_mutator'](data_value)
                # --
                # The data object that consists of names for the values that will be stored in the database with corrisponding values
                value_object = {value_object_keys[0] : key, value_object_keys[1] : data_value}
                value_obj_list.append(value_object)
            # --
            value_obj_lists[table_column_value] = value_obj_list
        # --
        super_fund['value_objects'] = value_obj_lists


        return super_fund
    # --
# --


'''
SuperDataMongodb

Class Varaibles:
 - collection_name[string]: the name of the collection we are putting data in (this is kind of temperery, fixing this stuff up is not a prority rn)

This class handles querying database about scraped data and uploading to database.

 --- __init__ ---
Sets up database connection variables.

 --- from_crawler ---
Sets the values of database connection variables,

 --- open_spider ---
 Opens connection to database

 --- close_spider ---
 Closes connection to database

 --- process_item ---

Parameters:
 - item[object(dict-like)]: object that contains scraped data and cleaning and formatting metadata (Refer to 'items.py').
 - spider[scrapy spider]: contains spider metadata and functions



 --- check_offering ---

Given a query, check to see if an item exists and if it does return it

Parameters:
 - super_fund[object(dict-like)]: object that contains scraped data and cleaning and formatting metadata (Refer to 'items.py').
 - offering_query[object(dict-like)]: object that contains a database query that is to run.

 --- check_for_offering_exist ---

Checks to see if the metadata id specifier for this scraped data exists, if i does then return the document.
If it does not it uses the name scraped from the data tables to guess what the id for a similar document might be and find it, lf found it adds the name for this data to the documents metadata for next time and returns the document.

Parameters:
 - super_fund[object(dict-like)]: object that contains scraped data and cleaning and formatting metadata (Refer to 'items.py').
 - table_column_value[string]: a string recived from scraping that is used to check database metadata to see if a document exists for the corisponding data (eg: a specific offering)
 - add_to_table[boolean]: a boolean that determins if this data should be added to a document if it turns out they are the same.

 --- create_new_offering ---

Creates a new document, this document is empty.
The id for the document is generated using the superfund metadata id and the 'table_column_value' derived from scraped data.

Parameters:
 - super_fund[object(dict-like)]: object that contains scraped data and cleaning and formatting metadata (Refer to 'items.py').
 - table_column_value[string]: a string recived from scraping that is used to create the id for the new document it creates.

'''

class SuperDataMongodb:

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

        #value_object_keys = ['Date','Value']
        #if 'value_object_keys' in super_fund:
        #    value_object_keys = super_fund['value_object_keys']

        # TODO: (Maybe) Loop through all fields in superfund item and if they are not there set them to None

        table_column_values = list(super_fund['scraped_data'].columns)
        for table_column_value in table_column_values:
            add_new = False
            if 'add_new' in super_fund:
                add_new = True
            # --
            offering = self.check_for_offering_exist(super_fund, table_column_value, add_new)
            if offering == None:
                offering = self.create_new_offering(super_fund, table_column_value)
                if offering == None:
                    continue
                # --
            # --

            query = {'_id' : offering['_id']}
            values = {'$addToSet': {super_fund['insert_cat'] : {'$each': super_fund['value_objects'][table_column_value]}}}
            self.db[self.collection_name].update_many(query, values)

        # ---

        return item
    # --

    def check_offering(self, super_fund, offering_query):#table_column_value
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
        offering = self.check_offering(super_fund, offering_query)

        # Return offering if exists
        if offering != None:
            return offering

        # Check if offering of same id type already exists
        offering_id = super_fund['_id'] + '_' + table_column_value
        offering_id = spiderdatautils.lower_underscore(offering_id)

        offering_query = {'_id' : offering_id}
        offering = self.check_offering(super_fund, offering_query)
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
            'costs_fees': [],
            'allocations': [],
            'inception': 'N/A',
            'metadata': {'table_strings': [table_column_value]}
            }
        self.db[self.collection_name].insert_one(new_offering)
        offering_query = {'_id' : new_offering['_id']}
        queried_offering = self.check_offering(super_fund, offering_query)
        return queried_offering
    # --



# --



class SiteTraversalCSV:

    #file_name = 'pendal'

    def process_item(self, item, spider):
        traverse_item = ItemAdapter(item)
        return item
    # --

    def close_spider(self, spider):
        print('*!)$&*#&$)&* CLOSE SPIDER!')
        with open(spider.domain['domain_file'] + '_traversed_urls.csv', 'w') as fp:
            data_writer = csv.writer(fp)
            for link in spider.traversed_urls:
                data_writer.writerow([link])
        # --

        session_handler = requests_session_handler()

        file_urls = {}

        for key in spider.file_urls:
            obj = spider.file_urls[key]
            content_type = session_handler.check_content_type(obj.url)
            for re_content_match in spider.file_extraction['content_types']:
                if content_type:
                    if re.match(content_type,re_content_match):
                        file_urls[obj.url] = obj
                        break

        with open(spider.domain['domain_file'] + '_file_urls.csv', 'w') as fp:
            data_writer = csv.writer(fp)
            for link_string in file_urls:#spider.file_urls:
                #link_obj = #spider.file_urls[link_string]
                data_writer.writerow([link_string])

        with open(spider.domain['domain_file'] + '_filtered_pages.csv', 'w') as fp:
            data_writer = csv.writer(fp)
            for obj in spider.filtered_pages:
                #print(spider.filtered_pages[obj].values())
                data_writer.writerow(spider.filtered_pages[obj].values())
        # --

        filtered_file_urls = {}
        for key in file_urls:
            obj = file_urls[key]
            for filter in spider.file_extraction['filters']:
                match = re.match(filter, obj.url)
                if match != None:
                    filtered_file_urls[obj.url] = obj.url
                    break
            for restrict_text in spider.file_extraction['restrict_text']:
                if obj.text and len(obj.text) > 0:
                    match = re.match(restrict_text, obj.text)
                    if match != None:
                        filtered_file_urls[obj.url] = obj.url
                        break
        # --

        with open(spider.domain['domain_file'] + '_filtered_file_urls.csv', 'w') as fp:
            data_writer = csv.writer(fp)
            for obj in filtered_file_urls:
                data_writer.writerow([filtered_file_urls[obj]])
        # --

        session_handler.close_session()
    # --
# --


class SiteTraversalDB:

    collection_name = 'site_traverse_data'

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

    def process_item(self, item, spider):
        traverse_item = ItemAdapter(item)
        return item

    def find_or_create_document(self, data_object, overwrite=False):
        query = {'_id' : data_object['_id']}
        document = self.db[self.collection_name].find_one(query)
        # If none create one
        if document == None:
            self.db[self.collection_name].insert_one(data_object)
            document = self.db[self.collection_name].find_one(query)
        elif overwrite == True:
            self.db[self.collection_name].update_one(query, {"$set": data_object})
        # --
        return document

    def close_spider(self, spider):#spider.traverse_data
        print('*!)$&*#&$)&* CLOSE SPIDER!')

        session_handler = requests_session_handler()

        file_urls = {}

        for key in spider.file_urls:
            obj = spider.file_urls[key]
            content_type = session_handler.check_content_type(obj[0].url)
            for re_content_match in spider.file_extraction['content_types']:
                if content_type:
                    if re.match(content_type,re_content_match):
                        file_urls[obj[0].url] = obj
                        break
        # --
        filtered_file_urls = {}

        for filtered_type_name in spider.file_filters:
            filtered_file_urls[filtered_type_name] = {}

        for key in file_urls:
            obj = file_urls[key]
            for filtered_type_name in spider.file_filters:
                filtered_type = spider.file_filters[filtered_type_name]
                for filter in filtered_type['filters']:
                    match = re.match(filter.lower(), obj[0].url.lower())
                    if match != None:
                        filtered_file_urls[filtered_type_name][obj[0].url] = obj[0].url
                        break
                for restrict_text in filtered_type['restrict_text']:
                    if obj[0].text and len(obj[0].text) > 0:
                        match = re.match(restrict_text.lower(), obj[0].text.lower())
                        if match == None:
                            match = re.match(restrict_text.lower(), obj[1].lower())
                            #print('YAYAYA: ', match == None)
                        if match != None:
                            filtered_file_urls[filtered_type_name][obj[0].url] = obj[0].url
                            break
        # --
        for filtered_type_name in spider.file_filters:
            filtered_file_urls[filtered_type_name] = list(filtered_file_urls[filtered_type_name].values())

        session_handler.close_session()

        new_document = spider.traverse_data
        new_document['traverse_urls'] = list(spider.traversed_urls.values())
        #new_document['filtered_traverse_urls'] = list(spider.filtered_pages.values())
        new_document['filtered_traverse_urls'] = spider.filtered_pages#list(spider.filtered_pages.keys())
        #new_document['file_urls'] = [x.url for x in list(spider.file_urls.values())]
        new_document['file_urls'] = [x[0].url for x in list(file_urls.values())]
        new_document['filtered_file_urls'] = filtered_file_urls#list(filtered_file_urls.values())

        document = self.find_or_create_document(new_document, True)
        traversal_urls = spider.traversed_urls.values()

        self.client.close()

        #values = {'$addToSet': {super_fund['insert_cat'] : {'$each': traversal_urls}}}
        #self.db[self.collection_name].update_many(query, values)
    # --
# --


'''
filtered_file_urls = {}
        for obj_string in spider.file_urls:
            obj = spider.file_urls[obj_string]
            for filter in spider.file_extraction['filters']:
                match = re.match(filter, obj.url)
                if match != None:
                    filtered_file_urls[obj.url] = obj.url
                    break
            for restrict_text in spider.file_extraction['restrict_text']:
                if obj.text and len(obj.text) > 0:
                    match = re.match(restrict_text, obj.text)
                    if match != None:
                        filtered_file_urls[obj.url] = obj.url
                        break
        # --
'''




'''
for obj_string in spider.file_urls:
    obj = spider.file_urls[obj_string]
    for filter in spider.file_extraction['filters']:
        match = re.match(filter, obj.url)
        if match != None:
            filtered_file_urls[obj.url] = obj.url
            break
    for restrict_text in spider.file_extraction['restrict_text']:
        #print(restrict_text, spider.file_urls[obj])
        match = re.match(restrict_text, obj.text)
        if match != None:
            #print(restrict_text, spider.file_urls[obj])
            filtered_file_urls[obj.url] = obj.url
            break
# --
'''





'''
class SuperDataMongodb:


import re


class ScraperPipeline:
    def process_item(self, item, spider):

        super_fund = ItemAdapter(item)

        value_object_keys = ['Date','Value']
        if 'value_object_keys' in super_fund:
            value_object_keys = super_fund['value_object_keys']

        # TODO: (Maybe) Loop through all fields in superfund item and if they are not there set them to None

        # Handles changing indecies
        if 'format_time' in super_fund:
            if super_fund['format_time']:
                if 'year_value' in super_fund:
                    super_fund['scraped_data'].set_index(pd.Index(spiderdatautils.month_format(list(super_fund['scraped_data'].index), year_value = super_fund['year_value'])),inplace=True)
                else:
                    super_fund['scraped_data'].set_index(pd.Index(spiderdatautils.month_format(list(super_fund['scraped_data'].index), parse_order = 'DMY')),inplace=True)
        # --
        table_column_values = list(super_fund['scraped_data'].columns)
        for table_column_value in table_column_values:
            add_new = False
            if 'add_new' in super_fund:
                add_new = True
            # --
            offering = self.check_for_offering_exist(super_fund, table_column_value, add_new)
            if offering == None:
                offering = self.create_new_offering(super_fund, table_column_value)
                if offering == None:
                    continue
                # --
            # --

            query = {'_id' : offering['_id']}

            value_obj_list = []
            value_obj_dict = super_fund['scraped_data'][table_column_value].to_dict()

            # TODO: Mabye use zip, but this is fine for now
            for key in value_obj_dict:
                # Handle value conversions and format changes
                data_value = spiderdatautils.digit_value_format(value_obj_dict[key])
                # Apply lamda if needed
                if 'value_mutator' in super_fund:
                    data_value = super_fund['value_mutator'](data_value)
                # --
                #value_object = {'Date' : key, 'Value' : data_value}
                value_object = {value_object_keys[0] : key, value_object_keys[1] : data_value}
                value_obj_list.append(value_object)
            # --
            values = {'$addToSet': {super_fund['insert_cat'] : {'$each': value_obj_list}}}
            self.db[self.collection_name].update_many(query, values)

        # ---

        return item


# --
'''



'''
class ScraperPipeline:
    def process_item(self, item, spider):
        return item




# TODO: Partition database for names, id, ect .. |\ then format data

class SuperDataArange:

    def process_item(self, item, spider):
        return item
# --
'''

























# --
