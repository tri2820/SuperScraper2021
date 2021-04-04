# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class SuperFundData(scrapy.Item):
    _id = scrapy.Field()
    super_offerings = scrapy.Field()
    insert_cat = scrapy.Field()



class SpecificOffering(scrapy.Item):
    _id = scrapy.Field()
    fund_id = scrapy.Field()
    name = scrapy.Field()
    monthly_performances = scrapy.Field()# [ {month: '', growth: ''}, {month: '', growth: ''} ]





























# --
