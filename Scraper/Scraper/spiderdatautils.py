










def month_format(month_strs, year_value):
    date_convertions = {'Jan':"01",'Feb':"02",'Mar':"03",'Apr':"04",'May':"05",'Jun':"06",'Jul':"07",'Aug':"08",'Sep':"09",'Oct':"10",'Nov':"11",'Dec':"12"}
    month_ints = []
    for month_str in month_strs:
        if month_str in date_convertions:
            month_ints.append(date_convertions[month_str] + "-" + year_value)
    return month_ints














































# --
