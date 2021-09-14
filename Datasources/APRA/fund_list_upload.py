from mongo_connector import Connect

client = Connect.get_connection()
db = client['Fundlist']

map_json_collections = {
'Eligible Rollover Funds':'eligible_rollover_funds',
'List of Licensee':'list_of_licensee',
'List of RSE':'list_of_RSE',
'MySuper Products':'mysuper_products',
}

uri = lambda basename: f"./fund_list/{basename}.json"
file_reader = lambda uri: open(uri, 'r')

import json

keys = map_json_collections.keys()
uris = map(uri, keys)
try:
    readers = map(file_reader, uris)
    readers = list(readers)
except FileNotFoundError as e:
    print(f'File {e.filename} not found, exit')
    exit()

jsons = map(json.load, readers)
collection_names = map(map_json_collections.get, keys)
map_content_where = zip(jsons, collection_names)

for (j, collection_name) in map_content_where:
    collection = db[collection_name]
    print(f'Inserting {collection_name}')
    collection.insert_many(j)

client.close()