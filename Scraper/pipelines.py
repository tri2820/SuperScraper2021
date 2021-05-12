# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


'''
# Refactor the pipline

'''


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import logging
import pandas as pd

import numpy as np

from collections import defaultdict

from Scraper import spiderdatautils


import json
import csv


import re


class ScraperPipeline:
    def process_item(self, item, spider):
        return item



















































# --
