import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from Scraper.spiders.super_base import BaseSpider


class FutureSpider(BaseSpider):
    name = "Future"

    start_urls = []
    crawl_selections = []
    fund_data = None

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

            table_rows = table_body.css("h4::text").getall()
            #using this variable to get offer type
            x = 0

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

            yield super_fund
