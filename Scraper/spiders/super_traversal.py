import scrapy
import csv
import logging

from Scraper.items import SuperFundData, SuperTraversalData
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO

#from Scraper.spiders.super_base import BaseSpider

from scrapy.linkextractors import LinkExtractor

from scrapy.http import Request

from difflib import SequenceMatcher



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

#APIR

#print(response.css("a[href]").getall())

#for href in response.css('div#all_results h3 a::attr(href)').extract():

class QuotesTraversal(scrapy.Spider):
    name = "Traversal"

    start_urls = []
    crawl_selections = []
    traverse_data = None

    APIR_urls = {}
    pdf_urls = {}

    APIR_code = 'RFA0818AU'#'RFA0059AU'#'RFA0818AU'
    #BNT0003AU

    file_name = 'pendal'

    traversed_urls = {}

    rules = {
        'allow': [
            #'category\.php',#category.php
            #'\.pdf',#.pdf
            '.+\.pdf',#anything + .pdf
        ]
    }

    pdf_extractor = LinkExtractor(allow = rules['allow'], deny_extensions = [])


    # www.hesta.com.au, www.pendalgroup.com, www.hyperion.com.au
    link_extractor = LinkExtractor(allow_domains = ['www.pendalgroup.com'])

    def __init__(self, traverse_data = None, *args, **kwargs):
        super(QuotesTraversal, self).__init__(*args, **kwargs)
        self.traverse_data = traverse_data
        if self.traverse_data != None:
            self.init_crawler_urls()

    def init_crawler_urls(self):

        #url_string = 'https://www.hesta.com.au/content/hesta/members/your-superannuation/fees-and-costs.html'
        #parse_object = ('extract_files', url_string)
        url_string = 'https://www.pendalgroup.com/'#https://www.pendalgroup.com/ #https://www.pendalgroup.com/products/pendal-australian-equity-fund/
        parse_object = ('traverse', url_string)
        self.crawl_selections.append(parse_object)
        self.start_urls.append(url_string)



    def start_requests(self):
        for selection in self.crawl_selections:
            parse_select, url = selection
            if hasattr(self, parse_select):
                yield scrapy.Request(url=url, callback=getattr(self,parse_select))
    # --



    def traverse(self, response, depth = 0):

        # Do not re-traverse already traversed urls
        if response.url in self.traversed_urls:
            return
        else:
            self.traversed_urls[response.url] = response.url
        # --

        traverse_item = SuperTraversalData()
        traverse_item['_id'] = self.traverse_data['_id']

        texts = response.css("::text").getall()
        #print(texts,'\n\n\n  ---')
        yes_ = False
        APIR_, APIR_CODE_ = -1, -1

        for text in texts:
            APIR_ = text.find('APIR')
            if APIR_ != -1:
                break
        # --

        for text in texts:
            APIR_CODE_ = text.find(self.APIR_code)
            if APIR_CODE_ != -1:
                break
        # --

        if APIR_ != -1 and APIR_CODE_ != -1:
            print("Url: ", response.url, 'APIR: ', self.APIR_code)
            self.APIR_urls[response.url] = {'URL': response.url, 'APIR': self.APIR_code}
            print(self.APIR_urls)
            yes_ = True
        # --

        urls_ = []

        for link in self.link_extractor.extract_links(response):
            if not link.url in self.traversed_urls:
                urls_.append(link)
                #self.traversed_urls[link.url] = link
                #if yes_ == True:
                    #self.APIR_urls[link.url] = (link, )
                #print("Url: ", link.url)
            # --
        # --

        for link in self.pdf_extractor.extract_links(response):
            if not link.url in self.pdf_urls:
                self.pdf_urls[link.url] = link

        if depth < 2:
            print(depth)
            for link in urls_:
                request = Request(link.url, callback=self.traverse)
                request.cb_kwargs['depth'] = depth + 1
                yield request
            # --
        # --
        yield traverse_item
    # --





    def download(self, response):
        filename = response.url.split('/')[-1] + '.pdf'
        print("Saving as: ", filename)
        with open(filename, 'wb') as f:
            f.write(response.body)
        # --
    # --

    def extract_files(self, response):
        traverse_item = SuperTraversalData()
        traverse_item['_id'] = self.traverse_data['_id']

        urls_ = []

        for link in self.pdf_extractor.extract_links(response):
            urls_.append(link)

        traverse_item['page_urls'] = urls_
        for link in urls_:
            print("Downloading: ", link.url)
            yield Request(link.url, callback=self.download)

        yield traverse_item
    # --

































































# --
