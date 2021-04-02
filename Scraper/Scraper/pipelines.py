# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScraperPipeline:
    def process_item(self, item, spider):
        return item


# TODO: Partition database for names, id, ect .. |\ then format data

class SuperDataArange:

    def process_item(self, item, spider):
        return item
# --

# TODO: Clean data

class SuperDataClean:

    def process_item(self, item, spider):
        return item
# --

# TODO: Enter into database

class SuperDataToMongodb:

    def process_item(self, item, spider):
        return item
# --
















































# --
