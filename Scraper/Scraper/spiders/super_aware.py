import scrapy
import csv
#import logging

from Scraper.items import SuperFundData, SpecificOffering
import pandas as pd

from Scraper import spiderdatautils

from io import StringIO

#https://aware.com.au/content/dam/ftc/superreturns/super-02-2021.csv


class AwareSpider(scrapy.Spider):
    name = "Aware"

    start_urls = []
    # --
    start_urls = ["https://aware.com.au/content/dam/ftc/charts/Super.csv"]

    super_id = 0

    def __init__(self, super_id = None, *args, **kwargs):
        super(AwareSpider, self).__init__(*args, **kwargs)
        self.super_id = super_id

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # Testing code -- Creates a csv with data

        filename = 'Aware.csv'
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






























































# --
