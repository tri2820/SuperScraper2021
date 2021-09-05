
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



import pdfplumber


import io

import requests



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
		"cat": "",
		"match": "",
		"ratio": 0,
	}
	similarity_list = []
	for cat_name in compare_values_:#compare_string_list_
		catagory = compare_values_[cat_name]
		for compare_name in catagory:
			item = catagory[compare_name]

			ratio_sequence = SequenceMatcher(None,compare_name.lower(),string_.lower()).ratio()
			ratio_cosine = cosine_similarity(compare_name.lower(), string_.lower())

			ratio_ = ratio_sequence
			if use_cosine:
				ratio_ = (ratio_sequence * 0.6) + ratio_cosine
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



class DocumentExtraction:
	url_string = ''
	"""
	table_areas: {'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])], 'conf': conf, 'class': names[c]}
	"""
	#detected_tables = []
	#pages_data = []

	def __init__(self, url_string_, save_iamges=False):
		self.url_string = url_string_
		self.save_iamges = save_iamges

		# Instance variables
		self.detected_tables = []
		self.pages_data = []

	def detect_tables(self):
		page_table_detections = run_pdf_table_detection(self.url_string, self.save_iamges)
		print(len(page_table_detections))
		self.detected_tables = page_table_detections

	def extract_tables(self):
		# Use nueral network to detect tables
		self.detect_tables()
		# Make sure to reset data to avoid repeats
		self.pages_data = []
		self.setup_pages()

		r = requests.get(self.url_string)
		f = io.BytesIO(r.content)

		# This is the pixel resolution, pdfplumber uses 72
		local_dpi = 72
		# If you change this, go look at the nn_extraction and change the dpi there as well
		global_dpi = 200

		with pdfplumber.open(f) as pdf:
			# Get pdf initial page size
			first_page = pdf.pages[0]
			print('PDF Size: ', (first_page.width,first_page.height))

			# Iterate over the pages detected
			for page_data in self.pages_data:
				#print('No. Pages: ',len(pdf.pages), '- Page Number: ', page_data['page_number'])
				if len(pdf.pages) - 1 < page_data['page_number']:
					print('\n\n\n --- PAGE NUMBER NOT RETRIVED! --- \n\n\n')
					continue

				# Get the pdf page
				pdf_page = pdf.pages[page_data['page_number']]

				page_data['all_text'] = pdf_page.extract_text(x_tolerance=1, y_tolerance=1)

				tables = page_data['tables']
				for table in tables:
					table['page_number'] = page_data['page_number']
					bbox = table['bbox']

					padding_table = 0
					xy1 = (int(bbox[0] - padding_table),int(bbox[1]) - padding_table)
					xy2 = (int(bbox[2] + padding_table),int(bbox[3]) + padding_table)

					dpi_ratio = local_dpi / global_dpi

					xy1 = (int(xy1[0] * dpi_ratio),int(xy1[1] * dpi_ratio))
					xy2 = (int(xy2[0] * dpi_ratio),int(xy2[1] * dpi_ratio))

					xy1 = (min(max(int(xy1[0]),0),int(first_page.width)),min(max(int(xy1[1]),0),int(first_page.height)))
					xy2 = (min(max(int(xy2[0]),0),int(first_page.width)),min(max(int(xy2[1]),0),int(first_page.height)))

					# Get page table crop
					cropped_table = pdf_page.crop((xy1[0],xy1[1],xy2[0],xy2[1]), relative=False)
					# Extract the text as lists of lists
					table['text'] = cropped_table.extract_text(x_tolerance=1, y_tolerance=1)
					if not table['text']:
						table['text'] = ''

					# Get text around the table
					#padding_horizontal = 4
					#padding_vertical = 20

					table_size = (xy2[0] - xy1[0], xy2[1] - xy1[1])
					table['size'] = table_size

					padding_horizontal = int(table_size[0] * 0.25)
					padding_vertical = int(table_size[1] * 0.75)

					around_top = (xy1[0] - padding_horizontal, xy1[1] - padding_vertical, xy2[0] + padding_horizontal, xy1[1])
					around_bottom = (xy1[0] - padding_horizontal, xy2[1], xy2[0] + padding_horizontal, xy2[1] + padding_vertical)

					around_top = (min(max(around_top[0],0),first_page.width), min(max(around_top[1],0),first_page.height), min(max(around_top[2],0),first_page.width), min(max(around_top[3],0),first_page.height))
					around_bottom = (min(max(around_bottom[0],0),first_page.width), min(max(around_bottom[1],0),first_page.height), min(max(around_bottom[2],0),first_page.width), min(max(around_bottom[3],0),first_page.height))

					table['text_top'] = ''
					table['text_bottom'] = ''

					if around_top[0] - around_top[2] > 1 and around_top[1] - around_top[3] > 1:
						table_top = pdf_page.crop((around_top[0],around_top[1],around_top[2],around_top[3]), relative=False)
						table['text_top'] = table_top.extract_text(x_tolerance=1, y_tolerance=1)
					if around_bottom[0] - around_bottom[2] > 1 and around_bottom[1] - around_bottom[3] > 1:
						table_bottom = pdf_page.crop((around_bottom[0],around_bottom[1],around_bottom[2],around_bottom[3]), relative=False)
						table['text_bottom'] = table_bottom.extract_text(x_tolerance=1, y_tolerance=1)

					#table_top.to_image(resolution=200).save("table_top.png", format="PNG")
					#table_bottom.to_image(resolution=200).save("table_bottom.png", format="PNG")


	def setup_pages(self):

		# Use detected tables to get an idea of infomation that might be present in pages
		for page_tables in self.detected_tables:
			page_data = {
				'page_number': page_tables['page_number'],#-0
				'tables': page_tables['table_areas'],
				# Note 'page_contexts' does nothing it is here for potential idea stuff
				'page_contexts': {
					'titles': None,
					'entitiy_relationships': None
				}
			}
			self.pages_data.append(page_data)
		# --
		return
# --



# TODO: add datatype biasing to 'compare_catargories' eg: prefers % preferes + - / ()

class DocumentDataExtractor:
	documents = []

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

	discard_indicators = ['example']

	similarity_data = {}

	def __init__(self):

		for cat_name in self.compare_values:
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
		for cat_name in self.compare_values:
			if not cat_name in document_data['sim_data']:
				document_data['sim_data'][cat_name] = []

		# Extract infomation from tables
		document = document_data['doc']
		for page_idx, page in enumerate(document.pages_data):
			for table_idx, table in enumerate(page['tables']):
				#table['bbox']
				text = table['text']

				
				texts = re.split("\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n|\\n\\n",text)#"\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n|\\n\\n"#\.\\n|\. [A-Z0-9] #\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n #'\u00b2'
				texts = [re.sub("\\n[\w\d]\\n|\\n",' ',x) for x in texts]#'\\n[\w\d]\\n|\\n

				

				# Look for discard indicaters
				discard_table = False
				for indicator in self.discard_indicators:
					if table['text'].lower().find(indicator) != -1 or table['text_top'].lower().find(indicator) != -1 or table['text_bottom'].lower().find(indicator) != -1:
						discard_table = True
						break
				
				if discard_table:
					continue

				#[print(repr(x)) for x in texts]

				for text_part in texts:
					item = find_most_similar(text_part, self.compare_values, True, True)# self.compare_string_list # , regex_list = [['[+\\$\-\%]',0.75],['\d',0.9]]
					# Add document->page->tables index to item
					#item.append([0, page_idx, table_idx])
					
					sim_val = item["ratio"]
					if sim_val > init_threshold:
						document_data['sim_data'][item["cat"]].append(item)
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





# ----------------------------------------------------------------------- #
