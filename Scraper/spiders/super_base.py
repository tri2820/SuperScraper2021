import scrapy
from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO



'''
BASESPIDER

Class Varaibles:
 - crawl_selections[list][tuples]: (parse_select, url)
    - url[string]: url parsed to scrapy spider, url to goto and scrap.
    - parse_select[string]: a string variable that matches the name of the function to be run (eg: 'parse_monthly', 'parse_hist')

This is the base class for all current conventional spiders.

 --- __init__ ---
Extension of defualt scrapy.spider __init__ additonal argument of fund_data
Runs on spider init, sets data varaibles and runs init_crawler_urls

Parameters:
 - fund_data[object(dict-like)]: metadata given for spider to run (typically pulled from the mongodb database).


 --- init_crawler_urls ---
Function used to set the initial set of urls and metadata that is used when running the scraping part of the spider.

Sets 'start_urls', 'crawl_selections' using 'fund_data' that was set upon spider initialization

 --- start_requests ---
Iterates through 'crawl_selections' and initiates a crawling operation for all url-function pairs in the list.
The idea is that 'url' specifies the page to go to and 'parse_select' specifies the function to run (specified in callback)

'''



class BaseSpider(scrapy.Spider):

    # These variables must be set on children of this class as the variables chage over use in thier respective spiders.
    start_urls = []
    crawl_selections = []
    fund_data = None

    def __init__(self, fund_data = None, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.fund_data = fund_data
        #logging.debug(self.fund_data)
        if self.fund_data != None:
            self.init_crawler_urls()

    # TODO: Make this apply for all spiders somehow
    def init_crawler_urls(self):

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
        # --


# --

























































# --
