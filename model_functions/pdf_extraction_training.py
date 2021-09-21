
from types import LambdaType
import dateparser
import datetime

import re

import camelot

# --- This may be useful
# NOTE: https://github.com/python/cpython/blob/main/Lib/difflib.py
from difflib import SequenceMatcher
# ---
#pip install nltk
# TODO: nltk will need the dwnload things, me do later

import nltk.data as nltk_data
#nltk.data.path.append('./test_nltk')
nltk_data.path.append('./install/nltk_data')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ---

import PyPDF2

import pandas as pd

#import matplotlib.pyplot as plt

from operator import itemgetter


from Scraper.nn_extraction import run_pdf_table_detection, pdf_to_images

#from nn_extraction import run_pdf_table_detection

import os


import pdfplumber


import io

import requests

import math

from scipy import stats as sci_stats


import numpy as np

import json

import pymongo

# https://bitbucket-students.deakin.edu.au/scm/webmc-ug/super-scrapper.git


'''
Below are some funds and the corrisponding links to the pdfs, i dont think we dont want to be uploading pdfs to the bitbucket, so download them and then move them out when uploading or something
https://www.pendalgroup.com/products/pendal-australian-share-fund/ : https://www.pendalgroup.com/wp-content/uploads/docs/factsheets/PDS/Pendal%20Australian%20Share%20Fund%20-%20PDS.pdf?v=2021-05-061620317117
https://www.hyperion.com.au/hyperion-australian-growth-companies-fund/ : https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf
https://www.fidelity.com.au/funds/fidelity-australian-equities-fund/ : https://www.fidelity.com.au/funds/fidelity-australian-equities-fund/related-documents/product-disclosure-statement/
https://www.vanguard.com.au/adviser/products/en/detail/wholesale/8100/equity : https://www.vanguard.com.au/adviser/products/documents/8189/AU
'''


# NOTE: Tutorial from: https://www.geeksforgeeks.org/python-measure-similarity-between-two-sentences-using-cosine-similarity/
# NOTE: Natural Language Processing tool kit is a great rescource for looking for stuff like this: https://www.nltk.org/
# NOTE: This should be a bit better than the basic sequence matcher

def cosine_similarity(string_1, string_2, ommit=[]):

	remove_symbols_1 = re.sub('[^\w ]+|[_]+',' ',string_1 + '')
	remove_symbols_2 = re.sub('[^\w ]+|[_]+',' ',string_2 + '')

	token_1 = word_tokenize(remove_symbols_1)
	token_2 = word_tokenize(remove_symbols_2)

	# If invalide
	if len(token_1) == 0 or len(token_2) == 0:
		return 0.0

	# Ommits common words that are not useful
	sw = stopwords.words('english')
	l1 =[];l2 =[]
	# Remove stop words from the string
	set_1 = {w for w in token_1 if not w in sw}
	set_2 = {w for w in token_2 if not w in sw}

	# Form a set containing keywords of both strings
	rvector = set_1.union(set_2)
	for w in rvector:
		if w in set_1:
			l1.append(1)
		else:
			l1.append(0)
		if w in set_2:
			l2.append(1)
		else:
			l2.append(0)
	c = 0
	
	# Cosine
	for i in range(len(rvector)):
		c+= l1[i]*l2[i]
	divisor = float((sum(l1)*sum(l2))**0.5)
	cosine = 0
	if divisor != 0:
		cosine = c / float((sum(l1)*sum(l2))**0.5)
	return cosine
# --


#tables = camelot.read_pdf("https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf",pages = 'all', flavor = 'stream',flag_size=True)


class StringTest:

	url_string = ""
	text = ""

	def __init__(self, url_string_):
		self.url_string = url_string_


	def extract_text(self, lower = False):
		r = requests.get(self.url_string)
		f = io.BytesIO(r.content)

		pdfReader = None
		try:
			#pdfReader = PyPDF2.PdfFileReader(f)#,strict=False
			pdfReader = pdfplumber.open(f)
		except:
			print('Failed String Test')
			return
		#print(pdfReader.numPages)
		self.text = ""

		#for page in pdfReader.pages:
		#	self.text += page.extractText()
		# --
		for page in pdfReader.pages:
			more_text = page.extract_text(x_tolerance=1, y_tolerance=1)
			if more_text:
				self.text += more_text
		if lower:
			self.text = self.text.lower()
		#text_file = open("pdf_texts.txt", "w")
		#text_file.write(self.url_string)
		#text_file.close()


	def test_for_string(self, test_string, regex_ = False, amount = None):
		found = False
		text = self.text
		if amount:
			text = self.text[:amount]
		if regex_:
			found = re.search(test_string, text)
		else:
			found = text.find(test_string) != -1
		return found

# --


# NOTE: This numerics/symbols regex weight function will allow stuff like 23, %, /, ^3, @#421-3, +, - to be given increased or decreased wieghts

def pattern_weights(in_string, regex_list):
	weight = 0
	for pattern in regex_list:
		if re.search(pattern[0], in_string) != None:
			weight += pattern[1]
	# --
	return weight




def find_most_similar(string_, compare_values_, use_cosine=True, use_weights=True):
	"""
	returns: ('string that was being tested', 'catagory string that matched highest', ratio of similarity)
	"""
	#highest_match = ["","",0]
	highest_match = {
		"str": "",
		"cat": None,
		"match": "",
		"ratio": 0,
	}
	similarity_list = []
	for cat_name in compare_values_:#compare_string_list_
		catagory = compare_values_[cat_name]
		for compare_name in catagory["compare"]:
			item = catagory["compare"][compare_name]

			ratio_sequence = SequenceMatcher(None,compare_name.lower(),string_.lower()).ratio()
			ratio_cosine = cosine_similarity(compare_name.lower(), string_.lower())

			ratio_ = ratio_sequence
			if use_cosine:
				ratio_ = (ratio_sequence * 0.35) + ratio_cosine
			# --

			if use_weights:
				regex_list = item["weights"]
				symbols_weight = pattern_weights(string_.lower(), regex_list)
				ratio_ += ratio_ * symbols_weight
				ratio_ += ratio_ * item["bias"]
			# --


			#match_info = [string_, compare_name, ratio_]
			match_info = {
				"str": string_,
				"cat": cat_name,
				"match": compare_name,
				"ratio": ratio_,
			}
			similarity_list.append(match_info)

	for match_info in similarity_list:
		if match_info["ratio"] > highest_match["ratio"]:
			highest_match = match_info
	return highest_match




def find_similar(string_, cat_name, catagory, use_cosine=True, use_weights=True):
	"""
	returns: ('string that was being tested', 'catagory string that matched highest', ratio of similarity)
	"""
	#highest_match = ["","",0]
	highest_match = {
		"str": None,
		"cat": None,
		"match": None,
		"ratio": 0,
	}
	similarity_list = []
	#for cat_name in compare_values_:#compare_string_list_
	#catagory = compare_values_[cat_name]
	for compare_name in catagory["compare"]:
		item = catagory["compare"][compare_name]

		ratio_sequence = SequenceMatcher(None,compare_name.lower(),string_.lower()).ratio()
		ratio_cosine = cosine_similarity(compare_name.lower(), string_.lower())

		ratio_ = ratio_sequence
		if use_cosine:
			ratio_ = (ratio_sequence * 0.35) + ratio_cosine
		# --

		if use_weights:
			regex_list = item["weights"]
			symbols_weight = pattern_weights(string_.lower(), regex_list)
			ratio_ += ratio_ * symbols_weight
			ratio_ += ratio_ * item["bias"]
		# --


		#match_info = [string_, compare_name, ratio_]
		match_info = {
			"str": string_,
			"cat": cat_name,
			"match": compare_name,
			"ratio": ratio_,
		}
		similarity_list.append(match_info)

	for match_info in similarity_list:
		if match_info["ratio"] > highest_match["ratio"]:
			highest_match = match_info
	return highest_match








def font_size_filter(in_object):
	success = True
	if 'size' in in_object:
		font_size = in_object['size']
		if font_size < 6:
			success = False
	# --
	return success
# --


class DocumentExtraction:
	url_string = ''
	"""
	table_areas: {'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])], 'conf': conf, 'class': names[c]}
	"""

	def __init__(self, url_string_, save_iamges=False):
		self.url_string = url_string_
		self.save_iamges = save_iamges

		# Instance variables
		self.detected_tables = []
		self.doc_pages = []

	def detect_tables(self):
		page_table_detections = run_pdf_table_detection(self.url_string, self.save_iamges)
		print(len(page_table_detections))
		self.detected_tables = page_table_detections

	def extract_tables(self):
		# Use nueral network to detect tables
		self.detect_tables()
		# Make sure to reset data to avoid repeats
		self.doc_pages = []

		r = requests.get(self.url_string)
		f = io.BytesIO(r.content)

		# This is the pixel resolution, pdfplumber uses 72
		local_dpi = 72
		# If you change this, go look at the nn_extraction and change the dpi there as well
		global_dpi = 200

		with pdfplumber.open(f) as pdf:
			# Get pdf initial page size
			first_page = pdf.pages[0]
			#print("\n\n -- FIRST PAGE WIDTH: ",first_page.width)
			print('PDF Size: ', (first_page.width,first_page.height))

			for page_tables in self.detected_tables:
				
				pg_no = page_tables['page_number']

				if len(pdf.pages) - 1 < pg_no:
					print('\n\n\n --- PAGE NUMBER NOT RETRIVED! --- \n\n\n')
					continue

				page_ = pdf.pages[pg_no]
				page_ = page_.filter(font_size_filter)
				new_page = DocPage(page_, pg_no, page_tables)
				res_ = new_page.extract_data()
				if res_ == 'page':
					return True
				elif res_ == 'fund':
					return 'fund'

				self.doc_pages.append(new_page)

		return True
# --

MONGO_URI = "mongodb+srv://bot-test-user:bot-test-password@cluster0.tadma.mongodb.net/cluster0?retryWrites=true&w=majority"
MONGO_DB = "SuperScrapper"


class DBHandler:

	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db

	def open_connection(self):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]


	def close_connection(self):
		self.client.close()


	def get_collection_ids(self, collection_name_):
		ids_list = [str(x) for x in self.db[collection_name_].find().distinct('_id')]
		return ids_list


	def find_or_create_document(self, collection_name_, data_object, overwrite=False):
		query = {'_id' : data_object['_id']}
		print(type(collection_name_))
		document = self.db[collection_name_].find_one(query)
		# If none create one
		if document == None:
			self.db[collection_name_].insert_one(data_object)
			document = self.db[collection_name_].find_one(query)
		elif overwrite == True:
			self.db[collection_name_].update_one(query, {"$set": data_object})
		# --
		return document


class Something:

	def extract_document_data(self, url):
		# Extract doc
		doc_extract = DocumentExtraction(url, save_iamges=False)
		res_ = doc_extract.extract_tables()
		if res_ == 'fund':
			return 'fund'
		else:
			return True
	
	def extract_data_from_documents(self, collection_id = 'fund_managers', custom_query=None):

		#self.docExtractor = DocumentDataExtractor()

		# Extract doc
		#doc_extract = DocumentExtraction("https://www.benthamam.com.au/assets/fundreports/20210630-GIF-Monthly-Report.pdf", save_iamges=True)
		#doc_extract.extract_tables()

		# Add extracted doc to handler
		#last_doc_idx = self.docExtractor.add_document(doc_extract)
		#return

		test_handler = DBHandler(MONGO_URI, MONGO_DB)
		test_handler.open_connection()
		fund_ids = test_handler.get_collection_ids(collection_id)

		item_querys = [[x, test_handler.find_or_create_document(collection_id, {'_id': x}, False)['metadata']['site_traversal_id']] for x in fund_ids]

		#item_querys = [["CSA0038AU",test_handler.find_or_create_document(collection_id, {'_id': "CSA0038AU"}, False)['metadata']['site_traversal_id']]]

		if custom_query:
			item_querys = [[custom_query,test_handler.find_or_create_document(collection_id, {'_id': custom_query}, False)['metadata']['site_traversal_id']]]


		test_handler.close_connection()
		count = 0

		for item_query in item_querys:
			#count += 1
			#if count < 5:
			#    continue

			

			item_id = item_query[0]

			print(f'\n-- {item_id} --\n')

			traversal_id = item_query[1]

			test_handler.open_connection()

			item = test_handler.find_or_create_document(collection_id, {'_id': item_id}, False)

			test_handler.close_connection()

			file_url_list = item['metadata']['pdf_url_list']

			for file_idx, file_url_data in enumerate(file_url_list):
				res_ = self.extract_document_data(file_url_data['url'])
				if res_ == 'fund':
					break
		# --

			



# TODO: add datatype biasing to 'compare_catargories' eg: prefers % preferes + - / ()

class DocumentDataExtractor:
	documents = []

	'''
	compare_values = {
		#[['[+\\$\-\%]',0.75],['\d',0.9]]
		"Management Fee": {
			"fees cost expenses management": {
				"weights": [['[+\\$\-\%]',0.75],['\d',0.9],['p.a',1.6]],
				"bias": 0
			},
			"management fee": {
				"weights": [['[+\\$\-\%]',0.75],['\d',0.9],['p.a',1.6]],
				"bias": 0.2
			},
		},
		"Buy/Sell spread": {
			"buy sell spread": {
				"weights": [['[+\\$\-\%]',0.75],['\d',0.9],['[\+\d.%]+ ?\/ ?\-[\d.%]+',2]],# '\+.+%.+\/.+\-.+%'
				"bias": 0.2
			},
			"transaction costs allowance": {
				"weights": [['[+\\$\-\%]',0.75],['\d',0.9],['[\+\d.%]+ ?\/ ?\-[\d.%]+',2]],# '\+.+%.+\/.+\-.+%'
				"bias": 0
			},
		},
		"Asset Allocation": {
			"asset allocation range": {
				"weights": [['[\-\%]',0.45],['\d',0.9], ['strategic', 0.1]],
				"bias": 0
			}
		}
	}
	'''

	extraction_params = {
		"Management Fee": {
			"compare": {
				"management fee": {
					"weights": [['[+\\$\-\%]',0.3], ['\d',0.9], ['management', 1], ['performance', -1], ['\%', 0.1], ['p.a', 0.5]],
					"bias": 0.2
				},
				"management cost": {
					"weights": [['[+\\$\-\%]',0.3], ['\d',0.9], ['management', 1], ['performance', -1], ['\%', 0.1], ['p.a', 0.5]],
					"bias": 0.2
				},
			},
			"args": {
			}
		},
		"Performance Fee": {
			"compare": {
				"performance fee": {
					"weights": [['[+\\$\-\%]',0.3], ['\d',0.9], ['management', -1], ['performance', 1], ['\%', 0.1], ['p.a', 0.5]],
					"bias": 0.2
				},
				"performance cost": {
					"weights": [['[+\\$\-\%]',0.3], ['\d',0.9], ['management', -1], ['performance', 1], ['\%', 0.1], ['p.a', 0.5]],
					"bias": 0.2
				},
			},
			"args": {
			}
		},
		"Buy/Sell spread": {
			"compare": {
				"buy sell spread": {
					"weights": [['[+\\$\-\%]',0.3],['\d',0.9],['[\+\d.%]+ ?\/ ?\-[\d.%]+|\++ ?[\d.%]* ?\/ ?\- ?[\d.%]*',2]],# '\+.+%.+\/.+\-.+%'
					"bias": 0.2
				},
				"transaction costs allowance": {
					"weights": [['[+\\$\-\%]',0.3],['\d',0.9],['[\+\d.%]+ ?\/ ?\-[\d.%]+|\++ ?[\d.%]* ?\/ ?\- ?[\d.%]*',2]],# '\+.+%.+\/.+\-.+%'
					"bias": 0
				},
			},
			"args": {
			}
		},
		"NAV": {
			"compare": {
				"nav": {
					"weights": [['\d',0.9]],# '\+.+%.+\/.+\-.+%'
					"bias": 0
				},
				"net asset value": {
					"weights": [['\d',0.9]],# '\+.+%.+\/.+\-.+%'
					"bias": 0.5
				},
			},
			"args": {
			}
		},
		"Class Size": {
			"compare": {
				"class size": {
					"weights": [['\d',0.9], ['size', 0.5], ['\$', 0.6], ['AUD|USD|A\$',1.2], ['million|billion', 1.2]],# '\+.+%.+\/.+\-.+%'
					"bias": 0.2
				}
			},
			"args": {
			}
		},
		"Fund Size": {
			"compare": {
				"fund size": {
					"weights": [['\d',0.9], ['size', 0.5], ['\$', 0.6], ['AUD|USD|A\$',1.2], ['million|billion', 1.2]],# '\+.+%.+\/.+\-.+%'
					"bias": 0.2
				}
			},
			"args": {
			}
		},
		"Strategy Size": {
			"compare": {
				"strategy size": {
					"weights": [['\d',0.9], ['size', 0.5], ['\$', 0.6], ['AUD|USD|A\$',1.2], ['million|billion', 1.2]],# '\+.+%.+\/.+\-.+%'
					"bias": 0.2
				}
			},
			"args": {
			}
		},
		
	}

	extraction_params_tables = {
		"Asset Allocation": {
			"compare": {
				"portfolio asset allocation": {
					"weights": [['\d',0.9], ['strategic', 0.3], ['asset class| asset allocation', 1.2], ['\%', 0.1], ['range', 0.2]],
					"bias": 0
				},
				"sector allocation": {
					"weights": [['\d',0.9], ['strategic', 0.3], ['asset class| asset allocation', 1.2], ['\%', 0.1], ['range', 0.2]],
					"bias": 0
				},
			},
			"args": {
				"table": {
					"top_regex": [
						'portfolio|allocation|asset|sector'
					],
					"search_regex": [
						{
							'search': 'portfolio|allocation',
							'label': 'asset_allocation',
							#'search': lambda item:
						},
						{
							'search': 'asset|sector',
							'label': 'asset_allocation',
							#'search': lambda item:
						}
					],
				}
			}
		},
		"Top Holdings": {
			"compare": {
				"top holdings": {
					"weights": [['\d',0.9], ['top 10', 0.5], ['top 5', 0.5], ['holding', 0.2]],
					"bias": 0
				},
			},
			"args": {
				"table": {
					"top_regex": [
						'holding'
					],
					"search_regex": [
						{
							'search': 'holding',
							'label': 'holdings',
							#'search': lambda item:
						}
					],
				}
			}
		},
		"Performance": {
			"compare": {
				"performance": {
					"weights": [['\d',0.9], ['month', 0.5], ['benchmark', 0.8], ['net', 0.5], ['fund perform', 0.9]],
					"bias": 0
				},
			},
			"args": {
				"table": {
					"top_regex": [
						'performance'
					],
					"search_regex": [
						{
							'search': 'performance',
							'label': 'performance',
							#'search': lambda item:
						}
					],
				}
			}
		},
		"FeesCosts_Table": {
			"compare": {
				"fee cost": {
					"weights": [['\d',0.9], ['management', 0.5], ['performance', 0.5], ['\%', 0.1], ['p.a', 0.5], ['type', 0.5]],
					"bias": 0
				},
				"management cost": {
					"weights": [['\d',0.9], ['management', 0.5], ['performance', 0.5], ['\%', 0.1], ['p.a', 0.5], ['type', 0.5]],
					"bias": 0
				},
			},
			"args": {
				"table": {
					"top_regex": [
						'fee|cost|expense'
					],
					"search_regex": [
						{
							'search': 'fee|cost|expense',
							'label': 'fee_cost_table',
							#'search': lambda item:
						},
					],
				}
			}
		},
	}

	discard_indicators = ['example']

	similarity_data = {}

	def __init__(self):

		for cat_name in self.extraction_params:#compare_values
			self.similarity_data[cat_name] = []


		return

	def process_document_data(self):
		pass

	def add_document(self, document):
		#document.url_string
		#document.pages_data
		document_obj = {
			#'url': document.url_string,
			#'pages_data': document.pages_data,
			'doc': document,
			'sim_data': {}
		}
		self.documents.append(document_obj)
		return len(self.documents) - 1
	
	def extract_similar_rows(self, init_threshold, doc_idx=0):

		#for compare_value in self.compare_string_list:
		#	self.similarity_data[compare_value] = []

		document_data = self.documents[doc_idx]

		# Init catagories for document data
		for cat_name in self.extraction_params:#compare_values
			if not cat_name in document_data['sim_data']:
				document_data['sim_data'][cat_name] = []
		
		# Init catagories for document data
		for cat_name in self.extraction_params_tables:#compare_values
			if not cat_name in document_data['sim_data']:
				document_data['sim_data'][cat_name] = []
		
		'''
				self.page_number = page_number

				self.bbox = bbox

				self.size = 0

				self.page_ = page_

				self.word_lines = {}
				self.table_collections = []

				self.ext_data = {
					'text_top': '',
					'text_bottom': '',
				}

				self.text = ''
		'''

		# Extract infomation from tables
		document = document_data['doc']
		for page_idx, page in enumerate(document.doc_pages):#pages_data
			for table_idx, table in enumerate(page.tables):#page['tables']


				table_ext_data = table.ext_data

				
				# Text based on sentence blob and ending-ness
				text_raw = table.text
				raw_texts = re.split("\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n|\\n\\n",text_raw)
				raw_texts = [re.sub("\\n[\w\d]\\n|\\n",' ',x) for x in raw_texts]

				word_lines = table.word_lines
				line_texts = [word_lines[idx]['text'] for idx in word_lines]
				#print(line_texts)

				#print(line_texts)

				# Look for discard indicaters
				discard_table = False
				for indicator in self.discard_indicators:
					if table.text.lower().find(indicator) != -1 or table_ext_data['text_top'].lower().find(indicator) != -1 or table_ext_data['text_bottom'].lower().find(indicator) != -1:
						discard_table = True
						break

				if discard_table:
					continue

				# Run matching for each catagory
				for text_part in raw_texts:
					for catagory_name in self.extraction_params:
						catagory = self.extraction_params[catagory_name]
						item = find_similar(text_part, catagory_name, catagory, True, True)

						if not item['cat']:
							continue

						#if "table" in self.extraction_params[item['cat']]['args']:
						#	item["table"] = table
						
						sim_val = item["ratio"]
						if sim_val > init_threshold:
							document_data['sim_data'][catagory_name].append(item)
				# --


				# Table similarity detection
				#text_above_table = table.ext_data['text_top']

				text_above_table = table.ext_data['text_top']


				# Run matching for each catagory
				for text_part in [text_above_table, text_raw]:
					for catagory_name in self.extraction_params_tables:
						catagory = self.extraction_params_tables[catagory_name]
						item = find_similar(text_part, catagory_name, catagory, True, True)

						if not item['cat']:
							continue

						if "table" in self.extraction_params_tables[item['cat']]['args']:
							item["table"] = table
						
						sim_val = item["ratio"]
						if sim_val > init_threshold:
							document_data['sim_data'][catagory_name].append(item)
				# --

				'''
				# Run matching for each catagory
				for text_part in raw_texts:
					for catagory_name in self.extraction_params_tables:
						catagory = self.extraction_params_tables[catagory_name]
						item = find_similar(text_part, catagory_name, catagory, True, True)

						if not item['cat']:
							continue

						if "table" in self.extraction_params_tables[item['cat']]['args']:
							item["table"] = table
						
						sim_val = item["ratio"]
						if sim_val > init_threshold:
							document_data['sim_data'][catagory_name].append(item)
				# --
				'''

				'''
				# Look for discard indicaters
				discard_table = False
				for indicator in self.discard_indicators:
					if table.text.lower().find(indicator) != -1 or table_ext_data['text_top'].lower().find(indicator) != -1 or table_ext_data['text_bottom'].lower().find(indicator) != -1:
						discard_table = True
						break
				
				if discard_table:
					continue

				for text_part in raw_texts:
					item = find_most_similar(text_part, self.extraction_params, True, True)

					if not item['cat']:
						continue

					if "table" in self.extraction_params[item['cat']]['args']:
						item["table"] = table
					
					sim_val = item["ratio"]
					if sim_val > init_threshold:
						document_data['sim_data'][item["cat"]].append(item)
				
				# --

				text_above_table = table.ext_data['text_top']

				#print(table.ext_data)

				#print('\n\n text_above_table: ', text_above_table)

				for cat_name in self.extraction_params_tables:
					cat = self.extraction_params_tables[cat_name]
					top_regex = cat["args"]["table"]["top_regex"]
					for regex_ in top_regex:
						search_ = re.search(regex_, text_above_table)
						if search_ == None:
							continue
						item = {
							"str": text_above_table,
							"cat": cat_name,
							"match": None,
							"ratio": 2,
							"table": table,
						}
						
						sim_val = item["ratio"]
						if sim_val > init_threshold:
							document_data['sim_data'][item["cat"]].append(item)
				'''
				'''
				for text_part in line_texts:
					item = find_most_similar(text_part, self.extraction_params_tables, True, True)

					if not item['cat']:
						continue

					if "table" in self.extraction_params_tables[item['cat']]['args']:
						item["table"] = table
					
					sim_val = item["ratio"]
					if sim_val > init_threshold:
						document_data['sim_data'][item["cat"]].append(item)
				'''
		# --

		# Get sub-tables
		for cat_name in self.extraction_params_tables:
			cat = self.extraction_params_tables[cat_name]
			if "table" in cat["args"]:
				table_args = cat["args"]["table"]

				item_list = document_data['sim_data'][cat_name]
				#item_list = sorted(item_list, key=lambda item: item["ratio"], reverse=True)

				item_table_list = []

				for idx, item in enumerate(item_list):
					table = item["table"]

					search_regex = table_args["search_regex"]

					table.search_for_subtables(search_regex)
					table.construct_subtables(3)
					table.format_subtables()

					df_list = table.create_subtable_dataframes()
					item["table"] = {}
					for df_ in df_list:
						df_dict = df_.to_json(orient='index')
						if not df_dict:
							continue
						df_dict = json.loads(df_dict)
						if len(df_dict) < 2:
							continue
						item["table"] = df_dict
						item["ratio"] += 5
						item_list[idx] = item
						item_table_list.append(item)
						break
				
				#item_list = sorted(item_list, key=lambda item: item["ratio"], reverse=True)

				document_data['sim_data'][cat_name] = item_table_list



		return
	



	
	def sort_as_most_similar(self, doc_idx):
		"""
		{
			"ratio": 0,
			"cat": "", catagory (similarity catagory)
			"str": "", string extracted
			"match": "", the regex string that matched for that catagory
		}
		"""

		similarity_data = self.documents[doc_idx]['sim_data']
		
		for sim_type in similarity_data:
			sim_values = similarity_data[sim_type]
			similarity_data[sim_type] = sorted(sim_values, key=lambda item: item["ratio"], reverse=True)

		return similarity_data

# --

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import cv2 as cv

from PIL import Image

class DocPage:

	def __init__(self, page_, page_number, page_tables):

		self.page_ = page_

		self.tables = []

		self.nn_tables = page_tables
		self.page_number = page_number

		self.text = ''

		# This is the pixel resolution, pdfplumber uses 72
		self.local_dpi = 72
		# If you change this, go look at the nn_extraction and change the dpi there as well
		self.global_dpi = 200

		return
	
	
	def extract_data(self):

		self.text = self.page_.extract_text(x_tolerance=1, y_tolerance=1)

		#self.page_.to_image(resolution=72).save("train_page.png", format="PNG")

		#print("\n\n -- PAGE WIDTH: ", self.page_.width)

		#for nn_table in self.nn_tables:
		table_areas = self.nn_tables['table_areas']#nn_table
		for table_area in table_areas:
			bbox = table_area['bbox']

			padding_table = 0
			xy1 = (int(bbox[0] - padding_table),int(bbox[1]) - padding_table)
			xy2 = (int(bbox[2] + padding_table),int(bbox[3]) + padding_table)

			dpi_ratio = self.local_dpi / self.global_dpi

			xy1 = (int(xy1[0] * dpi_ratio),int(xy1[1] * dpi_ratio))
			xy2 = (int(xy2[0] * dpi_ratio),int(xy2[1] * dpi_ratio))

			xy1 = (min(max(int(xy1[0]),0),int(self.page_.width)),min(max(int(xy1[1]),0),int(self.page_.height)))
			xy2 = (min(max(int(xy2[0]),0),int(self.page_.width)),min(max(int(xy2[1]),0),int(self.page_.height)))

			cropped_bbox = (xy1[0],xy1[1],xy2[0],xy2[1])
			# Get page table crop
			cropped_table = self.page_.crop(cropped_bbox, relative=False)

			'''
			print('-- TABLE MID --')

			cat_list = ['Allocation', 'Top_Holdings', 'Bot_Holdings', 'Performance', 'FeesCosts', 'Nothing']
			input_prompt = ''
			for idx, cat_ in enumerate(cat_list):
				input_prompt += f'({idx})-{cat_},'
				# Make dir if does not exist
				os.makedirs('data\\' + cat_, exist_ok=True)

			cropped_table.to_image(resolution=72).save("train_img.png", format="PNG")

			img_1 = cv.imread("train_img.png")
			img_2 = cv.imread("train_page.png")

			cv.imshow("img_1",img_1)
			cv.imshow("img_2",img_2)

			cv.waitKey(500)

			prompt_output = input(input_prompt)
			print(prompt_output)

			cv.destroyAllWindows()

			save_dir_prefix = 'data/' + cat_list[int(prompt_output)]

			lastnumber_ = 0
			try:
				while os.path.isfile(save_dir_prefix + "/" + str(lastnumber_) + "_" + prompt_output + ".txt"):
					lastnumber_ += 1
			except:
				print('--')
			'''

			
			
			new_table = self.add_table(cropped_bbox, cropped_table)

			new_table.extract_words()

			table_size = (xy2[0] - xy1[0], xy2[1] - xy1[1])
			new_table.size = table_size

			padding_horizontal = int(table_size[0] * 0.25)
			padding_vertical = int(table_size[1] * 0.25)

			around_top = (xy1[0] - padding_horizontal, xy1[1] - padding_vertical, xy2[0] + padding_horizontal, xy1[1])
			around_bottom = (xy1[0] - padding_horizontal, xy2[1], xy2[0] + padding_horizontal, xy2[1] + padding_vertical)

			around_top = (min(max(around_top[0],0),int(self.page_.width)), min(max(around_top[1],0),int(self.page_.height)), min(max(around_top[2],0),int(self.page_.width)), min(max(around_top[3],0),int(self.page_.height)))
			around_bottom = (min(max(around_bottom[0],0),int(self.page_.width)), min(max(around_bottom[1],0),int(self.page_.height)), min(max(around_bottom[2],0),int(self.page_.width)), min(max(around_bottom[3],0),int(self.page_.height)))

			table_ext_data = {
				'text_top': '',
				'text_bottom': '',
			}
			#print('---\n',around_top)
			#around_top = (around_top[0] + 1, around_top[1] - 1, around_top[2] - 1, around_top[3] + 1)
			#print(around_top,'\n---')

			#print(around_top[1] - around_top[3] > 1)
			# NOTE: I changed these around before
			try:
				if around_top[2] - around_top[0] > 1 and around_top[3] - around_top[1] > 1:
					table_top = self.page_.crop((around_top[0],around_top[1],around_top[2],around_top[3]), relative=False)
					table_ext_data['text_top'] = table_top.extract_text(x_tolerance=1, y_tolerance=1)
					if table_ext_data['text_top'] == None:
						table_ext_data['text_top'] = ''
					#table_top.to_image(resolution=200).save("table_top.png", format="PNG")
				if around_bottom[2] - around_bottom[0] > 1 and around_bottom[3] - around_bottom[1] > 1:#around_bottom[2] - around_bottom[0] > 1 and around_bottom[3] - around_bottom[1] > 1
					table_bottom = self.page_.crop((around_bottom[0],around_bottom[1],around_bottom[2],around_bottom[3]), relative=False)
					table_ext_data['text_bottom'] = table_bottom.extract_text(x_tolerance=1, y_tolerance=1)
					if table_ext_data['text_bottom'] == None:
						table_ext_data['text_bottom'] = ''
					#table_bottom.to_image(resolution=200).save("table_bottom.png", format="PNG")
			except:
				print('-- FAILED CROP -- ERROR: 999358')
			#print(table_ext_data)
			new_table.ext_data = table_ext_data




			print('\n\n ----------------- NEXT TABLE ----------------- ')
			print(f'PAGE NUMBER: {self.page_number}\n\n')


			for pos in new_table.word_lines:

				next_text = new_table.word_lines[pos]['text']

				print('-- NEXT LINE --')

				print('-TEXT-\n', next_text, '\n------')

				page_image = self.page_.to_image(resolution=72)#.save("train_page.png", format="PNG")

				page_image.draw_rects([new_table.word_lines[pos]['line_rect']], stroke=(255, 66, 144), fill=(255, 0, 46, 30))

				page_image.save("train_page.png", format="PNG")

				cat_list = ['Allocation', 'Holdings_Top', 'Holdings_Bot', 'Performance', 'FeesCosts', 'FundName', 'Managed_Funds', 'Buy_Sell',
				'Fee_Perform', 'Fee_Manage', 'NAV','ClassSize','FundSize','StrategySize','Fee_Ind', 'x_new_1', 'x_new_2', 'Trust_Valuations', 'x3', 'x4']
				#'Skip_To_Table'

				cat_list = sorted(cat_list)

				input_prompt = ''
				for idx, cat_ in enumerate(cat_list):
					input_prompt += f'- ({idx})-{cat_}\n'
					# Make dir if does not exist
					os.makedirs('data\\' + cat_, exist_ok=True)
					os.makedirs('data\\' + cat_ + '_table', exist_ok=True)

				#cropped_table.to_image(resolution=150).save("train_img.png", format="PNG")

				input_prompt = '(n)-Next Line, (t)-TableInput, (p)-NextTable, (|)-Next Fund\n' + input_prompt

				#img_1 = cv.imread("train_img.png")
				img_2 = cv.imread("train_page.png")

				#cv.imshow("img_1",img_1)
				cv.imshow("img_2",img_2)

				cv.waitKey(50)

				prompt_output = input(input_prompt)
				print(prompt_output)

				text_to_save = next_text
				addtional_dir_arg = ""


				cv.destroyAllWindows()

				if prompt_output == 'n':
					print('-- SKIPPING --')
					continue
				elif prompt_output == 't':
					print('-- TABLE --')
					text_to_save = new_table.text
					addtional_dir_arg = "_table"

					#img_1 = cv.imread("train_img.png")
					img_2 = cv.imread("train_page.png")

					#cv.imshow("img_1",img_1)
					cv.imshow("img_2",img_2)

					cv.waitKey(50)

					prompt_output = input(input_prompt)
					print(prompt_output)

					cv.destroyAllWindows()
					#break
				elif prompt_output == 'p':
					break
				elif prompt_output == '|':
					full_finish = 'page'
					print("\n\n ------ NEXT DOC ------ \n\n")
					return 'page'
				elif prompt_output == 'fund':
					print("\n\n\n\n\n ------------- FULL FINISH ------------- \n\n\n\n\n")
					full_finish = 'fund'
					return 'fund'

				print('-.-')



				prompt_outputs = prompt_output.split(",")

				for prompt_out in prompt_outputs:
					save_dir_prefix = 'data/' + cat_list[int(prompt_out)] + addtional_dir_arg

					lastnumber_ = 0
					try:
						while os.path.isfile(save_dir_prefix + "/" + str(lastnumber_) + "_" + prompt_out + ".txt"):
							lastnumber_ += 1
					except:
						print('--')

					print('SAVED')
					txt_save = open(save_dir_prefix + "/" + str(lastnumber_) + "_" + prompt_out + ".txt", 'w')
					txt_save.write(text_to_save)
					txt_save.close()
			# --

			self.tables.append(new_table)
			


		return True
	

	def add_table(self, bbox, page_crop):
		new_table = Table(page_crop, self.page_number, bbox)
		return new_table


class Table:

	def __init__(self, page_, page_number, bbox = []):
		"""
		Variables:
		"""

		self.page_number = page_number

		self.bbox = bbox

		self.size = 0

		self.page_ = page_

		self.word_lines = {}
		self.table_collections = []

		self.ext_data = {}

		self.text = ''

		return

	
	def extract_words(self):
		#if not page_:
		#	page_ = self.page_
		# Extract words
		page_ = self.page_


		self.text = page_.extract_text(x_tolerance=1, y_tolerance=1)
		if not self.text:
			self.text = ''


		words = page_.extract_words(x_tolerance=1, y_tolerance=1, keep_blank_chars=True)

		# Create lines from words based on vertical positioning [1px dif]
		for word_obj in words:
			bottom_pos = int(word_obj['bottom'])
			pos_range = [bottom_pos, bottom_pos - 1, bottom_pos + 1]
			
			current_word_line = None
			for pos in pos_range:
				if pos in self.word_lines:
					current_word_line = self.word_lines[pos]
					break
			if not current_word_line:
				self.word_lines[bottom_pos] = {
					'line_rect': {},
					'rects': [],
					'text': '',
					'search_found': None,
					'word_groups': [],
				}
				current_word_line = self.word_lines[bottom_pos]
			# --
			current_word_line['rects'].append(word_obj)
		# --
		word_line_rects = []
		for pos in self.word_lines:
			
			word_rects = self.word_lines[pos]['rects']
			word_rects = sorted(word_rects, key=lambda word: word["x0"], reverse=False)
			
			line_text = ''
			for word_rect in word_rects:
				line_text += word_rect['text'] + ' '
			
			self.word_lines[pos]['text'] = line_text
			self.word_lines[pos]['rects'] = word_rects
			
			# Rects stats
			for rect in word_rects:
				x0 = int(rect['x0'])
				x1 = int(rect['x1'])
				rect['x_mid'] = (x0 + x1) / 2
			
			
			#word_line = self.word_lines[pos]
			
			line_rect = {
				'x0': word_rects[0]['x0'],
				'x1': word_rects[-1]['x1'],

				'x_mid': (word_rects[0]['x0'] + word_rects[-1]['x1']) / 2,
				
				'width': word_rects[0]['x0'] - word_rects[-1]['x1'],
				'height': word_rects[0]['top'] - word_rects[-1]['bottom'],
				
				'top': word_rects[0]['top'],
				'bottom': word_rects[0]['bottom']
			}
			self.word_lines[pos]['line_rect'] = line_rect
			word_line_rects.append(line_rect)
		# --

		# Set line indecies
		for line_idx_name in self.word_lines:
			word_line = self.word_lines[line_idx_name]
			word_line['idx'] = line_idx_name
		# --


	def search_for_subtables(self, search_regexs):
		# Search for potential subtables with regex
		for pos in self.word_lines:
			word_line = self.word_lines[pos]
			found = False
			for search_regex in search_regexs:
				#found_idx = word_line['text'].lower().find(search_word)
				#if found_idx != -1:
				found_idx = re.search(search_regex['search'], word_line['text'].lower())#.find(search_word)
				if found_idx != None:
					word_line['search_found'] = search_regex['label']
					found = True
					break
			# --
			if not found:
				continue
			# --
			#print('\n -- FOUND -- \n')
		# --
		return


	def construct_subtables(self, line_leniency=2, min_lines=2):# TODO: Add args and have args for discard ect...


		line_indecies = list(self.word_lines.keys())
		line_indecies = sorted(line_indecies, reverse=False)

		table_line_rects = []
		self.table_collections = []

		already_in_table = {}
		
		for pos in self.word_lines:
			word_line = self.word_lines[pos]

			# If not found || already in a table
			if not word_line['search_found'] or pos in already_in_table:
				continue
			#print(f'\n - Constructing table for {word_line["search_found"]}')
			
			table_lines = []

			line_idx = line_indecies.index(pos)
			table_lines.append(self.word_lines[pos])
			#table_line_rects.append(self.word_lines[pos]['line_rect'])
			
			n = len(line_indecies) - 1
			count = 1
			last_idx = line_idx + 1
			last_line = self.word_lines[pos]
			extra_lines = 0
			last_line_failed = False
			last_line_failed_idx = 0
			while last_idx < n:
				count += 1
				line_pos = line_indecies[last_idx]
				next_line = self.word_lines[line_pos]
				
				# If last line inside next line
				if next_line['line_rect']['top'] < last_line['line_rect']['bottom']:
					#print(last_line['line_rect']['top'], next_line['line_rect']['bottom'])
					table_lines.append(next_line)
					#table_line_rects.append(next_line['line_rect'])
					
					last_line = next_line
					last_idx += 1
					
					continue
				# --
				
				line_text = next_line['text']
				
				patterns = []
				pattern = '[\d]+'
				
				found_re = re.search(pattern,line_text)
				if not found_re:
					extra_lines += 1
					last_line_failed = True
					last_line_failed_idx = max(1, len(table_lines) - 1)
					if extra_lines > line_leniency:
						break
				else:
					last_line_failed = False
				# --
				
				table_lines.append(next_line)
				#table_line_rects.append(next_line['line_rect'])
				
				last_line = next_line
				last_idx += 1
			# --
			
			# If failed cut back to prvious
			if last_line_failed:
				table_lines = table_lines[:last_line_failed_idx - 1]
			
			# If table lines does not reach the minimum
			if len(table_lines) < min_lines:
				#print(' FAILED - Not enough lines')
				continue

			table_rect = {
				'x0': table_lines[0]['line_rect']['x0'],
				'x1': table_lines[-1]['line_rect']['x1'],

				'x_mid': (table_lines[0]['line_rect']['x0'] + table_lines[-1]['line_rect']['x1']) / 2,
				
				'width': table_lines[0]['line_rect']['x0'] - table_lines[-1]['line_rect']['x1'],
				'height': table_lines[0]['line_rect']['top'] - table_lines[-1]['line_rect']['bottom'],
				
				'top': table_lines[0]['line_rect']['top'],
				'bottom': table_lines[0]['line_rect']['bottom']
			}
			
			table_collection_obj = {
				'table_lines': table_lines,
				'table_columns': [],
				'table_rect': table_rect,
			}

			self.table_collections.append(table_collection_obj)#table_lines

			# Do not make tables for tables that have already been added to tables
			for table_line in table_lines:
				already_in_table[table_line['idx']] = True
			
			
			
			for x in table_lines:
				table_line_rects.append(x['line_rect'])
			# --
			
			# --
		# --
		return


	def format_subtables(self):
		for table_collection in self.table_collections:
			#print('\n - New Table/collection - \n')

			"""
			-- Create and seperate word group columns --
			"""

			table_line_groups = []
			for table_line in table_collection['table_lines']:
				rects = table_line['rects']

				rects_txt = [x['text'] for x in rects]
				rect_sides_left = [x['x0'] for x in rects]
				rect_sides_right = [x['x1'] for x in rects]
				rect_lengths = [x['x1'] - x['x0'] for x in rects]

				rect_dists = []
				before_rect = rects[0]
				for idx in range(1, len(rects)):
					cur_rect = rects[idx]
					cur_rect['dist'] = math.inf

					distance = abs(cur_rect['x0'] - before_rect['x1'])
					before_rect['dist'] = distance

					rect_dists.append(distance)
					before_rect = cur_rect

				#print(rect_dists)

				if len(rect_dists) == 0:
					rect_dists = [0]

				average_dist = sum(rect_dists) / max(1,len(rect_dists))
				dist_modes = sci_stats.mode(rect_dists)
				dist_mode = list(dist_modes)[0]
				mode_threshold = int(math.ceil(dist_mode) * 1.25)
				#print(f'Mode thresh: {mode_threshold} - Avg dist: {average_dist}')

				word_groups = []#rect_groups
				cur_group = []
				cur_text = ''
				for idx in range(len(rects)):
					cur_rect = rects[idx]
					#print(f"- {cur_rect['text']} - {cur_rect['dist']} ")
					half_avg = False
					small_value = False

					if 'dist' in cur_rect:
						half_avg = cur_rect['dist'] < (average_dist / 2) + min(2, mode_threshold)
						small_value = cur_rect['dist'] < min(6, mode_threshold)
						#half_avg = cur_rect['dist'] < (average_dist / 2) + min(3, mode_threshold)
						half_avg = cur_rect['dist'] < average_dist + min(3, mode_threshold)
						small_value = cur_rect['dist'] < min(6, mode_threshold)
					if half_avg and small_value:
						cur_text += cur_rect['text'] + ' '
						cur_group.append(cur_rect)
					else:
						#if len(cur_group) == 0:
						#    continue
						cur_text += cur_rect['text'] + ' '
						cur_group.append(cur_rect)

						group_rect = {
							'x0': cur_group[0]['x0'],
							'x1': cur_group[-1]['x1'],
							
							'width': cur_group[0]['x0'] - cur_group[-1]['x1'],
							'height': cur_group[0]['top'] - cur_group[-1]['bottom'],

							'x_mid': (cur_group[0]['x0'] + cur_group[-1]['x1']) / 2,
							
							'top': cur_group[0]['top'],
							'bottom': cur_group[0]['bottom']
						}

						group_obj = {
							'rects': cur_group,
							'text': cur_text,
							'group_rect': group_rect,
							'range_idx': None,
						}
						word_groups.append(group_obj)
						cur_group = []
						cur_text = ''
				# --


				table_line['word_groups'] = word_groups
				table_line_groups.append(word_groups)

				

				#print('\n')
				#[print(x['text']) for x in word_groups]
				#im.draw_rects([x['group_rect'] for x in word_groups], stroke=(255, 66, 144), fill=(255, 0, 46, 30))
			# --


			"""
			-- Create and seperate word group columns --
			"""

			x_range_list_prior = []
			# Each lines groups
			#for word_groups in table_line_groups:
			for table_line in table_collection['table_lines']:
				word_groups = table_line['word_groups']
				# Groups on line
				for word_group in word_groups:
					group_rect = word_group['group_rect']
					#new_x_range = (group_rect['x0'] - 1, group_rect['x1'] + 1, group_rect['top'], group_rect['bottom'])
					new_x_range = (group_rect['x0'], group_rect['x1'], group_rect['top'], group_rect['bottom'])
					exists = False
					#exists = True

					#'''
					for idx, x_range_bit in enumerate(x_range_list_prior):
						x_range = x_range_bit[0]
						x_range_mid = (x_range[0] + x_range[1]) / 2
						# If mid of the group_rect being considered on this line is within the range of the any of the current ranges, or the other way round, take the max
						if new_x_range[0] == x_range[0] and new_x_range[1] == x_range[1]:
							new_x_range = (min(new_x_range[0], x_range[0]), max(new_x_range[1], x_range[1]), min(new_x_range[2], x_range[2]), max(new_x_range[3], x_range[3]))
							x_range_list_prior[idx] = (new_x_range, x_range_bit[1] + 1)
							#word_group['range_idx'] = idx
							exists = True
							break
					#'''
					
					if not exists:
						current_len = len(x_range_list_prior)
						#word_group['range_idx'] = current_len
						x_range_list_prior.append((new_x_range,1))
					# --
			# --


			x_range_list = []
			for table_line in table_collection['table_lines']:
				word_groups = table_line['word_groups']
				# Groups on line
				for word_group in word_groups:
					group_rect = word_group['group_rect']
					#new_x_range = (group_rect['x0'] - 1, group_rect['x1'] + 1, group_rect['top'], group_rect['bottom'])
					new_x_range = (group_rect['x0'], group_rect['x1'], group_rect['top'], group_rect['bottom'])
					#exists = False
					total_cover = 0
					for idx, x_range_bit in enumerate(x_range_list_prior):
						x_range = x_range_bit[0]
						# If you cover them
						if x_range[0] - 2 > new_x_range[0] and x_range[1] + 2 < new_x_range[1] and x_range_bit[1] >= 2:
							total_cover += 1
					# --
					if total_cover < 2:
						exists = False
						for idx, x_range in enumerate(x_range_list):
							x_range_mid = (x_range[0] + x_range[1]) / 2
							# If mid of the group_rect being considered on this line is within the range of the any of the current ranges, or the other way round, take the max
							if (group_rect['x_mid'] >= x_range[0] and group_rect['x_mid'] <= x_range[1]) or (x_range_mid >= new_x_range[0] and x_range_mid <= new_x_range[1]):
								new_x_range = (min(new_x_range[0], x_range[0]), max(new_x_range[1], x_range[1]), min(new_x_range[2], x_range[2]), max(new_x_range[3], x_range[3]))
								x_range_list[idx] = new_x_range
								word_group['range_idx'] = idx
								exists = True
								break
						
						if not exists:
							word_group['range_idx'] = len(x_range_list)
							x_range_list.append(new_x_range)
			# --
			table_collection['column_ranges'] = x_range_list

			table_columns_rects = []
			for x_range in x_range_list:
				rect_ = {'x0': x_range[0], 'x1': x_range[1], 'top': x_range[2], 'bottom': x_range[3]}
				table_columns_rects.append(rect_)
			#im.draw_rects(table_columns_rects, stroke=(255, 66, 144), fill=(255, 0, 46, 30))
			# --
		return

	def create_subtable_dataframes(self):
		df_list = []
		for table_collection in self.table_collections:#columns
			try:
				column_ranges = table_collection['column_ranges']
				df_rows = [[None] * len(column_ranges) for x in table_collection['table_lines']]
				df_rows = np.array(df_rows)
				for line_idx, table_line in enumerate(table_collection['table_lines']):
					word_groups = table_line['word_groups']
					# Groups on line
					for word_group in word_groups:
						range_idx = word_group['range_idx']
						df_rows[line_idx, range_idx] = word_group['text']
				collection_df = pd.DataFrame(df_rows)
				#print(collection_df)
				table_collection["df"] = collection_df
				df_list.append(collection_df)
			except:
				print('ERROR with dfs -- Search code 2336')
		return df_list



# ----------------------------------------------------------------------- #

















# --
