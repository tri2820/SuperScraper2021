
import dateparser
import datetime

import re

import camelot

# --- This may be useful
# NOTE: https://github.com/python/cpython/blob/main/Lib/difflib.py
from difflib import SequenceMatcher
# ---

import PyPDF2

import pandas as pd

import matplotlib.pyplot as plt

'''
Below are some funds and the corrisponding links to the pdfs, i dont think we dont want to be uploading pdfs to the bitbucket, so download them and then move them out when uploading or something
https://www.pendalgroup.com/products/pendal-australian-share-fund/ : https://www.pendalgroup.com/wp-content/uploads/docs/factsheets/PDS/Pendal%20Australian%20Share%20Fund%20-%20PDS.pdf?v=2021-05-061620317117
https://www.hyperion.com.au/hyperion-australian-growth-companies-fund/ : https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf
https://www.fidelity.com.au/funds/fidelity-australian-equities-fund/ : https://www.fidelity.com.au/funds/fidelity-australian-equities-fund/related-documents/product-disclosure-statement/
https://www.vanguard.com.au/adviser/products/en/detail/wholesale/8100/equity : https://www.vanguard.com.au/adviser/products/documents/8189/AU
'''

'''

To use the liabaries here you only need to install 1 new library: camelot-py
Can be done with this command: conda install -c conda-forge camelot-py

# TODO: Extract tables from pdf (this can be all of them, we can always choose which ones we want after extraction)
# TODO: Extract text from pdf: https://www.geeksforgeeks.org/working-with-pdf-files-in-python/ look at first point in this tutorial
        for a simple starting setup.

# TODO: Function that can find a specific sting in the pdf. This can then be used to find the sting of the APIR code eg: 'RFA0059AU'
        additionally we should also extract the 'ARSN' which is a different identification code in documents
# TODO: Classes and/or functions that extract tables from pdfs in pandas dataframe form.


# -- Current specific client data --
# TODO: We want to try and get:

1st Fees and expenses (eg: 'Management fee')

2nd Then stuff like 'Distribution frequency', 'Minimum investment', ect...

3rd(everything else) Then try 'sector allocation', 'holdings', ect..

'''


'''
Initially hardcoding for testing is good.
Later on try to use as little hardcoding as possible, try to make things have options so they are dynamic.
'''
#randomedit

'''
# TODO:
'''








import io

import requests


tables = camelot.read_pdf("https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf",pages = 'all', flavor = 'stream',flag_size=True)


class StringTest:

    url_string = ""
    text = ""

    def __init__(self, url_string_):
        self.url_string = url_string_


    def extract_text(self):
        r = requests.get(self.url_string)
        f = io.BytesIO(r.content)

        pdfReader = PyPDF2.PdfFileReader(f)
        #print(pdfReader.numPages)
        self.text = ""

        for page in pdfReader.pages:
            self.text += page.extractText()
        # --
        text_file = open("pdf_texts.txt", "w")
        text_file.write(self.url_string)
        text_file.close()


    def test_for_string(self, test_string):
        found = self.text.find(test_string) != -1
        return found

# --


class ExtractTableHandler:
    # -Remmbe self.url_string
    url_string = "https://www.vanguard.com.au/adviser/products/documents/8189/AU"
    compare_string_list = ['management fee','fees and expenses','estimated total management costs']

    tables = []

    # The function that runs upon creation
    def __init__(self, url_string_, compare_string_list_ = ['management fee','fees and expenses','estimated total management costs']):
        # Set the input url given on class creation ie: ExtractTable("https://www.vanguard.com.au/adviser/products/documents/8189/AU")
        self.url_string = url_string_
        self.compare_string_list = compare_string_list_

    def get_tables(self):
        self.tables = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=True)

    def find_most_similar(self, string_, compare_string_list_):
        highest_match = ("","",0)
        similarity_list = []
        for item in compare_string_list_:
            ratio_ = SequenceMatcher(None,item,string_).ratio()
            match_info = (string_, item, ratio_)
            similarity_list.append(match_info)

        for match_info in similarity_list:
            if match_info[2] > highest_match[2]:
                highest_match = match_info
        return highest_match

    def extract_match_tables(self):
        df_list = []
        matched_dfs = pd.DataFrame()
        for table in self.tables:
            table_df = table.df
            table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
            # Convert to list and extract lists that are similar
            # TODO: Do this using a dataframe at some point (not priority)
            values_list = table_df.values.tolist()
            #print(table_df, values_list)
            for i in range(len(values_list)):
                for j in values_list[i]:
                    # TODO: We should unhard code stuff like this
                    x = SequenceMatcher(None,'type of fee or costs',j).ratio()
                    if x > 0.6:
                        df_list.append(table_df)
                        print(table_df)
                        #matched_dfs = pd.concat(df_list)
        if len(df_list) > 0:
            matched_dfs = pd.concat(df_list)
        return matched_dfs


    def get_similar_row(self, matched_dfs):
        df_list = matched_dfs.values.tolist()
        #print(df_list)
        found = []
        highest = 0
        for i in range(len(df_list)):
            for j in df_list[i]:
                similarity_info = self.find_most_similar(str(j).lower(),self.compare_string_list)#j.lower()
                similarity_value = similarity_info[2]
                if similarity_value > highest:
                    highest = similarity_value
                    found = df_list[i]
        return found

    def extract_table(self):
        matched_dfs = self.extract_match_tables()
        found = self.get_similar_row(matched_dfs)

        # TODO: Mabye move these cleaning operations to a different class or functions,
        # reason being because this data cleaning operation is specifically for fund managers (not prio)
        # NOTE: Look into regex
        fee_value = ""
        for i in found:
            x = i.find("0.")
            if x != -1:
                fee_value = i[x:(x+10)]

        management_fee_list = []
        management_fee_list.append(fee_value)
        return management_fee_list

# --


class TableExtraction:

    url_string = ''
    extracted_tables = {
        'stream': [],
        'lattice_b_t': [],
        'lattice_b_f': [],
    }

    filtered_tables = {
        'stream': [],
        'lattice_b_t': [],
        'lattice_b_f': [],
    }

    def __init__(self, url_string_):
        self.url_string = url_string_

    def get_tables(self):
        self.extracted_tables['stream'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=False)
        self.extracted_tables['lattice_b_t'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=False, process_background = True)
        self.extracted_tables['lattice_b_f'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=False, process_background = False)

    def filter_tables(self):

        for table_type in self.extracted_tables:
            tables_ = self.extracted_tables[table_type]
            for table_ in tables_:
                table_df = table.df
                drop_table = Falsea
                # If only one column or one row - drop
                if table_.shape[0] <= 1 or table_.shape[1] <= 1:
                    drop_table = True

                if not drop_table:
                    table_object = self.generate_table_stats(table_)
                    self.filtered_tables[table_type].append(table_object)
        # --

    def generate_table_stats(self, table_):

        # Table bbox
        cols_ = [item for t in table_.cols for item in t]
        rows_ = [item for t in table_.rows for item in t]

        table_bbox = ((min(cols_),max(rows_)), (max(cols_), min(rows_)))
        table_bbox_string = str(min(cols_)) + ',' + str(max(rows_)) + ',' + str(max(cols_)) + ',' + str(min(rows_))

        # Table midpoint
        x_mid = (min(cols_)+max(cols_))/2
        y_mid = (min(rows_)+max(rows_))/2

        table_midpoint = (x_mid, y_mid)

        # Table area
        table_area = (max(_cols_) - min(_cols_)) * (max(_rows_) - min(_rows_))

        table_object = {
            'table': table_,
            'table_bbox': table_bbox,
            'table_bbox_string': table_bbox_string,
            'table_midpoint': table_midpoint,
            'table_area': table_area
        }

        return table_object


class TableDataExtractor:

    def __init__(self, url_string_):
        self.url_string = url_string_


#getting the dataframe
'''
table_handler = ExtractTableHandler("https://www.vanguard.com.au/adviser/products/documents/8189/AU")
table_handler.get_tables()
management_fee_list = table_handler.extract_table()


data = {'Management fee': management_fee_list,'Intial Investment':[None],'Additional Investment':[None], 'Withdraw':[None],'Transfer':[None]}
df = pd.DataFrame(data)

print(df)
'''

# 'https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund_PDS.pdf'
# 'https://www.pendalgroup.com/wp-content/uploads/docs/factsheets/PDS/Pendal%20Focus%20Australian%20Share%20Fund%20-%20PDS.pdf?v=2021-05-141620965181'

'''

url_string = 'https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund_PDS.pdf'

#url_string = 'https://www.pendalgroup.com/wp-content/uploads/docs/factsheets/PDS/Pendal%20Focus%20Australian%20Share%20Fund%20-%20PDS.pdf?v=2021-05-141620965181'

tables_list = []

# '1,2,3,4,5,6,7,8,9,10,11,12,13'

plt.rcParams["figure.figsize"] = (8,8)

tables_streams = camelot.read_pdf(url_string, pages = 'all', flavor = 'stream', flag_size = True)
tables_lattice_true = camelot.read_pdf(url_string, pages = 'all', flavor = 'lattice', process_background = True)
tables_lattice_false = camelot.read_pdf(url_string, pages = 'all', flavor = 'lattice', process_background = False)#, flag_size = True

#if tables.n > 0:
tables_list.append((tables_streams,tables_lattice_true,tables_lattice_false))
# --

if len(tables_list) > 0:
    for tables_a in tables_list:
        tables_streams_ = tables_a[0]
        tables_lattice_true_ = tables_a[1]
        tables_lattice_false_ = tables_a[2]
        lentgth = max([len(tables_streams_),len(tables_lattice_true_),len(tables_lattice_false_)])
        for i in range(lentgth):
            if i < len(tables_streams_):
                x = tables_[i]
                #camelot.plot(x, kind='text').show()
                #camelot.plot(x, kind='grid').show()
                plt.title('stream')
                camelot.plot(x, kind='contour').show()
                print(x.df)
                #print('Accuracy: ', x.accuracy)
                #print('Page: ', x.page)
                print('stream')
                print(x.parsing_report)
                #input(' - Press Enter to proceed')
                #plt.close('all')
            if i < len(tables_lattice_true_):
                x = tables_1[i]
                #camelot.plot(x, kind='text').show()
                #camelot.plot(x, kind='grid').show()
                plt.title('tables_lattice')
                camelot.plot(x, kind='contour').show()
                print(x.df)
                #print('Accuracy: ', x.accuracy)
                #print('Page: ', x.page)
                print('process_background = False')
                print(x.parsing_report)
                #input(' - Press Enter to proceed')
                #plt.close('all')
            if i < len(tables_lattice_false_):
                x = tables_1[i]
                #camelot.plot(x, kind='text').show()
                #camelot.plot(x, kind='grid').show()
                plt.title('tables_lattice_false')
                camelot.plot(x, kind='contour').show()
                print(x.df)
                #print('Accuracy: ', x.accuracy)
                #print('Page: ', x.page)
                print('process_background = False')
                print(x.parsing_report)
                #input(' - Press Enter to proceed')
                #plt.close('all')
            input(' - Press Enter to proceed')
            plt.close('all')
'''

        '''
        for x in tables_:7
            #camelot.plot(x, kind='text').show()
            #camelot.plot(x, kind='grid').show()
            camelot.plot(x, kind='contour').show()
            print(x.df)
            #print('Accuracy: ', x.accuracy)
            #print('Page: ', x.page)
            print(x.parsing_report)
            input(' - Press Enter to proceed')
            plt.close('all')
        # --

        for x in tables_1:
            #camelot.plot(x, kind='text').show()
            #camelot.plot(x, kind='grid').show()
            camelot.plot(x, kind='contour').show()
            print(x.df)
            #print('Accuracy: ', x.accuracy)
            #print('Page: ', x.page)
            print(x.parsing_report)
            input(' - Press Enter to proceed')
            plt.close('all')
        '''
        # --
    # --
# --



# class ExtractTable:

#         url_string = ""
#         compare_string_list = ['management fee','fees and expenses','estimated total management costs']

#         def __init__(self, url_string_):
#                 self.url_string = url_string_

#         def get_tables(self, url_string):
#                 tables = camelot.read_pdf(self.url_string,pages = 'all', flavor = 'stream',flag_size=True)
#                 return tables

#         def similarity_thing(self, string_,compare_string_list):
#                 found = False
#                 highest = 0
#                 similarity_list = []
#                 for item in self.compare_string_list:
#                     similarity_list.append(SequenceMatcher(None,item,string_).ratio())
#                 for i in similarity_list:
#                         if i > highest:
#                                 highest = i
#                 return highest

#         def get_specific_tables(self, url_string):
#                 tables = get_tables(self.url_string)
#                 df_new_list =[]
#                 all_df = pd.DataFrame()
#                 for table in tables:
#                         table_df = table.df
#                         table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
#                         df_list = table_df.values.tolist()
#                         for i in range(len(df_list)):
#                                 for j in df_list[i]:
#                                         x = SequenceMatcher(None,'type of fee or costs',j).ratio()
#                                         if x > 0.6:
#                                                 df_new_list.append(table_df)
#                                                 all_df = pd.concat(df_new_list)
#                 return all_df


#         def get_similar_row(self, all_df):
#                 new_df_list = self.all_df.values.tolist()
#                 found = []
#                 highest = 0
#                 for i in range(len(new_df_list)):
#                         for j in new_df_list[i]:
#                                 similarity_value = similarity_thing(j.lower(),compare_string_list)
#                                 if similarity_value> highest:
#                                         highest = similarity_value
#                                         found = new_df_list[i]
#                 return found

#         def extract_table(self,url_string):
#                 all_df = get_specific_tables(self.url_string)
#                 found = get_similar_row(all_df)

#                 fee_value = ""
#                 for i in found:
#                         x = i.find("0.")
#                         if x != -1:
#                                 fee_value = i[x:(x+10)]
#                 management_fee_list = []
#                 management_fee_list.append(fee_value)
#                 return management_fee_list





'''
#import re
#found = []
#found_investment = []

def camalot_test():
    #this extracts the apir code
    for table in tables:
        table_df = table.df
        table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
        df_list = table_df.values.tolist()
        #print(df_list)
        for i in range(len(df_list)):
            for j in df_list[i]:
                x = j.find("APIR")
                if x != -1:
                    end = j.find("AU")
                    APIR_code = j[x:(end+2)]


    print(APIR_code)

    #function to get highest similarity ratio based on defined strings
    def similarity_thing(string_):
        found = False
        highest = 0
        similarity_list = []
        similarity_list.append(SequenceMatcher(None,'management fee',string_).ratio())
        similarity_list.append(SequenceMatcher(None,'fees and expenses',string_).ratio())
        similarity_list.append(SequenceMatcher(None,'estimated total management costs',string_).ratio())
        for i in similarity_list:
            if i > highest:
                highest = i
        return highest



    #gets the specific tables(tables matching with type of fee or costs) and concatenates them in a dataframe
    df_new_list =[]
    for table in tables:
        table_df = table.df
        table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
        df_list = table_df.values.tolist()
        for i in range(len(df_list)):
            for j in df_list[i]:
                x = SequenceMatcher(None,'type of fee or costs',j).ratio()
                if x > 0.6:
                    df_new_list.append(table_df)
                    #all_df = pd.concat(df_new_list)


    all_df = pd.concat(df_new_list)
    print(all_df)


    #finds and extracts the most relatable list to get the management fee
    new_df_list = all_df.values.tolist()
    found = []
    highest = 0
    for i in range(len(new_df_list)):
        for j in new_df_list[i]:
            similarity_value = similarity_thing(j.lower())
            print(j)
            print(similarity_value)
            if similarity_value> highest:
                highest = similarity_value
                found = new_df_list[i]

    print(found)

    #extracting of management fee value into variable fee_value
    fee_value = ""
    for i in found:
        x = i.find("0.")
        if x != -1:
            fee_value = i[x:(x+10)]

    print(fee_value)




#"https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf"

def run_extraction(pdf_url):

    tables = camelot.read_pdf(pdf_url,pages = 'all', flavor = 'stream',flag_size=True)
    df_list = []
    for table in tables:
        # Turn into dataframe
        table_df = table.df
        table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
        # Add to df_list
        df_list.append(table_df)
    # --

    # Now we can combine all of them into a new dataframe
    all_df = pd.concat(df_list)

    found = []
    found_investment = []
    for table in tables:
        table_df = table.df
        table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
        df_list = table_df.values.tolist()

        for i in range(len(df_list)):
            for j in df_list[i]:
                similarity_ = SequenceMatcher(None,'Fees and expenses',j).ratio()
                similarity_2 = SequenceMatcher(None,'initial investment',j).ratio()
                if (similarity_ > 0.65):
                    found = df_list[i]
                if (similarity_2 > 0.65):
                    found_investment = df_list[i]


    fee_value = ""
    for i in found:
        x = i.find("0.")
        if x != -1:
            fee_value = i[x:len(i)]
            print(x)

    investment_value = ""
    for i in found_investment:
        x = i.find("$")
        if x != -1:
            investment_value = i[x:len(i)]
            print(x)

    #print('Fee & Investment values')
    print(fee_value)
    print(investment_value)
    return fee_value, investment_value


'''










# --
