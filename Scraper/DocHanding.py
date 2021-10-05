import pandas as pd
from itemadapter import ItemAdapter
import pymongo
import logging
from Scraper.pdf_extraction import StringTest, DocumentExtraction, DocumentDataExtractor
#, ExtractTableHandler, TableExtraction, TableDataExtractor

#from spiderdatautils import month_format
import dateparser

import math

import re
import ssl
import time


MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"


class DBHandler:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def open_connection(self):
        self.client = pymongo.MongoClient(self.mongo_uri, ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
        self.db = self.client[self.mongo_db]


    def close_connection(self):
        self.client.close()


    def get_collection_ids(self, collection_name_):
        ids_list = [str(x) for x in self.db[collection_name_].find().distinct('_id')]
        return ids_list


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










class DocumentHandler:

    traversal_collection = 'site_traverse_data'

    docExtractor = None


    def open_connection(self):
        self.dbHandler = DBHandler(MONGO_URI, MONGO_DB)
        self.dbHandler.open_connection()
    # --

    def close_connection(self):
        self.dbHandler.close_connection()
    # --
    

    def filter_file_urls(self, traversal_id, file_filter_catagory = 'PDS', must_contain = ["HOW0027AU"]):
        
        #document = self.dbHandler.find_or_create_document(collection_name, insert_document, False)

        #site_traversal_id = document['metadata']['site_traversal_id']
        
        traversal_document = self.dbHandler.db[self.traversal_collection].find_one({'_id' : traversal_id})

        # If not filtered file urls
        if not 'filtered_file_urls' in traversal_document:
            return []

        if not file_filter_catagory in traversal_document['filtered_file_urls']:
            print('FAIL')
            return []
        filtered_file_urls = traversal_document['filtered_file_urls'][file_filter_catagory]


        found_list = []



        #document['metadata']['pdf_url_list'] = []

        # Number of files to search
        number_files = len(filtered_file_urls)
        print('Number of urls to check: ', number_files)

        # Search through each url in the list
        for i in range(number_files):
            file_url = filtered_file_urls[i]


            string_tester = StringTest(file_url)
            string_tester.extract_text(lower=True)

            found = True

            # Must Contain
            for item in must_contain:
                found = string_tester.test_for_string(item.lower())
                if not found:
                    found = False
                    break
            # --

            print(f'-({i + 1}/{number_files})- Url: {file_url} - {found}'.format())


            if found:#26 July 2021

                # Get estimated date from the start of the document
                # TODO: Clean this data stuff up plz
                estimated_date = None
                date_query = '\d* ([jJ]an|[fF]eb|[mM]ar|[aA][ip][lr]|[mM]ay|[jJ]un|[jJ]ul|[aA]ug|[sS]ep|[oO]ct|[nN]ov|[dD]ec])\w* \d+'
                date_string_match = string_tester.test_for_string(date_query, True, 200)
                date_ = None
                epoch_time = 0
                if date_string_match:
                    date_strings = date_string_match.groups()
                    if len(date_strings) > 0:
                        date_string = date_strings[0]
                        if date_string:
                            date_ = dateparser.parse(date_string)
                            if date_:
                                estimated_date = date_.strftime('%Y-%m')
                                epoch_time = date_.timestamp()
                        # --
                    # --
                # --

                insert_object = {
                    'url': file_url,
                    'estimated_date': estimated_date,
                    'epoch_time': epoch_time,
                    'estimated_topic': file_filter_catagory
                }
                found_list.append(insert_object)
            # --
        # --
        return found_list
    

    def init_document_handler(self):
        if not self.docExtractor:
            self.docExtractor = DocumentDataExtractor()
        return

    def extract_document_data(self, url):
        if not self.docExtractor:
            self.init_document_handler()
        # --

        #self.docExtractor = DocumentDataExtractor()

        # Extract doc
        doc_extract = DocumentExtraction(url, save_iamges=False)
        doc_extract.extract_tables()

        # Add extracted doc to handler
        last_doc_idx = self.docExtractor.add_document(doc_extract)
        #last_doc_idx = len(self.docExtractor.documents) - 1
        self.docExtractor.extract_similar_rows(0.2, last_doc_idx)

        #self.docExtractor.data_to_csv(last_doc_idx)

        sorted_values = self.docExtractor.sort_as_most_similar(last_doc_idx)


        return sorted_values





class Something:

    extract_mutators = {
        'Buy/Sell spread': [
            [lambda x, obj: re.search('[\+\d.%]+ ?\/ ?\-[\d.%]+', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'Management Fee': [
            [lambda x, obj: re.search('[\d.%]+.{0,5}', x), lambda x, obj: x != None],#[\d.%]+.{0,5}p\.a
            [lambda x, obj: x.group(0)],
            [lambda x, obj: re.search('[\d]+[\.,][\d]+', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'Performance Fee': [
            [lambda x, obj: re.search('[\d.%]+.{0,5}', x), lambda x, obj: x != None],#[\d.%]+.{0,5}p\.a
            [lambda x, obj: x.group(0)],
            [lambda x, obj: re.search('[\d]+[\.,][\d]+', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'NAV': [
            [lambda x, obj: re.search('([^ \n\t\r]{0,4} {0,2}[\d]+[\d.,]+ *)(million)*(billion)*([bm])*', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],

        'Class Size': [
            [lambda x, obj: re.search('([^ \n\t\r]{0,4} {0,2}[\d]+[\d.,]+ *)(million)*(billion)*([bm])*', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'Fund Size': [
            [lambda x, obj: re.search('([^ \n\t\r]{0,4} {0,2}[\d]+[\d.,]+ *)(million)*(billion)*([bm])*', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'Strategy Size': [
            [lambda x, obj: re.search('([^ \n\t\r]{0,4} {0,2}[\d]+[\d.,]+ *)(million)*(billion)*([bm])*', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
    }

    file_filter_categories = ['PDS', 'Investment', 'FeesCosts', 'Performance', 'FactSheet', 'Report']

    docHandler = None


    def reset_document_handler(self):
        self.docHandler = DocumentHandler()
        return


    def find_item_file_urls(self, collection_id = 'fund_managers', custom_query=None):

        test_handler = DBHandler(MONGO_URI, MONGO_DB)
        test_handler.open_connection()
        fund_ids = test_handler.get_collection_ids(collection_id)

        item_querys = [[x, test_handler.find_or_create_document(collection_id, {'_id': x}, False)['metadata']['site_traversal_id']] for x in fund_ids]

        if custom_query:
            item_querys = [[custom_query,test_handler.find_or_create_document(collection_id, {'_id': custom_query}, False)['metadata']['site_traversal_id']]]

        test_handler.close_connection()
        count = 0

        #item_querys = [["HOW0027AU",test_handler.find_or_create_document(collection_id, {'_id': "HOW0027AU"}, False)['metadata']['site_traversal_id']]]

        for item_query in item_querys:
            #count += 1
            #if count < 5:
            #    continue
            try:
                item_id = item_query[0]

                traversal_id = item_query[1]

                self.reset_document_handler()

                #doctest = DocumentHandler()

                self.docHandler.open_connection()

                file_list_by_category = {}

                all_files_list = []

                #if True:
                for file_cat in self.file_filter_categories:
                    file_list = self.docHandler.filter_file_urls(traversal_id, file_cat, [item_id])
                    # Sort files
                    file_list = sorted(file_list, key=lambda item: item["epoch_time"], reverse=True)
                    # Found pdfs
                    print(f"-\nFound pdfs - {file_cat}")
                    [print(x) for x in file_list]
                    file_list_by_category[file_cat] = file_list
                    # REALLY DIRTY unduper
                    for idx, file in enumerate(file_list):
                        can_append = True
                        for all_idx, all_file in enumerate(all_files_list):
                            #print(file)
                            if file['url'] == all_file['url']:
                                can_append = False
                                break
                        if can_append:
                            all_files_list.append(file)
                    # --
                self.docHandler.close_connection()

                # Pull out
                test_handler.open_connection()
                fund = test_handler.find_or_create_document(collection_id, {'_id': item_id}, False)
                #test_handler.close_connection()

                # Sort all files list
                all_files_list = sorted(all_files_list, key=lambda item: item["epoch_time"], reverse=True)

                fund['metadata']['pdf_url_list'] = all_files_list

                #test_handler.open_connection()

                #fund['metadata']['pdf_url_list'] = []

                #return

                test_handler.find_or_create_document(collection_id, fund, True)

                #test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"metadata": 1}})
                #fund = test_handler.find_or_create_document(collection_id, {'_id': item_id}, False)
                #print(fund['metadata'])

                test_handler.close_connection()
            except:
                print(' -- ERROR -- 157838 - DocHandling - find_item_file_urls - db detection fail')
        # --
        return
    

    def extract_data_from_documents(self, collection_id = 'fund_managers', custom_query=None):

        #self.docExtractor = DocumentDataExtractor()

        # Extract doc
        #doc_extract = DocumentExtraction("https://www.benthamam.com.au/assets/fundreports/20210630-GIF-Monthly-Report.pdf", save_iamges=True)
        #doc_extract.extract_tables()

        # Add extracted doc to handler
        #last_doc_idx = self.docExtractor.add_document(doc_extract)
        #return

        test_handler = DBHandler(MONGO_URI, MONGO_DB)
        test_handler.open_connection()
        fund_ids = test_handler.get_collection_ids(collection_id)

        item_querys = [[x, test_handler.find_or_create_document(collection_id, {'_id': x}, False)['metadata']['site_traversal_id']] for x in fund_ids]

        #item_querys = [["CSA0038AU",test_handler.find_or_create_document(collection_id, {'_id': "CSA0038AU"}, False)['metadata']['site_traversal_id']]]

        if custom_query:
            item_querys = [[custom_query,test_handler.find_or_create_document(collection_id, {'_id': custom_query}, False)['metadata']['site_traversal_id']]]


        test_handler.close_connection()
        count = 0

        for item_query in item_querys:
            #count += 1
            #if count < 5:
            #    continue

            

            item_id = item_query[0]

            print(f'\n-- {item_id} --\n')

            traversal_id = item_query[1]

            self.reset_document_handler()
            
            # Pull out
            test_handler.open_connection()

            test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"data": 1}})


            item = test_handler.find_or_create_document(collection_id, {'_id': item_id}, False)
            #test_handler.close_connection()

            # Sort all files list
            #all_files_list = sorted(all_files_list, key=lambda item: item["epoch_time"], reverse=True)

            #fund['metadata']['pdf_url_list'] = all_files_list

            #item.pop("Buy/Sell spread", None)
            #item.pop("Management Fee", None)
            #item.pop("Asset Allocation", None)
            #item["data"] = {}


            #item['metadata']['pdf_url_list'] = []

            #item["data"] = {}


            item = self.extract_item_data(item)
            #test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"data": 1}})

            #test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"Buy/Sell spread":1}})
            #test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"Management Fee":1}})
            #test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"Asset Allocation":1}})

            #test_handler.db['fund_managers'].update_one({'_id' : item_id}, {"$unset": {"data": 1}})


            print_values = item['data']['_values']

            print("\n\n\n--ITEM VALUES --")
            #[print(x) for x in print_values]
            print_values_not_null = []
            for values_ in print_values:
                print('--------')
                print('url: ',values_['url'])
                print('estimated_topic: ',values_['estimated_topic'])
                for cat_name in values_:
                    cat_ = values_[cat_name]
                    if isinstance(cat_, list):
                        for isnt in cat_:
                            print(f'- {cat_name}')
                            print('-- extracted_value: ',isnt['extracted_value'])


            test_handler.find_or_create_document(collection_id, item, True)

            test_handler.close_connection()

        return


    def extract_item_data(self, item, catagory_args = {'Report': 3, 'FactSheet':3, 'PDS': 3, 'Performance':3, 'Investment':3}, time_args = {'PDS': [1, math.inf]}):
        """
        catagory_args: {topic: number, 'PDS': 5}
        time_args = {'PDS': [0, math.inf]}
        """

        file_url_list = item['metadata']['pdf_url_list']

        file_url_list = sorted(file_url_list, key=lambda file_item: file_item["epoch_time"], reverse=True)


        item_data = {
            '_c': {},
            '_values': []
        }

        # This is for getting the most cronologically up to date and highest ratio values from everything
        highest_cats = {}

        for file_idx, file_url_data in enumerate(file_url_list):
            if not file_url_data['estimated_topic'] in catagory_args:
                continue
            #elif file_url_data["epoch_time"] == 0:
            #    continue
            elif file_url_data['estimated_topic'] in time_args:
                time_range = time_args[file_url_data['estimated_topic']]
                if file_url_data["epoch_time"] < time_range[0] or file_url_data["epoch_time"] > time_range[1]:
                    print('File url out of range')
                    continue
            

            doc_data = self.docHandler.extract_document_data(file_url_data['url'])

            values_data = {
                'extract_date': time.time(),
                'url': file_url_data['url'],
                'file_url_idx': file_idx,
                'estimated_topic': file_url_data['estimated_topic']
            }

            # Get values for catagories
            for category in doc_data:
                matches = doc_data[category]
                if len(matches) == 0:
                    continue

                values_data[category] = []
                max_considered = 5
                for match in matches:
                    if max_considered <= 0:
                        break
                    max_considered -= 1
                    x = match['str']
                    if category in self.extract_mutators:
                        
                        for cond in self.extract_mutators[category]:
                            x = cond[0](x, match)
                            if len(cond) > 1:
                                if not cond[1](x, match):
                                    break
                        # --
                    if 'table' in match:
                        #print('table-url: ', file_url_data['url'])
                        x = match['table']
                    if x == None:
                        continue
                    match_data = {
                        'str': match['str'],
                        'ratio':  match['ratio'],
                        'extracted_value': x,
                    }
                    values_data[category].append(match_data)

                    # If most similar
                    if category in highest_cats:
                        if match_data['ratio'] > highest_cats[category]['ratio']:
                            highest_cats[category] = match_data
                            # Set index for file this comes from
                            highest_cats[category]['file_url_idx'] = file_idx
                    else:
                        highest_cats[category] = match_data
                        # Set index for file this comes from
                        highest_cats[category]['file_url_idx'] = file_idx

            item_data['_values'].append(values_data)

            # Deincrement remaining
            catagory_args[file_url_data['estimated_topic']] -= 1
        # --

        item_data['_c'] = highest_cats


        item['data'] = item_data

        return item
# --







'''
        for file_cat in file_list_by_category:
            file_list = file_list_by_category[file_cat]

            doctest.open_connection()

            doc_data_list = [doctest.extract_document_data(x['url']) for x in file_list]

            doctest.close_connection()

            # Extracted Data
            print("-\nExtracted Data")
            for matches_cats in doc_data_list:
                for cat in matches_cats:
                    matches = matches_cats[cat]
                    print('-', cat
                    , '\n -- ', matches[0]
                    , '\n -- ', matches[1]
                    , '\n -- ', matches[2]
                    , '\n -- ', matches[3]
                    , '\n -- ', matches[4])
            # --


            # Pull out
            #test_handler.open_connection()
            #fund = test_handler.find_or_create_document(collection_id, {'_id': item_id}, False)
            
            #fund['metadata']['pdf_url_list'] = file_list

            fund_data = {}

            for matches_cats in doc_data_list:
                for cat in matches_cats:
                    matches = matches_cats[cat]

                    x = matches[0]['str']

                    if cat in self.extract_mutators:
                        
                        for cond in self.extract_mutators[cat]:
                            x = cond[0](x, matches[0])
                            if len(cond) > 1:
                                if not cond[1](x, matches[0]):
                                    break
                        # --

                    fund_data[cat] = []
                    first_match = {
                        'str': matches[0]['str'],
                        'ratio':  matches[0]['ratio'],
                        'extracted_value': x,
                    }
                    fund_data[cat].append(first_match)
            # --


            fund['data'] = fund_data


            #test_handler.find_or_create_document(collection_id, fund, True)

            #test_handler.close_connection()
        # --
        test_handler.open_connection()

        test_handler.find_or_create_document(collection_id, fund, True)

        test_handler.close_connection()
'''











'''
from Scraper.DocHanding import DocumentHandler

def doc_handling_test():

    doctest = DocumentHandler()

    doctest.open_connection()

    file_list = doctest.filter_file_urls('novaport_site_traversal', 'PDS', ["HOW0027AU"])

    # Found pdfs
    print("-\nFound pdfs")
    [print(x) for x in file_list]



    doc_data_list = [doctest.extract_document_data(x['url']) for x in file_list]

    # Extracted Data
    print("-\nExtracted Data")
    for matches_cats in doc_data_list:
        for cat in matches_cats:
            matches = matches_cats[cat]
            print('-', cat
                , '\n -- ', matches[0]
                , '\n -- ', matches[1]
                , '\n -- ', matches[2]
                , '\n -- ', matches[3]
                , '\n -- ', matches[4])
    # --


    doctest.close_connection()


    # Pull out

    test_handler = DatabaseHandler(MONGO_URI, MONGO_DB)

    test_handler.open_connection()
    fund = test_handler.find_or_create_document('fund_managers', {'_id': "HOW0027AU"}, False)#HOW0027AU
    

    #fund['metadata']['pdf_url_list'] = [x['url'] for x in file_list]
    fund['metadata']['pdf_url_list'] = file_list

    fund_data = {}

    # Extract & clean
    extract_conditions = {
        'Buy/Sell spread': [
            [lambda x, obj: re.search('[\+\d.%]+ ?\/ ?\-[\d.%]+', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'Management Fee': [
            [lambda x, obj: re.search('[\d.%]+.{0,5}p\.a', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
            [lambda x, obj: re.search('[\d]+\.[\d]+', x), lambda x, obj: x != None],
            [lambda x, obj: x.group(0)],
        ],
        'Asset Allocation': [
            [lambda x, obj: re.findall('0|[\d]{2,3}', x), lambda x, obj: x != None],
        ],
    }

    for matches_cats in doc_data_list:
        for cat in matches_cats:
            matches = matches_cats[cat]

            x = matches[0]['str']

            if cat in extract_conditions:
                
                for cond in extract_conditions[cat]:
                    x = cond[0](x, matches[0])
                    if len(cond) > 1:
                        if not cond[1](x, matches[0]):
                            break
                # --

            fund_data[cat] = []
            first_match = {
                'str': matches[0]['str'],
                'ratio':  matches[0]['ratio'],
                'extracted_value': x,
            }
            fund_data[cat].append(first_match)
    # --


    fund['data'] = fund_data


    print(fund['data'])


    test_handler.find_or_create_document('fund_managers', fund, True)

    test_handler.close_connection()
    return
# -- # https://www.fidante.com/-/media/Shared/Fidante/NOVA/NMF_PDS.pdf?la=en

def doc_handling_run():


    test_handler = DatabaseHandler(MONGO_URI, MONGO_DB)

    test_handler.open_connection()
    fund_ids = test_handler.get_collection_ids('fund_managers')

    #traversal_ids = test_handler.get_collection_ids('site_traverse_data')

    fund_querys = [[x, test_handler.find_or_create_document('fund_managers', {'_id': x}, False)['metadata']['site_traversal_id']] for x in fund_ids]

    test_handler.close_connection()


    for fund_query in fund_querys:

        fund_id = fund_query[0]

        traversal_id = fund_query[1]

        doctest = DocumentHandler()

        doctest.open_connection()

        file_list = doctest.filter_file_urls(traversal_id, 'PDS', [fund_id])

        # Found pdfs
        print("-\nFound pdfs")
        [print(x) for x in file_list]



        doc_data_list = [doctest.extract_document_data(x['url']) for x in file_list]

        doctest.close_connection()

        # Extracted Data
        print("-\nExtracted Data")
        for matches_cats in doc_data_list:
            for cat in matches_cats:
                matches = matches_cats[cat]
                print('-', cat
                , '\n -- ', matches[0]
                , '\n -- ', matches[1]
                , '\n -- ', matches[2]
                , '\n -- ', matches[3]
                , '\n -- ', matches[4])
        # --


        # Pull out
        test_handler.open_connection()
        fund = test_handler.find_or_create_document('fund_managers', {'_id': fund_id}, False)
        

        #fund['metadata']['pdf_url_list'] = [x['url'] for x in file_list]
        fund['metadata']['pdf_url_list'] = file_list

        fund_data = {}


        # Extract & clean
        extract_conditions = {
            'Buy/Sell spread': [
                [lambda x, obj: re.search('[\+\d.%]+ ?\/ ?\-[\d.%]+', x), lambda x, obj: x != None],
                [lambda x, obj: x.group(0)],
            ],
            'Management Fee': [
                [lambda x, obj: re.search('[\d.%]+.{0,5}p\.a', x), lambda x, obj: x != None],
                [lambda x, obj: x.group(0)],
                [lambda x, obj: re.search('[\d]+\.[\d]+', x), lambda x, obj: x != None],
                [lambda x, obj: x.group(0)],
            ],
            'Asset Allocation': [
                [lambda x, obj: re.findall('0|[\d]{2,3}', x), lambda x, obj: x != None],
            ],
        }

        for matches_cats in doc_data_list:
            for cat in matches_cats:
                matches = matches_cats[cat]

                x = matches[0]['str']

                if cat in extract_conditions:
                    
                    for cond in extract_conditions[cat]:
                        x = cond[0](x, matches[0])
                        if len(cond) > 1:
                            if not cond[1](x, matches[0]):
                                break
                    # --

                fund_data[cat] = []
                first_match = {
                    'str': matches[0]['str'],
                    'ratio':  matches[0]['ratio'],
                    'extracted_value': x,
                }
                fund_data[cat].append(first_match)
        # --


        fund['data'] = fund_data


        test_handler.find_or_create_document('fund_managers', fund, True)

        test_handler.close_connection()
    # --

    return
# --


#doc_handling_run()

#doc_handling_test()
'''






























# --