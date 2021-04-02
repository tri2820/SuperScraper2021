import scrapy
import csv
#import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils




class HestaSpider(scrapy.Spider):
    name = "Hesta"
    #'''

    '''
    custom_settings = {
        '_id': 'some value',
    }
    '''

    # TODO: Make it so that this has settings/attributes which are specified when running this spider, these include _id, name, ect ..

    start_urls = []

    hesta_url_string = "https://www.hesta.com.au/content/hesta/members/investments/super-performance/jcr:content/par/investmentperformanc.monthly.html?year="

    # --- TEMPORARY ---

    url_append_strings = ['2016-2017','2017-2018','2018-2019','2019-2020','2020-2021']

    for append_string in url_append_strings:
        add_string = ""
        add_string = hesta_url_string + append_string
        start_urls.append(add_string)
        print(add_string)
    #'''

    '''
    # Example Data

    SuperFundAttributes = {
        '_id' = None,
        'name' = None,
        'type' = None,
        'website' = None,
        'crawl_order' = {
            'dates' = ['2016-2017','2017-2018','2018-2019','2019-2020','2020-2021']
        }
    }
    '''
    #_super_fund = SuperFund()

    super_id = 0

    #def __init__(self, superFundAttributes=None, *args, **kwargs):
    #def __init__(self, _id=None, name=None, type=None, website_url=None, *args, **kwargs):#, super_performance=None
    def __init__(self, super_id = None, *args, **kwargs):
        super(HestaSpider, self).__init__(*args, **kwargs)
        self.super_id = super_id
        #self._super_fund.super_atts = superFundAttributes
        #self._super_fund._id = _id
        #self._super_fund.name = name
        #self._super_fund.type = type
        #self._super_fund.website_url = website_url
        #self._super_fund.super_offerings = {}
        #self.start_urls = [f'http://www.example.com/categories/{category}']


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

        '''
        # Testing code -- Creates a csv with data

        year_value = response.url.split("year=")[1]
        year_value = year_value.split("-")[1]

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
        super_fund['_id'] = self.super_id

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
