import scrapy
import csv
#import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO


from Scraper.spiders.super_base import BaseSpider

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1

'''
TELSTRASPIDER

Class Variables:
- start_urls[list]: a list of urls that the spider will begin to crawl from when no particular URLs are specified

- name: a string which defines the name for the current spider

 - crawl_selections[list][tuples]: (parse_select, url)
    - url[string]: url parsed to scrapy spider, url to goto and scrap.
    - parse_select[string]: a string variable that matches the name of the function to be run (eg: 'parse_monthly', 'parse_hist')

- fund_data[object(dict-like)]: metadata given for spider to run (typically pulled from the mongodb database).

 --- parse_monthly ---
The parse method is responsible for processing the response and returning the scraped data and/or more URLs to follow.
Returns an iterable of requests or items[object](dict-like)].

Parameters:
 - response: It is an object in the form of an HTTP response that is fed to the spider for processing

'''

class TelstraSpider(scrapy.Spider):
    name = "Telstra"


    start_urls = []
    crawl_selections = []
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

    # --

    def parse_monthly(self, response):
        super_fund = SuperFundData()
        super_fund['_id'] = self.fund_data['_id']

        df = pd.read_csv(StringIO(response.text), sep=",", index_col= 'Date')

        super_fund['scraped_data'] = df

        super_fund['insert_cat'] = 'monthly_performances'

        super_fund['format_time'] = True

        yield super_fund


'''
class TelstraSpider(scrapy.Spider):
    name = "Telstra"
>>>>>>> VAISHALI-Thing


#jabgibaegibigbego

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1

#https://www.telstrasuper.com.au/api/Investment/DownloadMonthlyInvestmentPerformance?SelectedOptions=GROW%2CBAL%2CDEFG%2CCONS%2CINTL%2CAUST%2CPROP%2CFINT%2CCASH%2CINC&Category=AC&DataType=performancepercentage&DateRange=12m&ShowAll=1

'''































































# --
