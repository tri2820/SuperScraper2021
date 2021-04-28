import scrapy
import csv
#import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO

from Scraper.spiders.super_base import BaseSpider


#jabgibaegibigbego

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1


class TelstraSpider(BaseSpider):
    name = "Telstra"

    def parse_monthly(self, response):
        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']


        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Date')

        super_fund['super_offerings'] = df

        super_fund['insert_cat'] = 'monthly_performances'

        super_fund['format_time'] = True

        yield super_fund






























































# --
