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

More general and hopefully dynamic scraping coming in future, however there will always be an element of: Specific Logic for Specific Website

'spiderdatautils.py' is a utilities file with some hardcode right now, I will be expanded upon as/if spiders and logic become more dynamic and more utils are needed.

'settings.py' its settings

'piplines.py' this is basically where data coming out of the spiders is handled and manipulated, it goes in order and stuff there is a whole thing. Very useful


### Things to do

##### Documentation

Update documentation for all readme.md files. This includes 2 scraper files, 1 database one.

Specific stuff:
 - Add brief explanations for each spider.
 - Add explanations of functions in base spider class.
 - Add explanations of database - spider interaction in files: (base spider class, pipelines, scraper_run.py).
 - Add explanations of data cleaning and formatting in pipelines.
 - Add explanations of database document creation in pipelines.

General stuff:
 - Update documentation explaining how to install scrapy and requisite libraries, add documentation explaining other file interactions.
 - Outline future direction of scraper.
 - Some database documentation
 - Database table of variable types and what they mean/do.

Types of documentation:
 - Trello future features, direction, current tasks (very general) [Amount: small]
 - In code documentation [Amount: Large]
 - Readme.txt [Amount: Small]
 - Readme.md(like this) [Amount: Mid - Large]
 - Separate ms teams dev thread.

#### - Build basis for features to be expanded on next trimester -

##### PDF Scan [PRIO: Low]

Exists on separate feature branch 'pdf-extraction' - (branched from dev)

Hamish suggests the Camelot library as it contains a lot of options and variability:
https://camelot-py.readthedocs.io/en/master/

Create separate module/file(s) (similar to spiderdatautils) that can then be loaded in by pipelines for utility.

When testing start with completely separate testing, run the file itself.

#####  Website Traversal [PRIO: Low]
Exists on separate feature branch 'Site-Traversal' - (branched from dev)
Specific implementation and testing of a website traversal spider.

Given a website url:
 - Collect lists of all possible page and website links under the given website domain (Completed)
 - Go to all links/pages and run detections to detect possible scrapable data (data tables, files, pdfs, csv, ect..). (Not - Completed)
 - Send data to pipelines. (Not - Completed)

Complete to a very basic level.

##### Fee Scraping - (Extended) - [PRIO: Low]

If fees data can be found in simple scrapable form on websites, add it to current spider implementations.

Completed for: Aware.

Not Completed for: Hesta, Future, Telstra

##### Refactoring - (Stability, Readability, Structure) - [PRIO: Mid]

Focus on refactoring certain parts of spider codebase.

Prios here are referring to priority within this task

Parts to consider refactoring:
 - Pipelines: Separate 'SuperDataMongodb' into cleaning, formatting, database handler (upload, metadata) [Prio: High]
 - individual Spiders: Fix up certain parts of spiders (variable names, excessive complexity, additional metadata, ect..) [Prio: Low]
 - 'scraper_run.py': Add some additional bits and pieces to the 'scraper_run.py' file, then refactor it.
    It should have more functionality and have the ability for certain run variables to be called exteranally [Prio: Mid]
 - Items: Remove unecessery item variables, refactor certain sets of multiple variables into single variables that are objects or items (eg: format_time + year_value -> time),
    Add additional variables in anticipation for future values and metadata, just to give some direction [Prio: Mid]

All refactoring and extensions can dealt with when needed.

## NOTE: Feel free to append to this document thingy or ask Hamish about stuff in it


# --
