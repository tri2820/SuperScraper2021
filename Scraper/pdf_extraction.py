
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
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ---

import PyPDF2

import pandas as pd

#import matplotlib.pyplot as plt

from operator import itemgetter

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






from Scraper.nn_extraction import run_pdf_table_detection, pdf_to_images

#from nn_extraction import run_pdf_table_detection



import pdfplumber


import io

import requests


#tables = camelot.read_pdf("https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf",pages = 'all', flavor = 'stream',flag_size=True)


class StringTest:

	url_string = ""
	text = ""

	def __init__(self, url_string_):
		self.url_string = url_string_


	def extract_text(self):
		r = requests.get(self.url_string)
		f = io.BytesIO(r.content)

		pdfReader = None
		try:
			pdfReader = PyPDF2.PdfFileReader(f)
		except:
			print('Failed String Test')
			return
		#print(pdfReader.numPages)
		self.text = ""

		for page in pdfReader.pages:
			self.text += page.extractText()
		# --
		text_file = open("pdf_texts.txt", "w")
		text_file.write(self.url_string)
		text_file.close()


	def test_for_string(self, test_string, regex_ = False, amount = None):
		found = False
		text = self.text
		if not amount:
			text = self.text
		else:
			text = self.text[:amount]
		if regex_:
			found = re.search(test_string, text)
		else:
			found = text.find(test_string) != -1
		return found

# --


# NOTE: This numerics/symbols regex weight function will allow stuff like 23, %, /, ^3, @#421-3, +, - to be given increased or decrease wieghts

def pattern_weights(in_string, regex_list):
	weight = 0
	for pattern in regex_list:
		if re.search(pattern[0], in_string) != None:
			weight += pattern[1]
	# --
	return weight




def find_most_similar(string_, compare_string_list_, use_cosine=True, use_weights=True):
	"""
	returns: ('string that was being tested', 'catagory string that matched highest', ratio of similarity)
	"""
	highest_match = ["","",0]
	similarity_list = []
	for item in compare_string_list_:

		ratio_sequence = SequenceMatcher(None,item.lower(),string_.lower()).ratio()
		ratio_cosine = cosine_similarity(item.lower(), string_.lower())

		ratio_ = ratio_sequence
		if use_cosine:
			ratio_ = (ratio_sequence * 0.6) + ratio_cosine
		# --

		if use_weights:
			regex_list = [['[+\\$\-\%]',0.75],['\d',0.9]]
			symbols_weight = pattern_weights(string_.lower(), regex_list)
			ratio_ += ratio_ * symbols_weight
		# --


		match_info = [string_, item, ratio_]
		similarity_list.append(match_info)

	for match_info in similarity_list:
		if match_info[2] > highest_match[2]:
			highest_match = match_info
	return highest_match



class DocumentExtraction:
	url_string = ''
	"""
	table_areas: {'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])], 'conf': conf, 'class': names[c]}
	"""
	detected_tables = []
	pages_data = []

	def __init__(self, url_string_):
		self.url_string = url_string_

	def detect_tables(self):
		page_table_detections = run_pdf_table_detection(self.url_string,False)
		self.detected_tables = page_table_detections

	def extract_tables(self):
		self.detect_tables()
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

				if len(pdf.pages) - 1 < page_data['page_number']:
					print('\n\n\n --- PAGE NUMBER NOT RETRIVED! --- \n\n\n')
					continue

				# Get the pdf page
				pdf_page = pdf.pages[page_data['page_number']]

				page_data['all_text'] = pdf_page.extract_text(x_tolerance=1, y_tolerance=1)
				#print('\nNumber: ', page_data['page_number'])
				#print('\nAll text: ', page_data['all_text'])

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


					#ex_words = cropped_table.extract_words(x_tolerance=1, y_tolerance=1, use_text_flow=True, keep_blank_chars=True)
					#print(ex_words)
					#ex_words_ = [x['text'] for x in ex_words]

					#print(ex_words_)
					#text_list = []
					'''
					for text_section in ex_words_:
						#print('\n text section {} \n'.format(text_section))
						text_string = ''
						for x_txt in text_section:
							text_string += x_txt
						print('\n-Text section: {} \n--\n'.format(text_string))
						text_list.append(text_string)
					'''
					# --
					#print('\n\n-- Text List --\n\n',text_list,'\n\n')
					#table['text'] = text_list


					#text_string = ''
					#for x_txt in ex_words_:
					#	text_string += ' ' + x_txt
					# --

					'''
					print("\n-- NORMAL TEST --")
					print(table['text'])

					print("\n-- ex_words_ TEST --")
					print(ex_words_)

					print("\n-- text_string TEST --")
					print(text_string)
					'''


					
					
					

					#print(0/2)


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

	compare_string_list = [
		#'management fee',
		#'estimated total management costs',
		#'buy/sell spread',
		#'buy-sell spread',
		'fees expenses cost',
		'buy sell',
		'transaction costs allowance',
		'asset allocation',
	]

	compare_catargories = {
		#'management fee': 'Management Fee',
		#'fees and expenses': 'Management Fee',
		#'estimated total management costs': 'Management Fee',
		#'buy/sell spread': 'Buy/Sell spread',
		#'buy-sell spread': 'Buy/Sell spread',
		#'fee cost': 'Management Fee',
		'fees expenses cost': 'Management Fee',
		'buy sell': 'Buy/Sell spread',
		'transaction costs allowance': 'Buy/Sell spread',
		'asset allocation': 'Asset Allocation',
	}

	discard_indicators = ['example']

	similarity_data = {}

	def __init__(self):
		pass

	def process_document_data(self):
		pass

	def add_document(self, document):
		#document.url_string
		#document.pages_data
		document_obj = {
			'url': document.url_string,
			'pages_data': document.pages_data,
		}
		self.documents.append(document_obj)
		return len(self.documents) - 1
	
	def extract_similar_rows(self, init_threshold, doc_idx=0):

		for compare_value in self.compare_string_list:
			self.similarity_data[compare_value] = []

		document = self.documents[doc_idx]
		for page_idx, page in enumerate(document['pages_data']):
			for table_idx, table in enumerate(page['tables']):
				#table['bbox']
				text = table['text']

				#\.\\n|\. [A-Z0-9] #\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n #'\u00b2'
				#print('Text type: ', type(text))
				texts = re.split("\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n|\\n\\n",text)#"\.\\n|\. [A-Z0-9]|\\n[\w\d]\\n|\\n\\n"
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
					item = find_most_similar(text_part, self.compare_string_list, True, True)
					# Add document->page->tables index to item
					item.append([0, page_idx, table_idx])
					sim_val = item[2]
					if sim_val > init_threshold:
						self.similarity_data[item[1]].append(item)
		return
	
	def sort_as_most_similar(self):

		for sim_type in self.similarity_data:
			sim_values = self.similarity_data[sim_type]
			self.similarity_data[sim_type] = sorted(sim_values, key=lambda tup: tup[2], reverse=True)
		
		shrinked_catagories = {}

		for map_value in self.compare_catargories:
			cat_value = self.compare_catargories[map_value]
			shrinked_catagories[cat_value] = []

		for sim_cat in self.similarity_data:
			sim_data = self.similarity_data[sim_cat]
			shrinked_catagories[self.compare_catargories[sim_cat]].extend(sim_data)

		# Sort values by similarity threshold
		for cat_name in shrinked_catagories:
			sim_values = shrinked_catagories[cat_name]
			sim_values = sorted(sim_values, key=lambda tup: tup[2], reverse=True)
			#if shrink != None:
			#    if shrink > 0:
			shrinked_catagories[cat_name] = sim_values

		for cat_name in shrinked_catagories:
		    sim_values = shrinked_catagories[cat_name][:10]
		    #for value in sim_values:
		    #    print(value)

		#print(self.similarity_data)
		#print(shrinked_catagories)

		self.similarity_data = shrinked_catagories

		return self.similarity_data

# --





# ----------------------------------------------------------------------- #

'''

class TableDataExtractor:

	tables = []
	tables_dfs = []
	similarity_data = {}
	similarity_df_list = {}

	compare_string_list = ['management fee','fees and expenses','estimated total management costs','buy/sell spread']

	compare_catargories = {
		'management fee': 'Management Fee',
		'fees and expenses': 'Management Fee',
		'estimated total management costs': 'Management Fee',
		'buy/sell spread': 'Buy/Sell spread',
	}

	def __init__(self):
		self.tables = []
		self.tables_dfs = []
		self.similarity_data = {}
		self.similarity_df_list = {}

	def store_extracted_tables(self, extracted_tables_):

		tables = []
		tables_dfs = []

		for table_type in extracted_tables_:
			tables_ = extracted_tables_[table_type]
			for table_data in tables_:
				table_ = table_data['table']
				self.tables.append(table_data)
				self.tables_dfs.append(table_.df)

	def extract_similar_rows(self, init_threshold):
		# Returns string_, compared_string, ratio
		#find_most_similar(value, compare_string_list)

		for compare_value in self.compare_string_list:
			self.similarity_data[compare_value] = []

		for i in range(len(self.tables_dfs)):
			table_df = self.tables_dfs[i]
			for column_name in table_df.columns:
				similarities_list = [(idx,i,find_most_similar(value, self.compare_string_list)) for (idx, value) in zip(table_df.index, table_df[column_name])]
				for similarity_object in similarities_list:
					sim_val = similarity_object[2][2]
					# A more agressive threshold can be applied in data filter functions
					if sim_val > init_threshold:
						self.similarity_data[similarity_object[2][1]].append(similarity_object)
		# --

	def compile_similarity_data(self):

		self.similarity_df_list = {}

		for similarity_type in self.similarity_data:
			sim_list = self.similarity_data[similarity_type]
			sim_df_list = []
			#count = 0
			for sim_val in sim_list:
				row = self.tables_dfs[sim_val[1]].iloc[[sim_val[0]]]
				#row.index = count
				sim_df_list.append(row)
				#count += 1
			sim_df = pd.concat(sim_df_list)
			sim_df.set_index(pd.Index(range(len(sim_df))), inplace = True)
			self.similarity_df_list[similarity_type] = sim_df

	def sort_as_most_similar(self, set_main_data=False, shrink=None):

		shrinked_catagories = {}

		for map_value in self.compare_catargories:
			cat_value = self.compare_catargories[map_value]
			shrinked_catagories[cat_value] = []

		for sim_cat in self.similarity_data:
			sim_data = self.similarity_data[sim_cat]
			shrinked_catagories[self.compare_catargories[sim_cat]].extend(sim_data)

		# Sort values by similarity threshold
		for cat_name in shrinked_catagories:
			sim_values = shrinked_catagories[cat_name]
			sim_values = sorted(sim_values, key=lambda tup: tup[2][2], reverse=True)
			#if shrink != None:
			#    if shrink > 0:
			shrinked_catagories[cat_name] = sim_values

		#for cat_name in shrinked_catagories:
		#    sim_values = shrinked_catagories[cat_name][:10]
		#    for value in sim_values:
		#        print(value)

		if set_main_data:
			self.similarity_data = shrinked_catagories

		return shrinked_catagories[cat_name]


	def print_similarity_df(self):

		for similarity_type in self.similarity_df_list:
			print(f' ----- {similarity_type} ----- '.format())
			sim_df = self.similarity_df_list[similarity_type]
			print(sim_df)
# --




class TableExtraction:

	url_string = ''
	extracted_tables = {
		'stream': [],
		'lattice_b_t': [],
		'lattice_b_f': [],
	}

	filtered_tables = {
		'stream': [],
		'lattice_b_t': [],
		'lattice_b_f': [],
	}

	def __init__(self, url_string_):
		self.url_string = url_string_

	def extract_tables(self):
		self.extracted_tables['stream'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=False)
		self.extracted_tables['lattice_b_t'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'lattice',flag_size=False, process_background = True)
		self.extracted_tables['lattice_b_f'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'lattice',flag_size=False, process_background = False)#pdfplumber
		#page_detections = run_pdf_table_detection(self.url_string)
		#self.extracted_tables = page_detections
		
	def filter_tables(self):
		for table_type in self.extracted_tables:
			tables_ = self.extracted_tables[table_type]
			for table_ in tables_:
				table_df = table_.df
				drop_table = False
				# If only one column or one row - drop
				if table_.shape[0] <= 1 or table_.shape[1] <= 1:
					drop_table = True

				if not drop_table:
					table_object = self.generate_table_stats(table_)
					self.filtered_tables[table_type].append(table_object)
		# --

	def generate_table_stats(self, table_):

		# Table bbox
		cols_ = [item for t in table_.cols for item in t]
		rows_ = [item for t in table_.rows for item in t]

		table_bbox = ((min(cols_),max(rows_)), (max(cols_), min(rows_)))
		table_bbox_string = str(min(cols_)) + ',' + str(max(rows_)) + ',' + str(max(cols_)) + ',' + str(min(rows_))

		# Table midpoint
		x_mid = (min(cols_)+max(cols_))/2
		y_mid = (min(rows_)+max(rows_))/2

		table_midpoint = (x_mid, y_mid)

		# Table area
		table_area = (max(cols_) - min(cols_)) * (max(rows_) - min(rows_))

		table_object = {
			'table': table_,
			'bbox': table_bbox,
			'bbox_string': table_bbox_string,
			'midpoint': table_midpoint,
			'area': table_area
		}

		return table_object
# --






class ExtractTableHandler:
	# -Remmbe self.url_string
	url_string = "https://www.vanguard.com.au/adviser/products/documents/8189/AU"
	compare_string_list = ['management fee','fees and expenses','estimated total management costs']

	tables = []

	# The function that runs upon creation
	def __init__(self, url_string_, compare_string_list_ = ['management fee','fees and expenses','estimated total management costs']):
		# Set the input url given on class creation ie: ExtractTable("https://www.vanguard.com.au/adviser/products/documents/8189/AU")
		self.url_string = url_string_
		self.compare_string_list = compare_string_list_

	def get_tables(self):
		self.tables = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=True)

	def find_most_similar(self, string_, compare_string_list_):
		highest_match = ("","",0)
		similarity_list = []
		for item in compare_string_list_:
			ratio_ = SequenceMatcher(None,item,string_).ratio()
			match_info = (string_, item, ratio_)
			similarity_list.append(match_info)

		for match_info in similarity_list:
			if match_info[2] > highest_match[2]:
				highest_match = match_info
		return highest_match

	def extract_match_tables(self):
		df_list = []
		matched_dfs = pd.DataFrame()
		for table in self.tables:
			table_df = table.df
			table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
			# Convert to list and extract lists that are similar
			# TODO: Do this using a dataframe at some point (not priority)
			values_list = table_df.values.tolist()
			#print(table_df, values_list)
			for i in range(len(values_list)):
				for j in values_list[i]:
					# TODO: We should unhard code stuff like this
					x = SequenceMatcher(None,'type of fee or costs',j).ratio()
					if x > 0.6:
						df_list.append(table_df)
						print(table_df)
						#matched_dfs = pd.concat(df_list)
		if len(df_list) > 0:
			matched_dfs = pd.concat(df_list)
		return matched_dfs


	def get_similar_row(self, matched_dfs):
		df_list = matched_dfs.values.tolist()
		#print(df_list)
		found = []
		highest = 0
		for i in range(len(df_list)):
			for j in df_list[i]:
				similarity_info = self.find_most_similar(str(j).lower(),self.compare_string_list)#j.lower()
				similarity_value = similarity_info[2]
				if similarity_value > highest:
					highest = similarity_value
					found = df_list[i]
		return found

	def extract_table(self):
		matched_dfs = self.extract_match_tables()
		found = self.get_similar_row(matched_dfs)

		# TODO: Mabye move these cleaning operations to a different class or functions,
		# reason being because this data cleaning operation is specifically for fund managers (not prio)
		# NOTE: Look into regex
		fee_value = ""
		for i in found:
			x = i.find("0.")
			if x != -1:
				fee_value = i[x:(x+10)]

		management_fee_list = []
		management_fee_list.append(fee_value)
		return management_fee_list

# --
'''

'''
class TableDataExtractor:

	tables = []
	tables_dfs = []
	similarity_data = {}
	similarity_df_list = {}

	compare_string_list = ['management fee','fees and expenses','estimated total management costs','buy/sell spread']

	compare_catargories = {
		'management fee': 'Management Fee',
		'fees and expenses': 'Management Fee',
		'estimated total management costs': 'Management Fee',
		'buy/sell spread': 'Buy/Sell spread',
	}

	def __init__(self):
		self.tables = []
		self.tables_dfs = []
		self.similarity_data = {}
		self.similarity_df_list = {}

	def store_extracted_tables(self, extracted_tables_):

		tables = []
		tables_dfs = []

		for table_type in extracted_tables_:
			tables_ = extracted_tables_[table_type]
			for table_data in tables_:
				table_ = table_data['table']
				self.tables.append(table_data)
				self.tables_dfs.append(table_.df)

	def extract_similar_rows(self, init_threshold):
		# Returns string_, compared_string, ratio
		#find_most_similar(value, compare_string_list)

		for compare_value in self.compare_string_list:
			self.similarity_data[compare_value] = []

		for i in range(len(self.tables_dfs)):
			table_df = self.tables_dfs[i]
			for column_name in table_df.columns:
				similarities_list = [(idx,i,find_most_similar(value, self.compare_string_list)) for (idx, value) in zip(table_df.index, table_df[column_name])]
				for similarity_object in similarities_list:
					sim_val = similarity_object[2][2]
					# A more agressive threshold can be applied in data filter functions
					if sim_val > init_threshold:
						self.similarity_data[similarity_object[2][1]].append(similarity_object)
		# --

	def compile_similarity_data(self):

		self.similarity_df_list = {}

		for similarity_type in self.similarity_data:
			sim_list = self.similarity_data[similarity_type]
			sim_df_list = []
			#count = 0
			for sim_val in sim_list:
				row = self.tables_dfs[sim_val[1]].iloc[[sim_val[0]]]
				#row.index = count
				sim_df_list.append(row)
				#count += 1
			sim_df = pd.concat(sim_df_list)
			sim_df.set_index(pd.Index(range(len(sim_df))), inplace = True)
			self.similarity_df_list[similarity_type] = sim_df

	def sort_as_most_similar(self, set_main_data=False, shrink=None):

		shrinked_catagories = {}

		for map_value in self.compare_catargories:
			cat_value = self.compare_catargories[map_value]
			shrinked_catagories[cat_value] = []

		for sim_cat in self.similarity_data:
			sim_data = self.similarity_data[sim_cat]
			shrinked_catagories[self.compare_catargories[sim_cat]].extend(sim_data)

		# Sort values by similarity threshold
		for cat_name in shrinked_catagories:
			sim_values = shrinked_catagories[cat_name]
			sim_values = sorted(sim_values, key=lambda tup: tup[2][2], reverse=True)
			#if shrink != None:
			#    if shrink > 0:
			shrinked_catagories[cat_name] = sim_values

		#for cat_name in shrinked_catagories:
		#    sim_values = shrinked_catagories[cat_name][:10]
		#    for value in sim_values:
		#        print(value)

		if set_main_data:
			self.similarity_data = shrinked_catagories

		return shrinked_catagories[cat_name]


	def print_similarity_df(self):

		for similarity_type in self.similarity_df_list:
			print(f' ----- {similarity_type} ----- '.format())
			sim_df = self.similarity_df_list[similarity_type]
			print(sim_df)
'''

'''
extraction = TableExtraction('https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund_PDS.pdf')
extraction.extract_tables()
extraction.filter_tables()

extract_data = TableDataExtractor()
extract_data.store_extracted_tables(extraction.filtered_tables)
extract_data.extract_similar_rows(0.2)
extract_data.sort_as_most_similar(True)
extract_data.compile_similarity_data()
extract_data.print_similarity_df()
'''


#getting the dataframe
'''
table_handler = ExtractTableHandler("https://www.vanguard.com.au/adviser/products/documents/8189/AU")
table_handler.get_tables()
management_fee_list = table_handler.extract_table()


data = {'Management fee': management_fee_list,'Intial Investment':[None],'Additional Investment':[None], 'Withdraw':[None],'Transfer':[None]}
df = pd.DataFrame(data)

print(df)
'''

# 'https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund_PDS.pdf'
# 'https://www.pendalgroup.com/wp-content/uploads/docs/factsheets/PDS/Pendal%20Focus%20Australian%20Share%20Fund%20-%20PDS.pdf?v=2021-05-141620965181'

'''

url_string = 'https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund_PDS.pdf'

#url_string = 'https://www.pendalgroup.com/wp-content/uploads/docs/factsheets/PDS/Pendal%20Focus%20Australian%20Share%20Fund%20-%20PDS.pdf?v=2021-05-141620965181'

tables_list = []

# '1,2,3,4,5,6,7,8,9,10,11,12,13'

plt.rcParams["figure.figsize"] = (8,8)

tables_streams = camelot.read_pdf(url_string, pages = 'all', flavor = 'stream', flag_size = True)
tables_lattice_true = camelot.read_pdf(url_string, pages = 'all', flavor = 'lattice', process_background = True)
tables_lattice_false = camelot.read_pdf(url_string, pages = 'all', flavor = 'lattice', process_background = False)#, flag_size = True

#if tables.n > 0:
tables_list.append((tables_streams,tables_lattice_true,tables_lattice_false))
# --

if len(tables_list) > 0:
	for tables_a in tables_list:
		tables_streams_ = tables_a[0]
		tables_lattice_true_ = tables_a[1]
		tables_lattice_false_ = tables_a[2]
		lentgth = max([len(tables_streams_),len(tables_lattice_true_),len(tables_lattice_false_)])
		for i in range(lentgth):
			if i < len(tables_streams_):
				x = tables_[i]
				#camelot.plot(x, kind='text').show()
				#camelot.plot(x, kind='grid').show()
				plt.title('stream')
				camelot.plot(x, kind='contour').show()
				print(x.df)
				#print('Accuracy: ', x.accuracy)
				#print('Page: ', x.page)
				print('stream')
				print(x.parsing_report)
				#input(' - Press Enter to proceed')
				#plt.close('all')
			if i < len(tables_lattice_true_):
				x = tables_1[i]
				#camelot.plot(x, kind='text').show()
				#camelot.plot(x, kind='grid').show()
				plt.title('tables_lattice')
				camelot.plot(x, kind='contour').show()
				print(x.df)
				#print('Accuracy: ', x.accuracy)
				#print('Page: ', x.page)
				print('process_background = False')
				print(x.parsing_report)
				#input(' - Press Enter to proceed')
				#plt.close('all')
			if i < len(tables_lattice_false_):
				x = tables_1[i]
				#camelot.plot(x, kind='text').show()
				#camelot.plot(x, kind='grid').show()
				plt.title('tables_lattice_false')
				camelot.plot(x, kind='contour').show()
				print(x.df)
				#print('Accuracy: ', x.accuracy)
				#print('Page: ', x.page)
				print('process_background = False')
				print(x.parsing_report)
				#input(' - Press Enter to proceed')
				#plt.close('all')
			input(' - Press Enter to proceed')
			plt.close('all')

		for x in tables_:7
			#camelot.plot(x, kind='text').show()
			#camelot.plot(x, kind='grid').show()
			camelot.plot(x, kind='contour').show()
			print(x.df)
			#print('Accuracy: ', x.accuracy)
			#print('Page: ', x.page)
			print(x.parsing_report)
			input(' - Press Enter to proceed')
			plt.close('all')
		# --

		for x in tables_1:
			#camelot.plot(x, kind='text').show()
			#camelot.plot(x, kind='grid').show()
			camelot.plot(x, kind='contour').show()
			print(x.df)
			#print('Accuracy: ', x.accuracy)
			#print('Page: ', x.page)
			print(x.parsing_report)
			input(' - Press Enter to proceed')
			plt.close('all')
'''
		# --
	# --
# --



# class ExtractTable:

#         url_string = ""
#         compare_string_list = ['management fee','fees and expenses','estimated total management costs']

#         def __init__(self, url_string_):
#                 self.url_string = url_string_

#         def get_tables(self, url_string):
#                 tables = camelot.read_pdf(self.url_string,pages = 'all', flavor = 'stream',flag_size=True)
#                 return tables

#         def similarity_thing(self, string_,compare_string_list):
#                 found = False
#                 highest = 0
#                 similarity_list = []
#                 for item in self.compare_string_list:
#                     similarity_list.append(SequenceMatcher(None,item,string_).ratio())
#                 for i in similarity_list:
#                         if i > highest:
#                                 highest = i
#                 return highest

#         def get_specific_tables(self, url_string):
#                 tables = get_tables(self.url_string)
#                 df_new_list =[]
#                 all_df = pd.DataFrame()
#                 for table in tables:
#                         table_df = table.df
#                         table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
#                         df_list = table_df.values.tolist()
#                         for i in range(len(df_list)):
#                                 for j in df_list[i]:
#                                         x = SequenceMatcher(None,'type of fee or costs',j).ratio()
#                                         if x > 0.6:
#                                                 df_new_list.append(table_df)
#                                                 all_df = pd.concat(df_new_list)
#                 return all_df


#         def get_similar_row(self, all_df):
#                 new_df_list = self.all_df.values.tolist()
#                 found = []
#                 highest = 0
#                 for i in range(len(new_df_list)):
#                         for j in new_df_list[i]:
#                                 similarity_value = similarity_thing(j.lower(),compare_string_list)
#                                 if similarity_value> highest:
#                                         highest = similarity_value
#                                         found = new_df_list[i]
#                 return found

#         def extract_table(self,url_string):
#                 all_df = get_specific_tables(self.url_string)
#                 found = get_similar_row(all_df)

#                 fee_value = ""
#                 for i in found:
#                         x = i.find("0.")
#                         if x != -1:
#                                 fee_value = i[x:(x+10)]
#                 management_fee_list = []
#                 management_fee_list.append(fee_value)
#                 return management_fee_list


'''

class TableExtraction:

	url_string = ''
	extracted_tables_ = {
		'stream': [],
		'lattice_b_t': [],
		'lattice_b_f': [],
	}

	filtered_tables_ = {
		'stream': [],
		'lattice_b_t': [],
		'lattice_b_f': [],
	}

	extracted_tables = []
	filtered_tables = []

	def __init__(self, url_string_):
		self.url_string = url_string_

	def extract_tables(self):
		#self.extracted_tables['stream'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'stream',flag_size=False)
		#self.extracted_tables['lattice_b_t'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'lattice',flag_size=False, process_background = True)
		#self.extracted_tables['lattice_b_f'] = camelot.read_pdf(self.url_string, pages = 'all', flavor = 'lattice',flag_size=False, process_background = False)#pdfplumber
		page_detections = run_pdf_table_detection(self.url_string)
		self.extracted_tables = page_detections
		

	def filter_tables(self):

		for table_type in self.extracted_tables:
			tables_ = self.extracted_tables[table_type]
			for table_ in tables_:
				table_df = table_.df
				drop_table = False
				# If only one column or one row - drop
				if table_.shape[0] <= 1 or table_.shape[1] <= 1:
					drop_table = True

				if not drop_table:
					table_object = self.generate_table_stats(table_)
					self.filtered_tables[table_type].append(table_object)
		# --

	def generate_table_stats(self, table_):

		# Table bbox
		cols_ = [item for t in table_.cols for item in t]
		rows_ = [item for t in table_.rows for item in t]

		table_bbox = ((min(cols_),max(rows_)), (max(cols_), min(rows_)))
		table_bbox_string = str(min(cols_)) + ',' + str(max(rows_)) + ',' + str(max(cols_)) + ',' + str(min(rows_))

		# Table midpoint
		x_mid = (min(cols_)+max(cols_))/2
		y_mid = (min(rows_)+max(rows_))/2

		table_midpoint = (x_mid, y_mid)

		# Table area
		table_area = (max(cols_) - min(cols_)) * (max(rows_) - min(rows_))

		table_object = {
			'table': table_,
			'bbox': table_bbox,
			'bbox_string': table_bbox_string,
			'midpoint': table_midpoint,
			'area': table_area
		}

		return table_object
'''


'''
#import re
#found = []
#found_investment = []

def camalot_test():
	#this extracts the apir code
	for table in tables:
		table_df = table.df
		table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
		df_list = table_df.values.tolist()
		#print(df_list)
		for i in range(len(df_list)):
			for j in df_list[i]:
				x = j.find("APIR")
				if x != -1:
					end = j.find("AU")
					APIR_code = j[x:(end+2)]


	print(APIR_code)

	#function to get highest similarity ratio based on defined strings
	def similarity_thing(string_):
		found = False
		highest = 0
		similarity_list = []
		similarity_list.append(SequenceMatcher(None,'management fee',string_).ratio())
		similarity_list.append(SequenceMatcher(None,'fees and expenses',string_).ratio())
		similarity_list.append(SequenceMatcher(None,'estimated total management costs',string_).ratio())
		for i in similarity_list:
			if i > highest:
				highest = i
		return highest



	#gets the specific tables(tables matching with type of fee or costs) and concatenates them in a dataframe
	df_new_list =[]
	for table in tables:
		table_df = table.df
		table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
		df_list = table_df.values.tolist()
		for i in range(len(df_list)):
			for j in df_list[i]:
				x = SequenceMatcher(None,'type of fee or costs',j).ratio()
				if x > 0.6:
					df_new_list.append(table_df)
					#all_df = pd.concat(df_new_list)


	all_df = pd.concat(df_new_list)
	print(all_df)


	#finds and extracts the most relatable list to get the management fee
	new_df_list = all_df.values.tolist()
	found = []
	highest = 0
	for i in range(len(new_df_list)):
		for j in new_df_list[i]:
			similarity_value = similarity_thing(j.lower())
			print(j)
			print(similarity_value)
			if similarity_value> highest:
				highest = similarity_value
				found = new_df_list[i]

	print(found)

	#extracting of management fee value into variable fee_value
	fee_value = ""
	for i in found:
		x = i.find("0.")
		if x != -1:
			fee_value = i[x:(x+10)]

	print(fee_value)




#"https://www.hyperion.com.au/wp-content/uploads/Hyperion-Australian-Growth-Companies-Fund-PDS-Additional-Information.pdf"

def run_extraction(pdf_url):

	tables = camelot.read_pdf(pdf_url,pages = 'all', flavor = 'stream',flag_size=True)
	df_list = []
	for table in tables:
		# Turn into dataframe
		table_df = table.df
		table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
		# Add to df_list
		df_list.append(table_df)
	# --

	# Now we can combine all of them into a new dataframe
	all_df = pd.concat(df_list)

	found = []
	found_investment = []
	for table in tables:
		table_df = table.df
		table_df.rename(columns=table_df.iloc[0]).drop(table_df.index[0])
		df_list = table_df.values.tolist()

		for i in range(len(df_list)):
			for j in df_list[i]:
				similarity_ = SequenceMatcher(None,'Fees and expenses',j).ratio()
				similarity_2 = SequenceMatcher(None,'initial investment',j).ratio()
				if (similarity_ > 0.65):
					found = df_list[i]
				if (similarity_2 > 0.65):
					found_investment = df_list[i]


	fee_value = ""
	for i in found:
		x = i.find("0.")
		if x != -1:
			fee_value = i[x:len(i)]
			print(x)

	investment_value = ""
	for i in found_investment:
		x = i.find("$")
		if x != -1:
			investment_value = i[x:len(i)]
			print(x)

	#print('Fee & Investment values')
	print(fee_value)
	print(investment_value)
	return fee_value, investment_value


'''










# --
