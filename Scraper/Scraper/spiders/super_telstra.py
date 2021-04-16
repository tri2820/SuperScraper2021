import scrapy
import csv
#import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO


#jabgibaegibigbego

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1


class TelstraSpider(scrapy.Spider):
    name = "Telstra"

    start_urls = ['https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1']

    # --


    super_id = 0

    def __init__(self, super_id = None, *args, **kwargs):
        super(TelstraSpider, self).__init__(*args, **kwargs)
        self.super_id = super_id

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        '''
        # Testing code -- Creates a csv with data
        filename = 'Telstra.csv'
        with open(filename, mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow([response.url])
            #csv_writer.writerows(response.text)
            csv_file.write(response.text)
        '''
        # --

        super_fund = SuperFundData()
        super_fund['_id'] = self.super_id
        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Date')

        super_fund['super_offerings'] = df

        yield super_fund



























































# --
