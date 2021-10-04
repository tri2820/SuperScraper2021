# Scrapy Scraper



## Installation

### Installation - Standalone

###### 1. Download

Download and unzip the file.


###### 2. Run install .bat or .sh

--(Windows)--

Go to /install and run:
``` install.bat ```

Wait until it says it is finished

--(MacOSx)--

Go to /install and run:
``` install.sh ```

Wait until it says it is finished

###### 3. Running program

Go to the main directory and run:
``` run_program.bat ```


### Installation - Dev

The following consists of very basic instructions.

###### 1. Setup git

Download the project through bitbucket / scourcetree, pull, ect...

###### 2. Run install .bat or .sh

--(Windows)--

Go to /install and run:
``` install.bat ```

Wait until it says it is finished

--(MacOSx)--

Go to /install and run:
``` install.sh ```

Wait until it says it is finished

###### 3. Running program

There are several methods to run the scraper.

###### (1) - Run file
Go to the main directory and run:
``` run_program.bat ```

###### (2) - Command Line - Relative (Windows)

Using cmd or other command line equivelent, change directory (cd) to the project.
After this run the following command.

Full argument:

```install\\python_install\\python scraper_run.py```

If you are working with the scraper it is probably important that you understand what this is doing.
The command consists of 2 parts, the path to the python executable and the path to the python(.py) file to run.

1st part:

```install\\python_install\\python ```

2nd part:

```scraper_run.py```

In additon to this arguments may be added.

###### (3) - Python Install

###### Step 1 - Install python
While the program can be run using the relative isntallation, this does not leand itself well to development as
for example you cannot easily install additional libaries.

Install python, if you dont know how look it up https://www.python.org/

###### Step 1.5 (optional) - Setup a vertual environment

--

###### Step 2 - Install the required libaries

Using command line / terminal (macOS) cd to the install directory and install the reqirments.txt

```pip install -r requirements.txt```


###### Step 3 - Run

Now you can run the scraper aswell as other files in the project.

```python {name of file you want to run}```

You probably know what you are doing.




























### How Scrapy Works - ish (WIP)
The spiders folder is where more individual logic and code for both broad crawl spiders and per website scraping is held.
A new spider can be made by just copying the code of one to a new file and changing the requisite values. You can then work from there.


##### 'spiderdatautils.py'
is a utilities file with some functions for scraping and dataprocessing.

##### 'settings.py'
its settings for scrapy.

##### 'piplines.py'
this is where data coming out of the spiders is handled and manipulated.
It is basically the next step after data is collected by a spider.
Once a spider has finished scraping, pipelines processes and filters the data and then uploads it to the database.


##### 'middlewares.py'
the middlewares file is responsable for the 'connection' and 'content' that are retrived when a website is visited.
Normally a scraper visits a website and just grabs the first version of the page that exists, this is a problem however.
The reason this is a problem, is because sometimes there is dynamic content (content that is loaded with javascript run on your end or server stuff)
that is not loaded when just retriving the page scource.

The solution to this is to load the page in a similar way to if you opened it yourself on your browser. This involves a different web scraler libary called selenium.
Selenium docs: https://selenium-python.readthedocs.io/


Selenium is different to scrapy because it uses a webdriver, in this case chrome.

To understand Selenium I recommend setting up a test project and following the getting started page in the docs: https://selenium-python.readthedocs.io/getting-started.html
Additonally you must have google chrome installed and must ensure the version of chrome matches the chromedriver/chromedriver.exe file in the ``` install\chrome_driver ``` directoty,
if you are getting version errors you can swap that chromedriver file out here: https://chromedriver.chromium.org/downloads

So using this driver, instead of scrapy requesting the web page, scrapy asks the Selenium driver code in middlewares to load the page,
then the middlewares gives the loaded page back to scrapy.

To learn more about dowloader middlewares: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html



### How pdf-extraction works - ish (WIP)

'nn_extraction.py' this is the runtime code for the nueral network. There is an entire explination (WIP)

'pdf_extraction.py' this is the runtime code for the pdf extraction. There is an entire explination (WIP)
