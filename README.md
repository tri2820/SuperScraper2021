# Super Scrapper

###### -- Team Members Please Read --

#### Recommendations / Idea for Doing Stuff

###### -- Python and the Environment --

If you are going to use python and by extension if you are going to use the crawler, I highly recommend setting up a seperate virtual invironment.
This goes doubly so if if you want to do stuff with the crawler and the libaries surrounding it. The reason for this is because scrapy
(the crawling framework we are using) is a framework and likes to setup its own things.

Additionally if you are using any of the python stuff here, it is using anaconda. Use anaconda.

Creating an environment is simple.
	- Open your anaconda prompt console.
	- Enter: conda create --name YOUR_ENVIRONMENT_NAME_HERE

Using an environment.
	- Exit current environment: conda deactivate
	- Enter different environment: conda activate YOUR_ENVIRONMENT_NAME_HERE
	- See all current environments: conda env list
	- To install a python libary in an environment:
		- Make sure you are in the environment you want to be in.
		- Enter: conda install 'THE_NAME_OF_THE_PYTHON_LIBARY'

Even if you dont use or want to do stuff with the spider or python connection with the datbase directly
you still may need to run this stuff later down the track. It may be helpful to set this up, I seriously promise its simple (90% of the time).

If you want to set it up but are unsure or want claification ask Hamish.

### Structure

Currently the repo is structured with a database file and a scraper file.
If you want to setup different stuff and change things around go ahead. This is by all means just an inital setup.
The scraper file contains an instance of a scrapy project, this file structrure is important to the scraper operation, ask if you want to shift stuff in it around.

At some point it would be nice to add some other sections for and if we build UI/UX and other software.

If you want to add something for upskilling or example puposes I think for now just upload it, if its a test file it may be useful for others.

If you know how things should probably be structured please tell me so i can take that into account.

### Examples

###### -- Database example --

A python file that runs a basic mongodb connection operation and explains how to setup database interaction

###### -- Scraper Setup --

An exmplination on how to setup scraper stuff


### Instructions

For instructions concering the database use the example above.

Hamish(me) will be adding some stuff on how to setup and use the scraper

Ask if you want to know how to do anything or use anything.



### Links

Add some if you want

Scrapy Docs: https://docs.scrapy.org/en/latest/index.html










