import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO

from Scraper.spiders.super_base import BaseSpider

#https://aware.com.au/content/dam/ftc/superreturns/super-02-2021.csv

'''
AWARESPIDER

Class Variables:
- start_urls[list]: a list of urls that the spider will begin to crawl from when no particular URLs are specified

- name: a string which defines the name for the current spider

 - crawl_selections[list][tuples]: (parse_select, url)
    - url[string]: url parsed to scrapy spider, url to goto and scrap.
    - parse_select[string]: a string variable that matches the name of the function to be run (eg: 'parse_monthly', 'parse_hist')

- fund_data[object(dict-like)]: metadata given for spider to run (typically pulled from the mongodb database).

 --- parse_monthly ---
The parse method is responsible for processing the response and returning the scraped data and/or more URLs to follow.
Returns an iterable of requests or items[object](dict-like)].

--- parse_allocation ---

--- parse_fee ---

Parameters:
 - response: It is an object in the form of an HTTP response that is fed to the spider for processing


'''


class AwareSpider(BaseSpider):
    name = "Aware"

    start_urls = []
    crawl_selections = []
    fund_data = None

    #def parse(self, response):
    def parse_monthly(self, response):

        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']
        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Date')

        super_fund['scraped_data'] = df

        super_fund['value_mutator'] = lambda a: a * 100

        super_fund['insert_cat'] = 'monthly_performances'

        super_fund['format_time'] = True

        yield super_fund


    #def parse(self, response):
    def parse_fee(self, response):

        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']

        table_bodies = response.css("tbody")
        for table_body in table_bodies:
            # Get headings of this table (Hesta - Months)
            table_titles = []
            table_titles = table_body.css("th::text").getall()
            table_titles = table_titles[1:]
            # Handle table rows - values
            table_rows = table_body.css("tr")

            offer_types = {}
            for table_row in table_rows:
                row_values = []
                row_values_ = table_row.css("td")
                for value_ in row_values_:
                    temp = value_.css("::text").get()
                    if temp != None:
                        row_values.append(temp)
                # --


                if len(row_values) > 0:
                    offer_type = row_values[0]
                    row_values = row_values[1:]
                    offer_types[offer_type] = row_values
            # --

            df = pd.DataFrame(data = offer_types, index = table_titles)

            super_fund['scraped_data'] = df

            super_fund['insert_cat'] = 'costs_fees'

            #super_fund['format_time'] = False

            super_fund['value_object_keys'] = ['Cost_Type', 'Value']

            super_fund['add_new'] = True

            yield super_fund

            break # Break because we only want the first one


    def parse_allocation(self, response):
        #https://aware.com.au/content/dam/ftc/assetallocations/super-tris-actual-asset-allocation-2021-03.csv
        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']
        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Asset Class')
        #df = df.transpose()

        super_fund['scraped_data'] = df

        #super_fund['value_mutator'] = lambda a: a * 100

        super_fund['insert_cat'] = 'allocations'

        yield super_fund






























































# --
