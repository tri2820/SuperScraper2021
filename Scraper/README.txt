THIS IS ONE PLACE DOCUMENTING SCRAPER OPERATION AND FUNCTIONALITY







 ---- DOCUMENTATION ----

IF YOU THINK THAT THERE ARE SPECIFIC CHANGES OR IMPROVMENTS THAT CAN BE MADE OR SHOULD BE MADE, APEND TO THIS AND TELL PPL.
IF YOU HAVE ANY QUESTIONS ASK HAMISH.

Current protocol for in code documentation.
Use this format as a guide for the minimum level of detail for documentation and as a guide on how one might structure documentation.

Some formatting and documentation guides.
  - Denote variable, class and file names with some form of symbol. (eg: 'scraper_run.py')
    Do this when:
    - Referencing variables names or class names in descriptions or text where it is not immediately obvious that they are names.
  - When specifying certain values (variables, parameters, ect..) denote the type of variable. (eg: count[float])


'''
{CLASS NAME GOES HERE}

{CLASS DISCRIPTION OR VARIABLE DISCRIPTIONS}

Class Variables:
 - {VARIABLE NAME}[{VARIABLE TYPE}][{VARIABLE SUBTYPE}]: {example of variable structure}
    - {VARIABLE NAME}[{VARIABLE TYPE}]: {DISCRIPTION OF VARIABLE} {MABYE AN EXAMPLE}.
    - {VARIABLE NAME}[{VARIABLE TYPE}]: {DISCRIPTION OF VARIABLE}.

{CLASS DISCRIPTION}

Class Functions:

 --- {FUNCTION NAME GOES HERE} ---
{FUNCTION DISCRIPTION}
{FUNCTION DISCRIPTION}

Parameters:
 - {PARAMETER NAME}[{PARAMETER VARIABLE TYPE}]: {PARAMETER DISCRIPTION}.
 - {PARAMETER NAME}[{PARAMETER VARIABLE TYPE}]: {PARAMETER DISCRIPTION}.


 --- {FUNCTION NAME GOES HERE} ---
{FUNCTION DISCRIPTION}
{FUNCTION DISCRIPTION}

Parameters:
 - {PARAMETER NAME}[{PARAMETER VARIABLE TYPE}]: {PARAMETER DISCRIPTION}.
 - {PARAMETER NAME}[{PARAMETER VARIABLE TYPE}]: {PARAMETER DISCRIPTION}.

 --- {FUNCTION NAME GOES HERE} ---
{FUNCTION DISCRIPTION}
{FUNCTION DISCRIPTION}

Parameters:
 - {PARAMETER NAME}[{PARAMETER VARIABLE TYPE}]: {PARAMETER DISCRIPTION}.
 - {PARAMETER NAME}[{PARAMETER VARIABLE TYPE}]: {PARAMETER DISCRIPTION}.

'''

THE FOLLOWING IS AN EXAMPLE OF SOME DOCUMENTATION FOR A SCRAPER CLASS:

'''
BASESPIDER

Class Varaibles:
 - crawl_selections[list][tuples]: (parse_select, url)
    - url[string]: url parsed to scrapy spider, url to goto and scrap.
    - parse_select[string]: a string variable that matches the name of the function to be run (eg: 'parse_monthly', 'parse_hist')

This is the base class for all current conventional spiders.

 --- __init__ ---
Extension of defualt scrapy.spider __init__ additonal argument of fund_data
Runs on spider init, sets data varaibles and runs init_crawler_urls

Parameters:
 - fund_data[object(dict-like)]: metadata given for spider to run (typically pulled from the mongodb database).


 --- init_crawler_urls ---
Function used to set the initial set of urls and metadata that is used when running the scraping part of the spider.

Sets 'start_urls', 'crawl_selections' using 'fund_data' that was set upon spider initialization

 --- start_requests ---
Iterates through 'crawl_selections' and initiates a crawling operation for all url-function pairs in the list.
The idea is that 'url' specifies the page to go to and 'parse_select' specifies the function to run (specified in callback)

'''
