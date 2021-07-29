import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SuperTraversalData
import pandas as pd

#from Scraper.spiderdatautils import check_content_type

from io import StringIO

#from Scraper.spiders.super_base import BaseSpider

from scrapy.linkextractors import LinkExtractor, IGNORED_EXTENSIONS

from scrapy.http import Request

import time



from difflib import SequenceMatcher

#import re


class SiteTraversal(scrapy.Spider):
    name = "Traversal"


    crawl_selections = []

    traverse_data = None

    domain = None
    file_extraction = None

    file_extractor = None
    link_extractor = None

    traversed_urls = {}
    file_urls = {}
    filtered_pages = {}

    log_info = {
        'total_traversed': 0,
        'total_files_considered': 0,

        'last_traversed': 0,
        'last_considered': 0,

        'traversal_per_minute': 0,
        'considered_per_minute': 0,

        'time': {
            'start': 0,
            'current': 0,
            'last_min': 0
        }
    }

    def log_progress(self):
        self.log_info['time']['current'] = round(time.time() - self.log_info['time']['start'], 1)

        if self.log_info['time']['current'] / 60 > self.log_info['time']['last_min']:
            self.log_info['time']['last_min'] = round(self.log_info['time']['current'] / 60, 1)

            # Calculate per minute
            traversed_per_min = self.log_info['total_traversed'] - self.log_info['last_traversed']
            considered_per_min = self.log_info['last_considered'] - self.log_info['total_files_considered']
            self.log_info['traversal_per_minute'] = traversed_per_min
            self.log_info['considered_per_minute'] = considered_per_min

            # Update per min values
            self.log_info['last_traversed'] = self.log_info['total_traversed']
            self.log_info['last_considered'] = self.log_info['total_files_considered']
        else:
            return
        # --

        # Logging
        logging.info("Total time: {}".format(self.log_info['time']['current']))
        logging.info("Total traversed: {}".format(self.log_info['total_traversed']))
        logging.info("Total considered: {}".format(self.log_info['total_files_considered']))

        logging.info("Traversal per-min: {}".format(self.log_info['traversal_per_minute']))
        logging.info("Considered per-min: {}".format(self.log_info['considered_per_minute']))
        return

    def __init__(self, traverse_data = None, *args, **kwargs):
        super(SiteTraversal, self).__init__(*args, **kwargs)
        self.set_variables()
        #self.driver_awd = webdriver.Chrome(executable_path="chromedriver.exe")
        self.traverse_data = traverse_data
        #print('__init__ START ---- !*$(*!#%*&)')
        if self.traverse_data != None:
            self.init_crawler_urls()
        # --
    # --

    def init_crawler_urls(self):
        self.domain = self.traverse_data['domain']
        self.file_extraction = self.traverse_data['file_extraction_rules']
        deny_extensions_ = []
        if 'deny_extensions' in self.file_extraction:
            deny_extensions_ = self.file_extraction['deny_extensions']
        # --
        self.link_extractor = LinkExtractor(allow_domains = [self.domain['domain_name']])
        # Setup extractor for pdf files
        self.file_extractor = LinkExtractor(allow_domains = [self.domain['domain_name']], deny_extensions = deny_extensions_)# allow = self.file_extraction['allow'], restrict_text = restrict_text_,

        parse_object = (self.domain['parse_select'], self.domain['start_url'])
        self.crawl_selections.append(parse_object)
    # --



    def start_requests(self):
        #print('dom',self.domain)
        for selection in self.crawl_selections:
            parse_select, url = selection
            if hasattr(self, parse_select):
                yield scrapy.Request(url=url, callback=getattr(self,parse_select))
    # --

    def set_variables(self):
        self.crawl_selections = []

        self.traverse_data = None

        self.domain = None
        self.file_extraction = None

        self.file_extractor = None
        self.link_extractor = None

        self.traversed_urls = {}
        self.file_urls = {}
        self.filtered_pages = {}

        self.log_info = {
            'total_traversed': 0,
            'total_files_considered': 0,

            'last_traversed': 0,
            'traversal_per_minute': 0,
            
            'last_considered': 0,
            'considered_per_minute': 0,

            'time': {
                'start': time.time(),
                'current': 0,
                'last_min': 0
            }
        }
    # --



    def traverse(self, response, depth = 0):

        #print('HEADERS -- Traversal -- Content-type: ',response.headers.get('content-type'), ' response.url: ',response.url)
        # Do not re-traverse already traversed urls
        if response.url in self.traversed_urls:
            return
        else:
            self.traversed_urls[response.url] = response.url
        # --

        # Consider logging
        self.log_progress()

        traverse_item = SuperTraversalData()
        traverse_item['_id'] = self.traverse_data['_id']

        page_urls_ = []
        file_urls_ = []

        # Extract connected urls links
        for link in self.link_extractor.extract_links(response):
            if not link.url in self.traversed_urls:
                page_urls_.append(link)
        # --
        # Extract connected file links
        file_extractions = self.file_extractor.extract_links(response)
        for link in file_extractions:
            file_urls_.append(link.url)
            if not link.url in self.file_urls:
                self.file_urls[link.url] = link

        # Test for stings and codes requered to identify certain pages
        texts = response.css("::text").getall()

        for filter_name in self.domain['page_filters']:
            page_filter = self.domain['page_filters'][filter_name]
            successes = {}
            for text in texts:
                for find_string in page_filter:
                    if not find_string in successes:
                        success = text.find(find_string)
                        if success != -1:
                            successes[find_string] = True
            # --
            if len(successes) == len(page_filter):
                filtered_page = {
                    'name': filter_name,
                    'url': response.url,
                    'page_filter': page_filter,
                    'file_urls': file_urls_,
                }
                self.filtered_pages[filter_name] = filtered_page
            # --
        # --

        # Run iterative traversal operations
        if depth < 1:
            for link in page_urls_:
                request = Request(link.url, callback=self.traverse)
                request.cb_kwargs['depth'] = depth + 1
                yield request
            # --
        # --
        #yield traverse_item
    # --



#https://www.hyperion.com.au/wp-content/uploads/prices-page/GGCFB.csv

#Traversal

#http://quotes.toscrape.com/

#https://aware.com.au/sitemap.xml

#https://aware.com.au

#https://www.hesta.com.au/content/hesta/members/your-superannuation/fees-and-costs.html

#/content/dam/hesta/Documents/Fees-and-costs.pdf

#div.download-list-component

#div.download_wrapper

#https://www.hyperion.com.au/prices-performance/

#https://www.hyperion.com.au

#https://www.sitemaps.org/protocol.html

#https://www.pendalgroup.com/sitemap_index.xml


#url_string = 'https://www.hesta.com.au/content/hesta/members/your-superannuation/fees-and-costs.html'
#parse_object = ('extract_files', url_string)
#https://www.pendalgroup.com/ #https://www.pendalgroup.com/products/pendal-australian-equity-fund/





















































# --
