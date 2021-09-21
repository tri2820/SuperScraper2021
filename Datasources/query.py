# python query.py

from mongo_connector import Connect
from itertools import product
import json
from bson import json_util


def make_fuzzy_query(possible_keys, possible_values):
    morphims = product(possible_keys, possible_values)
    query_items = map(lambda m: {m[0]:m[1]}, morphims)
    or_query = {'$or': list(query_items)}
    return or_query

"""
Query in all collections of a database
"""
def find_by(db, query):
    collection_names = db.list_collection_names()
    document = {}

    for collection_name in collection_names:
        qresult = db[collection_name].find(query)
        qresult = list(qresult)
        if qresult:
            document[collection_name] = qresult
    return document

"""
Query in multiple databases
"""    
def find_all_by(query, database_names):
    client = Connect.get_connection()
    result = {}
    for database_name in database_names:
        db = client[database_name]
        dbresult = find_by(db, query)
        if dbresult: result[database_name] = dbresult
    client.close()
    return result

if __name__ == '__main__':
    query = make_fuzzy_query(['ABN', 'Fund ABN', 'Group 2.ABN', 'Group 5.ABN', 'Group 6.ABN', 'Group 7.ABN'], [90194410365, "90194410365"])
    database_names = ['Fundlist','APRA', 'APRAseries']
    result = find_all_by(query, database_names)

    f = open(f"query_result.json", 'w')
    content = json.dumps(result, sort_keys=True, indent=4, default=json_util.default)
    f.write(content)
    f.close()