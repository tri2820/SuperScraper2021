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
    # NOTE: I changed this for extra functionality (now object). May allow different assignments in future
    year_value = scrapy.Field()
    format_time = scrapy.Field()
    # This field is intended to be set as a lambda for any extra convertion things
    value_mutator = scrapy.Field()
    # Add as new table if not found
    add_new = scrapy.Field()
    # Indicates the keys for this collection
    value_object_keys = scrapy.Field()
# --





class SuperTraversalData(scrapy.Item):
    _id = scrapy.Field()
    page_urls = scrapy.Field()
    text_thing = scrapy.Field()
# --


class SpecificOffering(scrapy.Item):
    _id = scrapy.Field()
    fund_id = scrapy.Field()
    name = scrapy.Field()
    monthly_performances = scrapy.Field()# [ {month: '', growth: ''}, {month: '', growth: ''} ]





























# --
