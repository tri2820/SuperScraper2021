import scrapy
import csv
#import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO


#jabgibaegibigbego

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1


class TelstraSpider(scrapy.Spider):
    name = "Telstra"


    start_urls = []

    crawl_selections = []

    #data_url = ""

    fund_data = None

    # TODO: Make this apply for all spiders somehow
    def __init__(self, fund_data = None, *args, **kwargs):
        super(TelstraSpider, self).__init__(*args, **kwargs)
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

    def parse_monthly(self, response):
        print("hello")



'''
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


        # Testing code -- Creates a csv with data
        filename = 'Telstra.csv'
        with open(filename, mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow([response.url])
            #csv_writer.writerows(response.text)
            csv_file.write(response.text)

        # --

        super_fund = SuperFundData()
        super_fund['_id'] = self.super_id
        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Date')

        super_fund['super_offerings'] = df

        yield super_fund
'''


























































# --
