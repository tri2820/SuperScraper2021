from pymongo import MongoClient

class Connect(object):
    @staticmethod    
    def get_connection():
        MONGODB_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
        return MongoClient(MONGODB_URI, ssl = True)
