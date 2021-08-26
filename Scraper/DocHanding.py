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
                estimated_date = None
                date_query = '\d* ([jJ]an|[fF]eb|[mM]ar|[aA][ip][lr]|[mM]ay|[jJ]un|[jJ]ul|[aA]ug|[sS]ep|[oO]ct|[nN]ov|[dD]ec])\w+ \d+'
                date_string_match = string_tester.test_for_string(date_query, True, 200)
                date_ = None
                epoch_time = 0
                date_strings = date_string_match.groups()
                date_string = date_strings[0]
                if date_string:
                    date_ = dateparser.parse(date_string)
                    if date_:
                        estimated_date = date_.strftime('%Y-%m')
                        epoch_time = date_.timestamp()
                # --

                insert_object = {'url': file_url, 'estimated_date': estimated_date, 'epoch_time': epoch_time}
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

        # Extract doc
        doc_extract = DocumentExtraction(url)
        doc_extract.extract_tables()

        # Add extracted doc to handler
        last_doc_idx = self.docExtractor.add_document(doc_extract)
        #last_doc_idx = len(self.docExtractor.documents) - 1
        self.docExtractor.extract_similar_rows(0.2, last_doc_idx)

        sorted_values = self.docExtractor.sort_as_most_similar(last_doc_idx)


        return sorted_values



















































# --