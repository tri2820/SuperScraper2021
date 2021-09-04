import pdfplumber



import requests
import io


import re


def font_size_filter(in_object):
    success = True
    if 'size' in in_object:
        font_size = in_object['size']
        if font_size < 6:
            success = False
    # --
    return success
# --






url = "https://www.fidante.com/-/media/Shared/Fidante/ALPH/ASSF_PDS.pdf?la=en"
#url = "https://au.dimensional.com/dfsmedia/f27f1cc5b9674653938eb84ff8006d8c/59107-source/options/download/pds-world-equity-trust-au.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"
#url = "https://www.hyperion.com.au/app/uploads/2021/06/Hyperion-Australian-Growth-Companies-Fund-PDS.pdf"


r = requests.get(url)
f = io.BytesIO(r.content)


with pdfplumber.open(f) as pdf:
    page = pdf.pages[4]
    
    page = page.filter(font_size_filter)
    
    # 1st char test
    print(page.chars[0])
    
    # Img
    im = page.to_image(resolution=150)
    
    # Chars
    words = page.extract_words(x_tolerance=1, y_tolerance=1)
    
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
        
        word_line = word_lines[pos]
        
        line_rect = {
            'x0': word_rects[0]['x0'],
            'x1': word_rects[-1]['x1'],
            #'y0': word_rects[0]['y0'],
            #'y1': word_rects[-1]['y1'],
            
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
    search_words = ['asset class']
    
    line_indecies = list(word_lines.keys())
    
    line_indecies = sorted(line_indecies, reverse=False)
    #print(line_indecies)
    
    table_line_rects = []
    
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
                print(last_line['line_rect']['top'], next_line['line_rect']['bottom'])
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
    
    im.draw_rects(table_line_rects, stroke=(35, 61, 255), fill=(35, 61, 255, 30))
    #im.draw_rects(words)
    im.draw_rects(word_line_rects_not_table, stroke=(102, 255, 68), fill=(102, 255, 68, 30))
    
    
    
    # Save
    im.save('test_img.png', format="PNG")
# --



