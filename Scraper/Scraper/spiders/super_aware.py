import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO

#https://aware.com.au/content/dam/ftc/superreturns/super-02-2021.csv


class AwareSpider(scrapy.Spider):
    name = "Aware"

    start_urls = []

    crawl_selections = []

    # --
    #start_urls = ["https://aware.com.au/content/dam/ftc/charts/Super.csv"]

    #super_id = 0

    fund_data = None

    # TODO: Make this apply for all spiders somehow
    def __init__(self, fund_data = None, *args, **kwargs):
        super(AwareSpider, self).__init__(*args, **kwargs)
        self.fund_data = fund_data
        #logging.debug(self.fund_data)
        if self.fund_data != None:
            self.init_crawler_urls()

    # TODO: Make this apply for all spiders somehow
    def init_crawler_urls(self):

        crawl_objects = self.fund_data['metadata']['crawl_objects']

        for crawl_object in crawl_objects:
            data_url = crawl_object['get_data_url']
            # 'crawl_objects'
            # If there are variables to collect from create a url for each value
            url_variables = crawl_object['url_variables']
            parse_select = crawl_object['parse_select']
            for variable in url_variables:
                append_string = ""
                input_string = variable['input']
                variable_values = variable['values']
                for value in variable_values:
                    if value['use']:
                        append_string = data_url#self.data_url
                        append_string += input_string + value['url_string']
                        parse_object = (parse_select, append_string)
                        self.crawl_selections.append(parse_object)
                        self.start_urls.append(append_string)



    def start_requests(self):
        #for url in self.start_urls:
        for selection in self.crawl_selections:
            parse_select, url = selection
            if hasattr(self, parse_select):
                yield scrapy.Request(url=url, callback=getattr(self,parse_select))


    #def parse(self, response):
    def parse_monthly(self, response):

        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']
        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Date')

        super_fund['super_offerings'] = df

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

            super_fund['super_offerings'] = df

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

        super_fund['super_offerings'] = df

        #super_fund['value_mutator'] = lambda a: a * 100

        super_fund['insert_cat'] = 'allocations'

        #super_fund['format_time'] = False

        yield super_fund






























































# --
