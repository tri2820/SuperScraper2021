import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils




class HestaSpider(scrapy.Spider):
    name = "Hesta"


    start_urls = []

    crawl_selections = []

    #data_url = ""


    '''
    # --- TEMPORARY ---

    data_url = "https://www.hesta.com.au/content/hesta/members/investments/super-performance/jcr:content/par/investmentperformanc.monthly.html?year="

    url_append_strings = ['2016-2017']#,'2017-2018','2018-2019','2019-2020','2020-2021'

    for append_string in url_append_strings:
        add_string = ""
        add_string = hesta_url_string + append_string
        start_urls.append(add_string)
        print(add_string)
    '''

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

        table_bodies = response.css("tbody")
        for table_body in table_bodies:
            # Get headings of this table (Hesta - Months)
            table_months = []
            table_months = table_body.css("th::text").getall()
            table_months = table_months[1:]
            #if len(table_months) > 0:
                #table_months = spiderdatautils.month_format(table_months, year_value)

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

            df = pd.DataFrame(data = offer_types, index = table_months)

            super_fund['super_offerings'] = df

            super_fund['insert_cat'] = 'historial_performances'

            yield super_fund

    #def parse(self, response):
    def parse_monthly(self, response):
        year_value = response.url.split("year=")[1]
        year_value = year_value.split("-")[1]

        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']

        table_bodies = response.css("tbody")
        for table_body in table_bodies:
            # Get headings of this table (Hesta - Months)
            table_months = []
            table_months = table_body.css("th::text").getall()
            table_months = table_months[1:]
            if len(table_months) > 0:
                # TODO: Move this logic to datacleaning pipeline
                table_months = spiderdatautils.month_format(table_months, year_value)

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

            df = pd.DataFrame(data = offer_types, index = table_months)

            super_fund['super_offerings'] = df

            super_fund['insert_cat'] = 'monthly_performances'

            yield super_fund
        # --















































# --
