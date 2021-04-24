import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils




class FutureSpider(scrapy.Spider):
    name = "Future"


    start_urls = []

    crawl_selections = []


    fund_data = None

    # TODO: Make this apply for all spiders somehow
    def __init__(self, fund_data = None, *args, **kwargs):
        super(HestaSpider, self).__init__(*args, **kwargs)
        self.fund_data = fund_data
        #logging.debug(self.fund_data)
        if self.fund_data != None:
            self.init_crawler_urls()

    # TODO: Make this apply for all spiders somehow
    def init_crawler_urls(self):
        #self.data_url = self.fund_data['metadata']['get_data_url']
        #data_url = self.fund_data['metadata']['get_data_url']

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
            #yield scrapy.Request(url=url, callback=self.parse)

    # --

    def parse_hist(self, response):
        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']

        table_bodies = response.css("table-container four-up")
        for table_body in table_bodies:
            # Get headings of this table (Future - Months)
            table_months = []
            table_months = table_body.css("h5::text").getall()
            table_months = table_months[1:]

            table_rows = table_body.css("h4::text")getall()
            #using this variable to get offer type
    	    x= 0

            offer_types = {}
            for table_row in table_rows:
                row_values = []
                row_values = table_row.css("p::text").getall()
                if len(row_values) > 0:
                    offer_type = table_row[x]
                    row_values = row_values[1:]
                    offer_types[offer_type] = row_values
                    x = x+1
            # --

            df = pd.DataFrame(data = offer_types, index = table_months)

            super_fund['super_offerings'] = df

            super_fund['insert_cat'] = 'historial_performances'

            super_fund['format_time'] = False

            yield super_fund

   