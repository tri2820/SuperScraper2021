
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
 - year_value(Integer value): if only the month is given in date_strings then year_value can be added if difined

'''
#, date_order = None

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
    data_value_ = re.sub('[^-\d.]+','',str(data_value))
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












































# --
