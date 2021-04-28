
import dateparser
import datetime

import re




# TODO: Make date format with zero at front '07-2017' instead of '7-2017'
# TODO: Make year first then month

# TODO: Make year value a settings option thingy so that this can handle different stuff




'''
-- Settings --

date_strings([string]): strings of dates

optionals:
# NOTE: This format will probably change in future
 - year_value(Integer value): if only the month is given in date_strings then year_value can be added if difined


'''

#- year_value(Integer value): if only the month is given in date_strings then year_value can be added if difined



def month_format(date_strings, year_value = None, date_format = None, parse_order = None):

    # Formating reference: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    date_format_ = '%Y-%m'
    if date_format:
        date_format_ = date_format

    month_dates = []

    parse_order_ = 'YMD'
    if parse_order:
        parse_order_ = parse_order

    for month_str in date_strings:
        combined_string = month_str
        # If year value
        if year_value:
            combined_string = year_value + combined_string
        parsed_value = dateparser.parse(combined_string,settings={'DATE_ORDER': parse_order_})
        # Using output python base datetime -> convert into string THEN append
        #print(parsed_value.strftime(date_format))
        month_dates.append(parsed_value.strftime(date_format_))
    return month_dates
# --





def digit_value_format(data_value):
    # Remove symbols and other things that are not standard
    data_value_ = re.sub('[^-+Ee\d.]+','',str(data_value))
    #print(data_value,data_value_)
    # If there are digits indication its probably not a null value then try to convert to float
    if re.search('[\d]',data_value_) != None:
        data_value_ = float(data_value_)
    # --
    return data_value_
# --



def digit_list_value_format(data_values):
    data_values_ = []
    for data_value in data_values:
        new_data_value = digit_value_format(data_value)
        data_values_.append(new_data_value)
    # --
    return data_values_
# --


def lower_underscore(start_string):
    underscores = re.sub('[ ]+','_',str(start_string))
    lowercase = underscores.lower()
    remove_symbols = re.sub('[^\w_]+|[0-9]+','',lowercase)
    end_string = remove_symbols
    return end_string
# --





'''

# - year_values(list(strings)): index-esque list with years to for each value

# - year_values(dict-object): {'2019': [], '2020': []}

def month_format(date_strings, year_values = None, date_format = None, parse_order = None):

    # Formating reference: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    date_format_ = '%Y-%m'
    if date_format:
        date_format_ = date_format

    month_dates = []

    parse_order_ = 'YMD'
    if parse_order:
        parse_order_ = parse_order
    # --

    month_count = 0

    for month_str in date_strings:
        combined_string = month_str
        # If year values
        if year_values:
            # If a value exists for this part
            if year_values[month_count]:
                combined_string = year_values[month_count] + combined_string
        parsed_value = dateparser.parse(combined_string,settings={'DATE_ORDER': parse_order_})
        # Using output python base datetime -> convert into string THEN append
        #print(parsed_value.strftime(date_format))
        month_dates.append(parsed_value.strftime(date_format_))
        month_count += 1
    return month_dates
# --
'''




































# --
