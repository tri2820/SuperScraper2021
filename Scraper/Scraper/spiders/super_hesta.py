import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils




class HestaSpider(scrapy.Spider):
    name = "Hesta"


    start_urls = []

    data_url = ""


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
        logging.debug(self.fund_data)
        if self.fund_data != None:
            self.init_crawler_urls()

    # TODO: Make this apply for all spiders somehow
    def init_crawler_urls(self):
        self.data_url = self.fund_data['metadata']['get_data_url']

        # If there are variables to collect from create a url for each value
        url_variables = self.fund_data['metadata']['url_variables']
        for variable in url_variables:
            append_string = ""
            input_string = variable['input']
            variable_values = variable['values']
            for value in variable_values:
                if value['use']:
                    append_string = self.data_url
                    append_string += input_string + value['url_string']
                    self.start_urls.append(append_string)




    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)


    '''
    def month_format(month_strs, year_value):
        date_convertions = {'Jan':"01",'Feb':"02",'Mar':"03",'Apr':"04",'May':"05",'Jun':"06",'Jul':"07",'Aug':"08",'Sep':"09",'Oct':"10",'Nov':"11",'Dec':"12"}
        month_ints = []
        for month_str in month_strs:
            if month_str in date_convertions:
                month_ints.append(date_convertions[month_str] + "-" + year_value)
        return month_ints
    '''

    # --

    def parse(self, response):

        year_value = response.url.split("year=")[1]
        year_value = year_value.split("-")[1]

        '''
        # Testing code -- Creates a csv with data

        with open('hesta-thing.csv', mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow([response.url])
            table_bodies = response.css("tbody")
            for table_body in table_bodies:
                # Get headings of this table
                table_headings = []
                table_headings = table_body.css("th::text").getall()
                table_headings = table_headings[1:]
                if len(table_headings) > 0:
                    csv_writer.writerow(table_headings)

                # Handle table rows - values
                table_rows = table_body.css("tr")
                for table_row in table_rows:
                    row_values = []
                    row_values = table_row.css("td::text").getall()
                    #self.log(row_values)
                    if len(row_values) > 0:
                        csv_writer.writerow(row_values)
        # --
        '''

        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']

        table_bodies = response.css("tbody")
        for table_body in table_bodies:
            # Get headings of this table (Hesta - Months)
            table_headings = []
            table_headings = table_body.css("th::text").getall()
            table_headings = table_headings[1:]
            if len(table_headings) > 0:
                table_headings = spiderdatautils.month_format(table_headings, year_value)

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

            df = pd.DataFrame(data = offer_types, index = table_headings)

            super_fund['super_offerings'] = df

            yield super_fund
        # --















































# --
