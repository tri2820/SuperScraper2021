from pymongo import MongoClient
from urllib.parse import quote

class Connect(object):
    @staticmethod    
    def get_connection():
        MONGODB_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
        return MongoClient(MONGODB_URI, ssl = True)

client = Connect.get_connection()
db = client['APRAseries']

collection = db['fund_level_profile_and_structure']
item_details = collection.find()
for item in item_details:
    print(item)


map_json_collections = {
'table6':'activity_fees_disclosed_mysuper_products',
'table5':'administration_fee_levels_mysuper_products',
'table4':'investment_fee_levels_lifecycle_stages',
'table3':'mysuper_fees_disclosed_mysuper_products',
'table7':'mysuper_insurance_premiums_disclosed_mysuper_products',
'table1b': 'profile_return_target_and_asset_allocation_targets_and_ranges_lifecycle_stages',
'table1a': 'profile_return_target_and_asset_allocation_targets_and_ranges_mysuper_products',
'table2b': 'representative_member_investment_performance_lifecycle_stages',
'table2a': 'representative_member_investment_performance_mysuper_products_with_single_investment_strategy'
}

import json
for file in map_json_collections.keys():
    uri = f"./quarterly_series/{file}.json"
    try:
        f = open(uri, 'r')
    except FileNotFoundError as e:
        print(f'File {e.filename} not found, skip')
        continue

    j = json.load(f)

    collection_name = map_json_collections[file]
    collection = db[collection_name]
    print(f'Inserting {file} -> {collection_name}')
    collection.insert_many(j)

client.close()
