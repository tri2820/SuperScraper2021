import pandas as pd
from itemadapter import ItemAdapter
import pymongo
import logging
from Scraper.pdf_extraction import StringTest, DocumentExtraction, DocumentDataExtractor
#, ExtractTableHandler, TableExtraction, TableDataExtractor

#from spiderdatautils import month_format
import dateparser



MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"



#name_collection = 'fund_managers'
#traversal_collection = 'site_traverse_data'

#client = None
#db = None
#mongo_uri = MONGO_URI
#mongo_db = MONGO_DB


class DBHandler:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def open_connection(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    def close_connection(self):
        self.client.close()


    def get_collection_ids(self, collection_name_):
        ids_list = [str(x) for x in self.db[collection_name_].find().distinct('_id')]
        return ids_list


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




class FundManagerHandler:

    name_collection = 'fund_managers'
    traversal_collection = 'site_traverse_data'

    '''
    fund_test_obj = {
        '_id': 'RFA0059AU',
        'name': 'Pendal Focus Australian Share Fund',
        'APIR_code': 'RFA0059AU',
        'metadata': {
            'site_traversal_id': 'pendal_site_traversal',
            #'pdf_url': 'uehfaouefu.pdf',
        },
    }
    '''

    def open_connection(self):
        self.dbHandler = DBHandler(MONGO_URI, MONGO_DB)
        self.dbHandler.open_connection()
    # --

    def close_connection(self):
        self.dbHandler.close_connection()
    # --

    def find_pdf_urls(self, insert_document, test_against = {"discard": [], "tolerance": 4}):

        fund_document = self.dbHandler.find_or_create_document(self.name_collection, insert_document, False)#True

        fund_id = fund_document['_id']

        site_traversal_id = fund_document['metadata']['site_traversal_id']

        query = {'_id' : site_traversal_id}

        traversal_document = self.dbHandler.db[self.traversal_collection].find_one(query)

        filtered_file_urls = traversal_document['filtered_file_urls']['PDS']

        number_files = len(filtered_file_urls)

        print('Number of urls to check: ', number_files)

        for i in range(number_files):
            file_url = filtered_file_urls[i]
            print(f'-({i}/{number_files})- Url: {file_url}'.format())
            string_tester = StringTest(file_url)
            string_tester.extract_text()
            found = string_tester.test_for_string(fund_document['APIR_code'])

            # Test against
            discard_total = 0
            for discard in test_against["discard"]:
                found_discard = string_tester.test_for_string(discard)
                if found_discard and discard != fund_document['APIR_code']:
                    discard_total += 1
            # --


            if found:

                print('-FOUND-', found)

                fund_document['metadata']['pdf_url'] = file_url
                if not "pdf_url_list" in fund_document['metadata']:
                    fund_document['metadata']['pdf_url_list'] = []
                fund_document['metadata']['pdf_url_list'].append(file_url)
                
                if discard_total > test_against["tolerance"]:
                    print("\nTwo many tested against: {}".format(test_against["discard"]))
                else:
                    fund_document = self.set_pdf_url(file_url, fund_document)
                    break

                #break
            # --
        # --
        return fund_document
    # --

    def set_pdf_url(self, file_url, fund_document):
        fund_document['metadata']['pdf_url'] = file_url
        #if not "pdf_url_list" in fund_document['metadata']:
        #    fund_document['metadata']['pdf_url_list'] = []
        #fund_document['metadata']['pdf_url_list'].append(file_url)
        fund_document = self.dbHandler.find_or_create_document(self.name_collection, fund_document, True)
        return fund_document
    # --

    def get_document_pdf_data(self,insert_document):

        # Get document from database
        fund_document = self.dbHandler.find_or_create_document(self.name_collection, insert_document, False)

        if fund_document == None:
            return

        # Get ids
        fund_id = fund_document['_id']
        site_traversal_id = fund_document['metadata']['site_traversal_id']




        # DOCUMENT TESTING

        print('\n\n ---- DOCUMENT TESTING ---- \n\n')

        # IF no pdf_url : giveup

        if not 'pdf_url' in fund_document['metadata']:
            print('No url found for {}'.format(fund_id))
            return

        extraction = DocumentExtraction(fund_document['metadata']['pdf_url'])
        extraction.extract_tables()
        
        
        extract_data = DocumentDataExtractor()

        extract_data.add_document(extraction)
        extract_data.extract_similar_rows(0.2,0)
        sim_values = extract_data.sort_as_most_similar()
        #[print('\n', x, ' - ', sim_values[x], '\n') for x in sim_values]

        try:
            fund_document['Management Fee'] = sim_values['Management Fee'][0][0]
        except:
            print('Reee')
        try:
            fund_document['Buy/Sell spread'] = sim_values['Buy/Sell spread'][0][0]
        except:
            print('Reee')
        try:
            table_indecies = sim_values['Asset Allocation'][0][3]
            fund_document['Asset Allocation'] = extract_data.documents[table_indecies[0]]['pages_data'][table_indecies[1]]['tables'][table_indecies[2]]['text']
        except:
            print('Reee')



        #print(fund_document)

        fund_document = self.dbHandler.find_or_create_document(self.name_collection, fund_document, True)

        #table_handler = ExtractTableHandler(fund_document['metadata']['pdf_url'])
        #table_handler.get_tables()
        #management_fee_list = table_handler.extract_table()
        #data = {'Management fee': management_fee_list,'Intial Investment':[None],'Additional Investment':[None], 'Withdraw':[None],'Transfer':[None]}
        #df = pd.DataFrame(data)
        #print(df)
        #return df

    # --
# --


class DocumentHandler:

    traversal_collection = 'site_traverse_data'

    def open_connection(self):
        self.dbHandler = DBHandler(MONGO_URI, MONGO_DB)
        self.dbHandler.open_connection()
    # --

    def close_connection(self):
        self.dbHandler.close_connection()
    # --
    

    def find_pdf_urls(self, insert_document, collection_name = 'fund_managers', file_filter_type = 'PDS', test_for = {"accept": [], "tolerance": 1}, test_against = {"discard": [], "tolerance": 4}):
        
        document = self.dbHandler.find_or_create_document(collection_name, insert_document, False)

        site_traversal_id = document['metadata']['site_traversal_id']

        traversal_document = self.dbHandler.db[self.traversal_collection].find_one({'_id' : site_traversal_id})

        filtered_file_urls = traversal_document['filtered_file_urls'][file_filter_type]

        number_files = len(filtered_file_urls)

        print('Number of urls to check: ', number_files)

        document['metadata']['pdf_url_list'] = []

        for i in range(number_files):
            file_url = filtered_file_urls[i]
            print(f'-({i}/{number_files})- Url: {file_url}'.format())


            string_tester = StringTest(file_url)
            string_tester.extract_text()

            found = False

            # Test For
            accept_total = 0
            for accept in test_for["accept"]:
                found_accept = string_tester.test_for_string(accept)
                if found_accept and accept != document['_id']:
                    accept_total += 1
            # --
            if accept_total >= test_for["tolerance"]:
                found = True
            # --


            # Test Against
            discard_total = 0
            for discard in test_against["discard"]:
                found_discard = string_tester.test_for_string(discard)
                if found_discard and discard != document['_id']:
                    discard_total += 1
            # --
            if discard_total > test_against["tolerance"]:
                print("\nTwo many tested against: {}".format(test_against["discard"]))
                found = False
            # --


            if found:#26 July 2021
                
                
                print('-FOUND-', found)

                estimated_date = None
                date_query = '\d* ([jJ]an|[fF]eb|[mM]ar|[aA][ip][lr]|[mM]ay|[jJ]un|[jJ]ul|[aA]ug|[sS]ep|[oO]ct|[nN]ov|[dD]ec])\w+ \d+'
                date_obj = string_tester.test_for_string(date_query, True, 200)
                date_ = None
                epoch_time = 0
                if date_obj:
                    #month_format([date_obj])
                    date_ = dateparser.parse(date_obj)
                    if date_:
                        estimated_date = date_.strftime('%Y-%m')
                        epoch_time = date_.utcfromtimestamp(0)
                        

                document['metadata']['pdf_url'] = file_url
                if not "pdf_url_list" in document['metadata']:
                    document['metadata']['pdf_url_list'] = []
                document['metadata']['pdf_url_list'].append([file_url, estimated_date, epoch_time])

                document['metadata']['pdf_url_list'] = sorted(document['metadata']['pdf_url_list'], key=lambda tup: tup[2], reverse=True)
                
                #document = self.dbHandler.find_or_create_document(collection_name, document, True)
                #document = self.set_pdf_url(file_url, document)

                #break
            # --
        # --
        document = self.dbHandler.find_or_create_document(collection_name, document, True)

        return document

    def get_document_pdf_data(self,insert_document, collection_name):

        # Get document from database
        fund_document = self.dbHandler.find_or_create_document(collection_name, insert_document, False)

        if fund_document == None:
            return

        # Get ids
        fund_id = fund_document['_id']
        site_traversal_id = fund_document['metadata']['site_traversal_id']




        # DOCUMENT TESTING

        print('\n\n ---- DOCUMENT TESTING ---- \n\n')

        # IF no pdf_url : giveup

        if not 'pdf_url' in fund_document['metadata']:
            print('No url found for {}'.format(fund_id))
            return

        extraction = DocumentExtraction(fund_document['metadata']['pdf_url'])
        extraction.extract_tables()
        
        
        extract_data = DocumentDataExtractor()

        extract_data.add_document(extraction)
        extract_data.extract_similar_rows(0.2,0)
        sim_values = extract_data.sort_as_most_similar()


        try:
            fund_document['Management Fee'] = sim_values['Management Fee'][0][0]
        except:
            print('Reee')
        try:
            fund_document['Buy/Sell spread'] = sim_values['Buy/Sell spread'][0][0]
        except:
            print('Reee')
        try:
            table_indecies = sim_values['Asset Allocation'][0][3]
            fund_document['Asset Allocation'] = extract_data.documents[table_indecies[0]]['pages_data'][table_indecies[1]]['tables'][table_indecies[2]]['text']
        except:
            print('Reee')



        #print(fund_document)

        fund_document = self.dbHandler.find_or_create_document(collection_name, fund_document, True)



def run_test():


    

    fund_manager_handler = DocumentHandler()#FundManagerHandler()
    fund_manager_handler.open_connection()

    # --

    fund_managers_ids = fund_manager_handler.dbHandler.get_collection_ids('fund_managers')



    # --

    site_traverse_data_ids = fund_manager_handler.dbHandler.get_collection_ids('site_traverse_data')

    for site_id in site_traverse_data_ids:
        traversal_obj = fund_manager_handler.dbHandler.find_or_create_document('site_traverse_data', {'_id': site_id}, False)
        if not traversal_obj:
            continue
        page_filters = traversal_obj['domain']['page_filters']
        for page_filter in page_filters:
            new_manager = {
                '_id': page_filter,
                'name': 'N/A',
                'APIR_code': page_filter,
                'metadata': {
                    'site_traversal_id': traversal_obj['_id']
                },
            }
            new_manager = fund_manager_handler.find_pdf_urls(new_manager, collection_name = 'fund_managers', file_filter_type = 'PDS', test_for = {"accept": [page_filter], "tolerance": 1}, test_against= {"discard": fund_managers_ids, "tolerance": 4})
            fund_manager_handler.get_document_pdf_data(new_manager, 'fund_managers')
    # --

    #for test_obj in test_obj_list:
    #    fund_manager_handler.find_pdf_urls(test_obj)
    #    fund_manager_handler.get_document_pdf_data(test_obj)
    # --
    fund_manager_handler.close_connection()
# --














'''
{
    '_id': 'VAN0002AU',
    'name': 'Vanguard Australian Share Index',
    'APIR_code': 'VAN0002AU',
    'metadata': {
        'site_traversal_id': 'vanguard_site_traversal',
        'pdf_url': 'https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS-1.pdf',
    },
},
{
    '_id': 'RFA0059AU',
    'name': 'Pendal Focus Australian Share Fund',
    'APIR_code': 'RFA0059AU',
    'metadata': {
        'site_traversal_id': 'pendal_site_traversal',
        #'pdf_url': 'uehfaouefu.pdf',
    },
},
{
    '_id': 'BNT0003AU',
    'name': 'Hyperion Australian Growth Companies Fund',
    'APIR_code': 'BNT0003AU',
    'metadata': {
        'site_traversal_id': 'hyperion_site_traversal',
        #'pdf_url': 'uehfaouefu.pdf',
    },
},
{
    '_id': 'FID0008AU',
    'name': 'Fidelity Australian Equities',
    'APIR_code': 'FID0008AU',
    'metadata': {
        'site_traversal_id': 'fidelity_site_traversal',
        #'pdf_url': 'uehfaouefu.pdf',
    },
},
'''





























































# --
