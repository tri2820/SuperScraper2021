from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

process.crawl('Telstra')
process.crawl('Aware')
process.crawl('Hesta')
process.start()

print("Crawl Completed")















































# --
