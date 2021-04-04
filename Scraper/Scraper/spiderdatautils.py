
import dateparser
import datetime

'''
date_string = 'Feb-2017'

parsed_value = dateparser.parse(date_string)

print(parsed_value.year,parsed_value.month)
'''






def month_format(month_strs, year_value):
    month_dates = []
    for month_str in month_strs:
        combined_string = month_str + year_value
        parsed_value = dateparser.parse(combined_string)
        month_dates.append(str(parsed_value.month) + "-" + str(parsed_value.year))
    return month_dates





'''
def month_format(month_strs, year_value):
    date_convertions = {'Jan':"01",'Feb':"02",'Mar':"03",'Apr':"04",'May':"05",'Jun':"06",'Jul':"07",'Aug':"08",'Sep':"09",'Oct':"10",'Nov':"11",'Dec':"12"}
    month_ints = []
    for month_str in month_strs:
        if month_str in date_convertions:
            month_ints.append(date_convertions[month_str] + "-" + year_value)
    return month_ints
'''














































# --
