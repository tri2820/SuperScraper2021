import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd
import numpy as np

from Scraper import spiderdatautils

from Scraper.spiders.super_base import BaseSpider

'''
HESTASPIDER

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

--- parse_hist ---
The parse method is responsible for processing the response and returning the scraped data and/or more URLs to follow.
Returns an iterable of requests or items[object](dict-like)].


Parameters:
 - response: It is an object in the form of an HTTP response that is fed to the spider for processing


'''

#class HestaSpider(scrapy.Spider):
class HestaSpider(BaseSpider):
    name = "Hesta"

    start_urls = []
    crawl_selections = []
    fund_data = None

    # --

    def parse_hist(self, response):
        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']

        table_bodies = response.css("tbody")
        for table_body in table_bodies:
            # Get headings of this table (Hesta - Months)
            table_titles = []
            table_titles = table_body.css("th::text").getall()
            table_titles = table_titles[1:]
            #if len(table_titles) > 0:
                #table_titles = spiderdatautils.month_format(table_titles, year_value)

            # Handle table rows - values
            table_rows = table_body.css("tr")

            offer_types = {}
            for table_row in table_rows:
                row_values = []
                row_values = table_row.css("td::text").getall()
                if len(row_values) > 0:
                    offer_type = row_values[0]
                    row_values = row_values[1:]
                    offer_types[offer_type] = row_values
            # --

            df = pd.DataFrame(data = offer_types, index = table_titles)

            super_fund['scraped_data'] = df

            super_fund['insert_cat'] = 'historial_performances'

            #super_fund['format_time'] = False

            yield super_fund

    #def parse(self, response):
    def parse_monthly(self, response):
        # TODO: Use meta data instead (do this when metadata setup is used)
        print('000ew0ijg09 g20g148u t8 85389 h2593 9053gh2 5 HESTAHETA')
        print(response.url.split("year="))
        year_value = response.url.split("year=")[1]
        year_values = year_value.split("-")
        year_value_first = year_values[0]
        year_value_second = year_values[1]

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
                row_values = table_row.css("td::text").getall()
                if len(row_values) > 0:
                    offer_type = row_values[0]
                    row_values = row_values[1:]
                    offer_types[offer_type] = row_values
            # --

            df = pd.DataFrame(data = offer_types, index = table_titles)

            #super_fund['scraped_data'] = df

            super_fund['insert_cat'] = 'monthly_performances'

            super_fund['format_time'] = True

            # Split dataframe in two and give, first year, then second

            dfs = np.split(df, [6], axis=0)

            super_fund['year_value'] = year_value_first

            super_fund['scraped_data'] = dfs[0]

            yield super_fund

            super_fund['year_value'] = year_value_second

            super_fund['scraped_data'] = dfs[1]

            yield super_fund
        # --















































# --
