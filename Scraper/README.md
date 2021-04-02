# Scrapy Scraper



### How To Set This Up

Things you need:
- Python (anaconda)
- Scrapy: conda install scrapy (do in vertual env)
- Mongodb lib: Refer to database example

### How To Run This

Navigate to the base directory (Its name is 'Scraper' and it has this file in it)

In the anaconda prompt console (or in IDE ect..) type: 'python scraper_run.py' .

This will run everything that is setup so far-ish.


### How Scrapy Works - ish
The spiders folder is where more individual logic and code for spiders and per website scraping is held.
A new spider can be made by just copying the code of one to a new file and changing the requisite values.

More general and hopfully dynamic scraping coming in future, however there will always be an element of: Specific Logic for Specific Website

'spiderdatautils.py' is a utilitise file with some hardcode right now, I will be expanded upon as/if spiders and logic become more dynamic and more utils are needed.

'settings.py' its settings

'piplines.py' this is basically where data coming out of the spiders is handled and manipulated, it goes in order and stuff there is a whole thing. Very useful



