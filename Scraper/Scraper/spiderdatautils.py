
import dateparser
import datetime




# TODO: Make date format with zero at front '07-2017' instead of '7-2017'
# TODO: Make year first then month

# TODO: Make year value a settings option thingy so that this can handle different stuff

'''
def month_format(month_strs, year_value):

    # Formating reference: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    date_format = '%Y-%m'
    month_dates = []
    for month_str in month_strs:
        combined_string = year_value + month_str
        parsed_value = dateparser.parse(combined_string,settings={'DATE_ORDER': 'YMD'})
        # Using output python base datetime -> convert into string THEN append
        month_dates.append(parsed_value.strftime(date_format))
    return month_dates
'''


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





'''
#,settings={'DATE_ORDER': 'YMD'} , date_formats = ['%y','%m']
#month_dates.append(str(parsed_value.year) + "-" + str(parsed_value.month))
#print(type(parsed_value))
#print(parsed_value)
#print(parsed_value.strftime('%Y-%m'))

print('wOOOOOOOOOOOOOOOOOOOOOAHAYFWBGYwf -------------')
print(dateparser.parse('1/02/2021',settings={'DATE_ORDER': 'DMY'}).strftime('%Y-%m'))
'''










































# --
