import pymongo

# This is the URI used to authenticate and connect to the database
MONGODB_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
# This is the name of the 'database'
MONGODB_DB = "SuperScrapper"
# These are collection names(currently in database)
MONGODB_COLLECTIONS = ["funds","offerings"]

''' --- Needs possible updating --- '''

'''

Before using this scipt:
    - You will need to have pymongo installed
    - You will need to have dnspython installed

    To install these use:
        conda install pymongo
        conda install dnspython


In order to use this setup you must make sure that you have the following setup on the atlas database:
    - An account - You can use the test account I have setup already 'bot-test-user'
    - The account password - This is given when an account is created, in this case you can use the one for the test bot already here 'bot-test-password'
    - Your IP is allowed on the whitelist. Depending on the authentication you will need to add your ip to the whitelist.
        This can be done by navigating to 'Security' - 'Network Access' and clicking 'ADD IP ADDRESS' add your ip.
        If you create a different database access user then this will be part of the process.
    - If you want to creat your own account for access go to 'Security' - 'Database Access' and click 'ADD NEW DATABASE USER' and pick an authentication method
        The most simple form of authentication is the password method, that method is used here.
'''


class SuperDataMongodb:

    # NOTE: THIS DOES NOT CURRENTLY WORK, JUST PROOF
    collection_name = 'funds'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def open_spider(self):
        self.client = pymongo.MongoClient(self.mongo_uri, ssl = True)
        self.db = self.client[self.mongo_db]

    def close_spider(self):
        self.client.close()

    def do_thing(self):
        self.db[self.collection_name].insert_one({'hmmmm':123})
        return
# --


new_mongo = SuperDataMongodb(MONGODB_URI,MONGODB_DB)
new_mongo.open_spider()
new_mongo.do_thing()
new_mongo.close_spider()












# --
