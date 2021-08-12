import pandas as pd
from itemadapter import ItemAdapter
import pymongo
import logging
from Scraper.pdf_extraction import StringTest, ExtractTableHandler, TableExtraction, TableDataExtractor, DocumentExtraction, DocumentDataExtractor


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

    fund_test_obj = {
        '_id': 'RFA0059AU',
        'name': 'Pendal Focus Australian Share Fund',
        'APIR_code': 'RFA0059AU',
        'metadata': {
            'site_traversal_id': 'pendal_site_traversal',
            #'pdf_url': 'uehfaouefu.pdf',
        },
    }

    def open_connection(self):
        self.dbHandler = DBHandler(MONGO_URI, MONGO_DB)
        self.dbHandler.open_connection()
    # --

    def close_connection(self):
        self.dbHandler.close_connection()
    # --

    def find_pdf_urls(self, insert_document):

        fund_document = self.dbHandler.find_or_create_document(self.name_collection, insert_document, True)#True

        fund_id = fund_document['_id']

        site_traversal_id = fund_document['metadata']['site_traversal_id']

        query = {'_id' : site_traversal_id}

        traversal_document = self.dbHandler.db[self.traversal_collection].find_one(query)

        filtered_file_urls = traversal_document['filtered_file_urls']

        number_files = len(filtered_file_urls)

        print('Number of urls to check: ', number_files)

        for i in range(number_files):
            file_url = filtered_file_urls[i]
            print(f'-({i}/{number_files})- Url: {file_url}'.format())
            #fee_value, investment_value = run_extraction(file_url)
            string_tester = StringTest(file_url)
            string_tester.extract_text()
            found = string_tester.test_for_string(fund_document['APIR_code'])
            if found:
                self.set_pdf_url(file_url, fund_document)
                print('-FOUND-', found)
                break
            # --
        # --
    # --

    def set_pdf_url(self, file_url, fund_document):
        fund_document['metadata']['pdf_url'] = file_url
        fund_document = self.dbHandler.find_or_create_document(self.name_collection, fund_document, True)
    # --

    def get_document_pdf_data(self,insert_document):

        # Get document from database
        fund_document = self.dbHandler.find_or_create_document(self.name_collection, insert_document, False)

        if fund_document == None:
            return

        # Get ids
        fund_id = fund_document['_id']
        site_traversal_id = fund_document['metadata']['site_traversal_id']

        #'''
        extraction = TableExtraction(fund_document['metadata']['pdf_url'])
        extraction.extract_tables()
        extraction.filter_tables()

        extract_data = TableDataExtractor()
        extract_data.store_extracted_tables(extraction.filtered_tables)
        extract_data.extract_similar_rows(0.2)
        extract_data.sort_as_most_similar(True)
        extract_data.compile_similarity_data()
        extract_data.print_similarity_df()

        sim_df_list = extract_data.similarity_df_list

        #print(sim_df_list)

        fund_document['Management Fee'] = sim_df_list['Management Fee'][1][0]
        fund_document['Buy/Sell spread'] = sim_df_list['Buy/Sell spread'][1][0]
        #'''




        # DOCUMENT TESTING

        print('\n\n ---- DOCUMENT TESTING ---- \n\n')

        extraction = DocumentExtraction(fund_document['metadata']['pdf_url'])
        extraction.extract_tables()
        
        
        extract_data = DocumentDataExtractor()

        extract_data.add_document(extraction)
        extract_data.extract_similar_rows(0,0.2)
        shrinked_catagories = extract_data.sort_as_most_similar()
        [print('\n', x, ' - ', shrinked_catagories[x], '\n') for x in shrinked_catagories]




        #print(fund_document)

        #fund_document = self.dbHandler.find_or_create_document(self.name_collection, fund_document, True)

        #table_handler = ExtractTableHandler(fund_document['metadata']['pdf_url'])
        #table_handler.get_tables()
        #management_fee_list = table_handler.extract_table()
        #data = {'Management fee': management_fee_list,'Intial Investment':[None],'Additional Investment':[None], 'Withdraw':[None],'Transfer':[None]}
        #df = pd.DataFrame(data)
        #print(df)
        #return df

    # --
# --




'''

test_obj_list = [
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
    {
        '_id': 'VAN0002AU',
        'name': 'Vanguard Australian Share Index',
        'APIR_code': 'VAN0002AU',
        'metadata': {
            'site_traversal_id': 'vanguard_site_traversal',
            #'pdf_url': 'uehfaouefu.pdf',
        },
    },
]

fund_manager_handler = FundManagerHandler()
fund_manager_handler.open_connection()
for test_obj in [test_obj_list[1]]:
    fund_manager_handler.find_pdf_urls(test_obj)
    fund_manager_handler.get_document_pdf_data(test_obj)
# --
fund_manager_handler.close_connection()
'''


def run_test():

    test_obj_list = [
        {
            '_id': 'VAN0002AU',
            'name': 'Vanguard Australian Share Index',
            'APIR_code': 'VAN0002AU',
            'metadata': {
                'site_traversal_id': 'vanguard_site_traversal',
                'pdf_url': 'https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS-1.pdf',
            },
        },
    ]

    fund_manager_handler = FundManagerHandler()
    fund_manager_handler.open_connection()
    for test_obj in [test_obj_list[0]]:
        fund_manager_handler.find_pdf_urls(test_obj)
        fund_manager_handler.get_document_pdf_data(test_obj)
    # --
    fund_manager_handler.close_connection()
# --














'''
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
