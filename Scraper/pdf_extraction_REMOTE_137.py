
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

url_string = "https://www.vanguard.com.au/adviser/products/documents/8189/AU"
compare_string_list = ['management fee','fees and expenses','estimated total management costs']
def get_tables():
        tables = camelot.read_pdf(url_string,pages = 'all', flavor = 'stream',flag_size=True)
        return tables

def similarity_thing(string_, compare_string_list_):
        found = False
        highest = 0
        similarity_list = []
        for item in compare_string_list_:
            similarity_list.append(SequenceMatcher(None,item,string_).ratio())
        for i in similarity_list:
                if i > highest:
                        highest = i
        return highest

def get_specific_tables():
        tables = get_tables()
        df_new_list =[]
        all_df = pd.DataFrame()
        for table in tables:
                table_df = table.df
                table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
                df_list = table_df.values.tolist()
                for i in range(len(df_list)):
                        for j in df_list[i]:
                                x = SequenceMatcher(None,'type of fee or costs',j).ratio()
                                if x > 0.6:
                                        df_new_list.append(table_df)
                                        all_df = pd.concat(df_new_list)
        return all_df


def get_similar_row(all_df):
        new_df_list = all_df.values.tolist()
        found = []
        highest = 0
        for i in range(len(new_df_list)):
                for j in new_df_list[i]:
                        similarity_value = similarity_thing(j.lower(),compare_string_list)
                        if similarity_value> highest:
                                highest = similarity_value
                                found = new_df_list[i]
        return found

def extract_table():
        all_df = get_specific_tables()
        found = get_similar_row(all_df)

        fee_value = ""
        for i in found:
                x = i.find("0.")
                if x != -1:
                        fee_value = i[x:(x+10)]

        management_fee_list = []
        management_fee_list.append(fee_value)
        return management_fee_list

#getting the dataframe
management_fee_list = extract_table()
data = {'Management fee': management_fee_list,'Intial Investment':[None],'Additional Investment':[None], 'Withdraw':[None],'Transfer':[None]}
df = pd.DataFrame(data)  

#print(df)  



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

#testing for hyperian
#tables = camelot.read_pdf("https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf",pages = 'all', flavor = 'stream',flag_size=True)


# Print table types
#for table in tables:
    #print(type(table))
    #print(type(table.df))
#print(type(tables))

# Save all tables as test csv
#tables.export('camalot_test.csv', f='csv')


# Create one big dataframe of all tables
#df_list = []
#for table in tables:
    # Turn into dataframe
    #table_df = table.df
    # Add to df_list
    #df_list.append(table_df)
# --

# Now we can combine all of them into a new dataframe
#all_df = pd.concat(df_list)
#all_df.columns = range(len(all_df.columns))
#all_df.to_csv('camalot_test_dataframes.csv')#,index=True
#print(all_df)

# Extracting first table
#temp_df = tables[0].df

#temp_df.rename(columns=temp_df.iloc[0]).drop(temp_df.index[0])

#exporting to csv for trial
#temp_df.to_csv('tables.csv',index=True)


#checks for management fee in the table
#outputs a dataframe of false and true values
#found = temp_df.apply(lambda row: row.astype(str).str.contains('Management fee').any(), axis=1)
#print(found)


#def similarity_thing(string_):
    #similarity_ = SequenceMatcher(None,'Fees',string_).ratio()
    #return similarity_
# --

#SequenceMatcher(None, ,similar_string)
#def find_similar(similar_df,similar_string):
    #new_df = similar_df.apply(similarity_thing)
    #new_df = [similar_df]
    #new_df = similar_df[similar_df[0]]
    #return new_df
# --






# Testing how running against dataframes works

df_test = pd.DataFrame(data={'num1':[0,1,2,3,4,5],'num2':[23,4,5,17,25,21],'num3':[1,2,3,21,5,6]})

print(df_test)

hmm_df = df_test[df_test > 3]#df_test.where(df_test[])

hmm_df1 = df_test[df_test['num3'] > 3]

print(hmm_df)
print(hmm_df1)

Returns:
   num1  num2  num3
0     0    23     1
1     1     4     2
2     2     5     3
3     3    17    21
4     4    25     5
5     5    21     6
   num1  num2  num3
0   NaN    23   NaN
1   NaN     4   NaN
2   NaN     5   NaN
3   NaN    17  21.0
4   4.0    25   5.0
5   5.0    21   6.0
   num1  num2  num3
3     3    17    21
4     4    25     5
5     5    21     6



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
