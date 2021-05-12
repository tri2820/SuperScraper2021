
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



''' ------ TESTING ------ '''

#'''
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
#'''

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





'''
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

'''

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






































# --
