import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd
import numpy as np

from Scraper import spiderdatautils

from Scraper.spiders.super_base import BaseSpider



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

            super_fund['super_offerings'] = df

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

            #super_fund['super_offerings'] = df

            super_fund['insert_cat'] = 'monthly_performances'

            super_fund['format_time'] = True

            # Split dataframe in two and give, first year, then second

            dfs = np.split(df, [6], axis=0)

            super_fund['year_value'] = year_value_first

            super_fund['super_offerings'] = dfs[0]

            yield super_fund

            super_fund['year_value'] = year_value_second

            super_fund['super_offerings'] = dfs[1]

            yield super_fund
        # --















































# --
