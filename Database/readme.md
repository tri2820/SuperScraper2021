# Super Scraper Database
## Outline
We use MongoDB, specifically the Atlas offering (due to free tier and access). See a Senior team member if you don't have access. We use MongoDB because as it stores data effectively as JSON, it is easier to manipulate and play with in Python, as well as being more suited to this structure.

Each Collection holds specific information, and each document inside those collections is specific to one fund, or fund offeirng.
## Collection Details
### fund_managers
***To Do***
### funds
This Collection contains the data about the Superannuation Funds that we track performance of, each fund is in its own Document
* `_id` : String; A Fund Identifier to use across documents
* `name` : String; The name of the fund
* `website` : String; the URL of the website
* `super_performance` : String; URL of specifically their super performance
* `metadata` : Object; Contains data that helps power the 
    * `crawl_objects` : Array; specific details for the web crawling
         *  `url_variables` : Array; contains the URL variables and values to access
         * `parse_select` : String; Period data to get
### offerings
This Collection stores the data for each funds superannuation offerings; each offering gets its own Document
* `_id` : String; Specific identifier for the offering. Usually `fund_offeringName` or similar
* `fund_id` : String; Identifier for the fund this offering belongs to
* `name` : String; The name of the offering
* `monthly_performances` : Array; Contains entries for each month that data exists for. Each entry is an object in the form of:
    * `Date` : String, the month this data refers to. Uses structure of `YYYY-MM`
    * `Value` : Decimal number; The percentage growth reported for that month
* `historial_performances` : Array; contains entries of standard historical periods and the growth recorded, in the form of:
    * `Date` : String; identifies the historical period
    * `Value` : Decminal; The recorded growth for the period
* `costs_fees` : Array; Stores information for the fees associated with this offering
    * `Cost_Type` : String; Description of the fee
    * `Value` : Fee as a percentage value
* `allocations` : Array; contains the types of investments and how much of it (***to do***)
* `inception` : String; The reported date that the fund began
* `metadata` : Object; contains data to asist the scraper
    * `table_strings` : Array; contains any previous names for the offering, allowing us to join the data into one continuous stream
### site_traverse_data
***in progress***
## Examples
### Connect To MongoDB
*To do this with Python, make sure you `pip install pymongo` and `include pymongo` in your code*

1. Establish the client connection, in this case using the **extractor** user details
    - `client = pymongo.MongoClient("mongodb+srv://extractor:I62EK5HE5yBL59Yz@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority")`

2. Specify the database to access
    - `db = client.SuperScrapper`

3. Then, specify the exact collection you want ot access
    - `fundCollection = db.funds`
    - `offeringCollection = db.offerings`

### Get All Funds
This will give you a list (`[x, y, z]`) of all documents in the collection, with each entry in the list being a json object you can access

`funds = list(fundCollection.find())`
### Filter Search Results
With pymongo, you can specify the exact attributes you want to retrieve, like the `SELECT` feature in SQL queries

To get only the fund identifier, name, and monthly performances of all Hesta offerings, you need to specify the key search criteria (`"fund_id" : "hesta"`) and then the filter
```
offerings = list(offeringCollection.find(
    {"fund_id": "hesta"},
    {'fund_id' : 1, 'name' : 1, 'monthly_performances' : 1}
    ))
```
## Imagery
Concept for how the database would be designed. We stuck to this, and have expanded it, but it demonstrates where we started from. Dummy data on the left, more theoretical explanation on the right.

![mongooDB Diagrams](mongo_mockup.png)

This is what the Mongo Atlas interface looks like, with the collections on the left, various data visible across the display

![MongoDB Atlas Interface](mongo_example.jpg)