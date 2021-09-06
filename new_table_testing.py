import pdfplumber



import requests
import io


import re

import numpy as np

from sklearn.neighbors import KernelDensity

from scipy.signal import argrelextrema

import matplotlib.pyplot as plt

from scipy.signal import find_peaks

from scipy import stats as sci_stats

import math

import pandas as pd



def font_size_filter(in_object):
    success = True
    if 'size' in in_object:
        font_size = in_object['size']
        if font_size < 6:
            success = False
    # --
    return success
# --


#from numpy import array, linspace



url = "https://www.fidante.com/-/media/Shared/Fidante/ALPH/ASSF_PDS.pdf?la=en"
url = "https://au.dimensional.com/dfsmedia/f27f1cc5b9674653938eb84ff8006d8c/59107-source/options/download/pds-world-equity-trust-au.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://apngroup.com.au/wp-content/uploads/2019/07/PFIF-PDS_JUN2019_combined.pdf"
#url = "https://www.bennelongfunds.com/download/be20aef/performance/may-2021"

url = "https://www.benthamam.com.au/assets/fundreports/Bentham-Global-Income-Fund-Profile-2019-FINAL.pdf"

url = "https://www.fidante.com/-/media/Shared/Fidante/ALPH/ASSF_PDS.pdf?la=en"

url = "https://apngroup.com.au/wp-content/uploads/2019/07/PFIF-PDS_JUN2019_combined.pdf"

url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"

url = "https://au.dimensional.com/dfsmedia/f27f1cc5b9674653938eb84ff8006d8c/59107-source/options/download/pds-world-equity-trust-au.pdf"

pg_no = 4

search_texts = ['assets', 'asset class', 'financial year']#'sector allocation']
search_texts = ['target asset']
search_texts = ['asset class']

r = requests.get(url)
f = io.BytesIO(r.content)


class Table:

    def __init__(self):
        """
        Variables:
        """

        self.page_ = None

        self.word_lines = {}
        self.table_collections = []

        return
    

    def extract_words(self, page_):
        if not page_:
            page_ = self.page_
        # Extract words
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
            print('\n -- FOUND -- \n')
        # --
        return
    

    def construct_subtables(self, line_leniency=2):# TODO: Add args and have args for discard ect...


        line_indecies = list(self.word_lines.keys())
        line_indecies = sorted(line_indecies, reverse=False)

        table_line_rects = []
        self.table_collections = []
        
        for pos in self.word_lines:
            word_line = self.word_lines[pos]
            if not word_line['search_found']:
                continue
            print(f'\n - Constructing table for {word_line["search_found"]}')
            
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
            
            table_collection_obj = {
                'table_lines': table_lines,
                'table_columns': []
            }

            self.table_collections.append(table_collection_obj)#table_lines
            
            
            for x in table_lines:
                table_line_rects.append(x['line_rect'])
            # --
            
            # --
        # --
        return
    

    def format_subtables(self):
        for table_collection in self.table_collections:
            print('\n - New Table/collection - \n')

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

                

                print('\n')
                [print(x['text']) for x in word_groups]
                #im.draw_rects([x['group_rect'] for x in word_groups], stroke=(255, 66, 144), fill=(255, 0, 46, 30))
            # --


            """
            -- Create and seperate word group columns --
            """
            x_range_list = []
            # Each lines groups
            #for word_groups in table_line_groups:
            for table_line in table_collection['table_lines']:
                word_groups = table_line['word_groups']
                # Groups on line
                for word_group in word_groups:
                    group_rect = word_group['group_rect']
                    new_x_range = (group_rect['x0'], group_rect['x1'], group_rect['top'], group_rect['bottom'])
                    exists = False
                    for idx, x_range in enumerate(x_range_list):
                        x_range_mid = (x_range[0] + x_range[1]) / 2
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
        for table_collection in self.table_collections:#columns
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
            print(collection_df)
        return

            

'''
x_range_list = []
# Each lines groups
for word_groups in table_line_groups:
    # Groups on line
    for word_group in word_groups:
        group_rect = word_group['group_rect']
        new_x_range = (group_rect['x0'], group_rect['x1'], group_rect['top'], group_rect['bottom'])
        exists = False
        for idx, x_range in enumerate(x_range_list):
            x_range_mid = (x_range[0] + x_range[1]) / 2
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
# --

'''



with pdfplumber.open(f) as pdf:
    page = pdf.pages[pg_no]
    
    page = page.filter(font_size_filter)

    new_table = Table()

    new_table.extract_words(page)
    search_regex = [
        {
            'search': 'asset class',
            'label': 'asset_class',
        }
    ]
    new_table.search_for_subtables(search_regex)
    new_table.construct_subtables(2)
    new_table.format_subtables()
    new_table.create_subtable_dataframes()


'''
# --

with pdfplumber.open(f) as pdf:
    page = pdf.pages[pg_no]
    
    page = page.filter(font_size_filter)
    
    # 1st char test
    #print(page.chars[0])
    
    # Img
    im = page.to_image(resolution=150)
    
    # Chars
    words = page.extract_words(x_tolerance=1, y_tolerance=1, keep_blank_chars=True)
    
    # Table det
    print('\n Words[0]: ',words[0])
    
    word_lines = {}
    
    for word_obj in words:
        bottom_pos = int(word_obj['bottom'])
        pos_range = [bottom_pos, bottom_pos - 1, bottom_pos + 1]
        
        current_word_line = None
        for pos in pos_range:
            if pos in word_lines:
                current_word_line = word_lines[pos]
                break
        if not current_word_line:
            word_lines[bottom_pos] = {
                'line_rect': {},
                'rects': [],
                'text': '',
            }
            current_word_line = word_lines[bottom_pos]
        # --
        current_word_line['rects'].append(word_obj)
        #print(word_obj)
    # --
    
    
    word_line_rects = []
    for pos in word_lines:
        
        word_rects = word_lines[pos]['rects']
        word_rects = sorted(word_rects, key=lambda word: word["x0"], reverse=False)
        
        line_text = ''
        for word_rect in word_rects:
            line_text += word_rect['text'] + ' '
        
        word_lines[pos]['text'] = line_text
        word_lines[pos]['rects'] = word_rects
        
        # Rects stats
        for rect in word_rects:
            x0 = int(rect['x0'])
            x1 = int(rect['x1'])
            rect['x_mid'] = (x0 + x1) / 2
        
        
        word_line = word_lines[pos]
        
        line_rect = {
            'x0': word_rects[0]['x0'],
            'x1': word_rects[-1]['x1'],

            'x_mid': (word_rects[0]['x0'] + word_rects[-1]['x1']) / 2,
            
            'width': word_rects[0]['x0'] - word_rects[-1]['x1'],
            'height': word_rects[0]['top'] - word_rects[-1]['bottom'],
            
            'top': word_rects[0]['top'],
            'bottom': word_rects[0]['bottom']
        }
        word_lines[pos]['line_rect'] = line_rect
        word_line_rects.append(line_rect)
    # --
    
    #[print(word_lines[x]) for x in word_lines]
    
    
    #im.draw_rects(words)
    #im.draw_rects(word_line_rects)
    
    
    # Word line processing
    search_words = search_texts
    
    line_indecies = list(word_lines.keys())
    
    line_indecies = sorted(line_indecies, reverse=False)
    #print(line_indecies)
    
    table_line_rects = []

    table_collections = []
    
    for pos in word_lines:
        word_line = word_lines[pos]
        found = False
        for search_word in search_words:
            found_idx = word_line['text'].lower().find(search_word)
            if found_idx != -1:
                found = True
                break
        # --
        if not found:
            continue
        # --
        print('\n -- FOUND -- \n')
        
        table_lines = []
        line_idx = line_indecies.index(pos)
        table_lines.append(word_lines[pos])
        #table_line_rects.append(word_lines[pos]['line_rect'])
        
        n = len(line_indecies) - 1
        count = 1
        last_idx = line_idx + 1
        last_line = word_lines[pos]
        extra_lines = 0
        last_line_failed = False
        last_line_failed_idx = 0
        while last_idx < n:
            count += 1
            line_pos = line_indecies[last_idx]
            next_line = word_lines[line_pos]
            
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
                if extra_lines > 2:
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
        
        table_collections.append(table_lines)
        
        
        for x in table_lines:
            table_line_rects.append(x['line_rect'])
        # --
        
        # --
    # --
    
    word_line_rects_not_table = []
    for line_rect in word_line_rects:
        add_line = True
        for table_rect in table_line_rects:
            if line_rect['bottom'] == table_rect['bottom']:
                add_line = False
                break
        if add_line:
            word_line_rects_not_table.append(line_rect)
    
    for table_collection in table_collections:
        print('\n - New collection - \n')
        #mids = []
        #tops = []
        #all_rects = []
        #all_texts = []
        #[print(x['text']) for x in table_collection]


        table_line_groups = []
        for table_line in table_collection:
            rects = table_line['rects']
            #all_rects += rects
            rects_txt = [x['text'] for x in rects]
            #all_texts += rects_txt
            #mids += [x['x_mid'] for x in rects]
            #mids += [x['x0'] for x in rects]
            #mids += [x['x1'] for x in rects]
            #tops += [x['top'] for x in rects]
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

            rect_groups = []
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
                        'group_rect': group_rect
                    }
                    rect_groups.append(group_obj)
                    cur_group = []
                    cur_text = ''
            # --


            table_line['rect_groups'] = rect_groups
            table_line_groups.append(rect_groups)

            
            #print(average_dist)
            #print(rects_txt)
            #print(rect_groups)
            #[print([i['text'] for i in x]) for x in rect_groups]
            print('\n')
            [print(x['text']) for x in rect_groups]#[i['text'] for i in x['text']]
            im.draw_rects([x['group_rect'] for x in rect_groups], stroke=(255, 66, 144), fill=(255, 0, 46, 30))
        # --


        x_range_list = []
        # Each lines groups
        for rect_groups in table_line_groups:
            #x_range_list = []
            # Groups on line
            for rect_group in rect_groups:
                group_rect = rect_group['group_rect']
                new_x_range = (group_rect['x0'], group_rect['x1'], group_rect['top'], group_rect['bottom'])
                exists = False
                for idx, x_range in enumerate(x_range_list):
                    x_range_mid = (x_range[0] + x_range[1]) / 2
                    if (group_rect['x_mid'] >= x_range[0] and group_rect['x_mid'] <= x_range[1]) or (x_range_mid >= new_x_range[0] and x_range_mid <= new_x_range[1]):
                        new_x_range = (min(new_x_range[0], x_range[0]), max(new_x_range[1], x_range[1]), min(new_x_range[2], x_range[2]), max(new_x_range[3], x_range[3]))
                        x_range_list[idx] = new_x_range
                        rect_group['range_idx'] = idx
                        exists = True
                        break
                
                if not exists:
                    rect_group['range_idx'] = len(x_range_list)
                    x_range_list.append(new_x_range)
                # --
        # --

        col_draw_rects_ = []
        for x_range in x_range_list:
            rect_ = {'x0': x_range[0], 'x1': x_range[1], 'top': x_range[2], 'bottom': x_range[3]}
            col_draw_rects_.append(rect_)
        im.draw_rects(col_draw_rects_, stroke=(255, 66, 144), fill=(255, 0, 46, 30))'''


        # TODO: Make arguments things for each line to be run thing



'''
        kde = KernelDensity(kernel='gaussian', bandwidth=4)

        print(mids)

        #fit_data = [166.5, 192.5, 327.0, 344.0, 417.5, 436.0, 68.0, 106.0, 174.0, 346.0, 435.5, 164.5, 348.5, 438.0]
        #print(fit_data)
        fit_data = mids
        fit_data = np.array(fit_data).reshape(-1, 1)

        kde.fit(fit_data)


        s = np.linspace(int(min(mids)),int(max(mids)))

        sample_array = s.reshape(-1, 1)#np.array(s).
        mids_score = kde.score_samples(sample_array)
        #print(mids_score)


        #mi, ma = argrelextrema(mids_score, np.less), argrelextrema(mids_score, np.greater)

        mi, ma = argrelextrema(mids_score, np.less)[0], argrelextrema(mids_score, np.greater)[0]

        print('\n - argrelextrema - idx`s - ')
        print(mi)
        print(ma)

        mi, ma = argrelextrema(mids_score, np.less)[0], argrelextrema(mids_score, np.greater)[0]
        print('\n - argrelextrema - ')
        print(s[mi])
        print(s[ma])

        #print(s[mi][0])

        #split_list = [fit_data[fit_data < mi[0]], fit_data[(fit_data >= mi[0]) * (fit_data <= mi[1])], fit_data[fit_data >= mi[1]]]
        #[mids[mids < mi[0]], mids[(mids >= mi[0]) * (mids <= mi[1])], mids[mids >= mi[1]]]

        #split_list = [fit_data[fit_data < mi[0]], fit_data[(fit_data >= mi[0]) * (fit_data <= mi[1])], fit_data[fit_data >= mi[1]]]
        #split_list = [fit_data[fit_data < s[mi][0]], fit_data[(fit_data >= s[mi][0]) * (fit_data <= s[mi][1])], fit_data[fit_data >= s[mi][1]]]

        min_vals = list(s[mi])
        max_vals = list(s[ma])

        if len(min_vals) < len(max_vals):
            min_vals.append(min_vals[-1])
        if len(max_vals) < len(min_vals):
            max_vals.append(max_vals[-1])

        split_list = []
        split_list_2 = []
        split_list_3 = []
        split_list_4 = []
        for min_x, max_x in zip(min_vals, max_vals):
            new_split = fit_data[(fit_data >= min_x) * (fit_data <= max_x)]
            split_list.append(new_split)
            new_2_list = []
            new_3_list = []
            new_4_list = []
            for mid, top, rect in zip(mids, tops, all_rects):
                if mid + 3 >= min_x and mid - 3 <= max_x:
                    new_2_list.append([int(mid), int(top)])
                    new_3_list.append((rect['x0'],rect['x1'],rect['bottom'],rect['top']))
                    new_4_list.append(rect)
            split_list_2.append(new_2_list)
            if len(new_4_list) > 0:
                split_list_4.append(new_4_list)
            if len(new_3_list) > 0:
                #print(new_3_list)
                big_bbox = {
                    'x0': min([x[0] for x in new_3_list]),
                    'x1': max([x[1] for x in new_3_list]),
                    'bottom': max([x[2] for x in new_3_list]),
                    'top': min([x[3] for x in new_3_list]),
                }
                split_list_3.append(big_bbox)

        print(split_list)

        print(split_list_2)

        total_red = 255 // len(split_list_4)
        for idx, rect_list in enumerate(split_list_4):
            im.draw_rects(rect_list, stroke=(total_red * idx, 58, 34, 30), fill=(total_red * idx, 58, 34, 30))
        
        im.draw_lines(split_list_2, stroke=(102, 255, 68))

        im.draw_rects(split_list_3, stroke=(255, 66, 144), fill=(255, 0, 46, 30))
        #'''

        

        #print(fit_data[fit_data < mi[0]], fit_data[(fit_data >= mi[0]) * (fit_data <= mi[1])], fit_data[fit_data >= mi[1]])

        #print('find_peaks')

        #peaks, _ = find_peaks(mids_score)

        #print(peaks)

        #plt.plot(s,mids_score)
        #plt.show()

        #for i in range(all_texts):
        #    all_texts

        #print(split_list)

        #N = 100
        #X = np.concatenate((np.random.normal(0, 1, int(0.3 * N)),np.random.normal(5, 1, int(0.7 * N))))[:, np.newaxis]
        #print(X)
        #print(mids)
        #[166.5, 192.5, 327.0, 344.0, 417.5, 436.0, 68.0, 106.0, 174.0, 346.0, 435.5, 164.5, 348.5, 438.0]

    #for rect in table_line_rects:
    
    #im.draw_rects(table_line_rects, stroke=(35, 61, 255), fill=(35, 61, 255, 30))
    #im.draw_rects(words)
    #im.draw_rects(word_line_rects_not_table, stroke=(102, 255, 68), fill=(102, 255, 68, 30))
    
    
    # Save
    #im.save('test_img.png', format="PNG")
# --



