#!/usr/bin/env python3.9

#Import pymongo for mongoDB integration, csv for file creation
import pymongo
import csv
import json
import ssl
import datetime

class managedFund:
    def __init__(self, name, age):
        self.name = name
        self.apir = apir
        self.fee_perf = fee_perf
        self.fee_admin = fee_admin
        self.fee_mgmt = fee_mgmt
        self.buy_sell = buy_sell
        self.nav = nav
        self.perf = perf
        self.allocation = allocation
        self.top = top
        self.bot = bot
        self.allocation_range = allocation_range


def extractSuper():
    '''Function to extract data from the database
    Outputs two .csv files, with the data transposed
    '''
    #Connect with the export user
    client = pymongo.MongoClient("mongodb+srv://extractor:I62EK5HE5yBL59Yz@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
    #Database and collection information
    db = client.SuperScrapper
    fundCol = db.funds
    offeringCol = db.offerings

    #variables for the program
    fundIDs = []
    dates = []
    offeringList = []
    perfTable = []

    #get list of funds
    funds = list(fundCol.find())

    #build list of funds we are tracking
    for fund in funds:
        fundIDs.append(fund["_id"])

    #extract all the offerings for each fund
    for fundID in fundIDs:
        #print('+-- Getting ' + fundID + ' Data --+')
        #get list of offerings for each fund
        offerings = list(offeringCol.find({"fund_id": fundID}, {'fund_id' : 1, 'name' : 1, 'monthly_performances' : 1, 'historical_performances' : 1}))
        
        for offering in offerings:
            #print("\t" + offering['name'])
            #Build list of dates there is recorded data for
            for period in offering['monthly_performances']:
                if period['Date'] not in dates:
                    dates.append(period['Date'])
            #Add the offering to the list of offerings
            offeringList.append(offering)

    #remove duplicates from the date list, then sort so they're in order
    dates = list(dict.fromkeys(dates))
    dates.sort()

    #Write the data to the database
    with open('performance.csv', 'w', newline='') as perf:
        perf_writer = csv.writer(perf)
        #Build header row with all dates
        row = ['Offering']
        for date in dates:
            row.append(date)
        #Write the header row
        perf_writer.writerow(row)
        perfTable.append(row)
        #For every offering we track:
        for offering in offeringList:
            #build dictionary to hold every date that fund has records for
            dateDict = {}
            for period in offering['monthly_performances']:
                dateDict[period['Date']] = period['Value']
            
            #build row for the offering
            row = [offering['fund_id'] + " " + offering['name']]
            for date in dates:
                #check each date we recorded
                if date in dateDict:
                    #if that date is in the reported dates for the offering
                    #but the data is either '-' or 'not a number' then write an empty cell
                    #the '!=' part is a quick NaN check thanks to python magic
                    if dateDict[date] == '-' or dateDict[date] != dateDict[date]:
                        row.append("")
                    else:
                        #if the date is in the data, and is a number, add that to the row
                        row.append(dateDict[date])
                else:
                    #If it isnt in the dates, add an empty cell
                    row.append("")
            #write row for that offering
            perf_writer.writerow(row)
            perfTable.append(row)

    newPerf = []
    for i in range(0, len(perfTable[0])):
        newPerf.append([])

    for i in range(len(perfTable[0])):
        for j in range(len(perfTable)):
            newPerf[i].append(perfTable[j][i])

    with open('performance_pivot.csv', 'w', newline='') as perf_pivot:
        perf_pivot_writer = csv.writer(perf_pivot)
        for row in newPerf:
            perf_pivot_writer.writerow(row)

    
    print(str(datetime.datetime.now()) + ": Super Extracted")

def extractFundManagers():
    #print("Getting Fund Manager  Data...")
     #Connect with the export user
    client = pymongo.MongoClient("mongodb+srv://extractor:I62EK5HE5yBL59Yz@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
    #Database and collection information
    db = client.SuperScrapper
    man_data = db.fund_managers
    trav_data = db.site_traverse_data

    offeringCol = db.offerings

    #variables for the program
    fund_managers = {}
    useful_data = {}

    #get list of funds
    funds = list(trav_data.find())
    for fund in funds:
        fund_managers[fund['domain']['domain_file']] = []
        for apir in fund['domain']['page_filters']:
            fund_managers[fund['domain']['domain_file']].append(apir)
    #Get the extracted data
    info = list(man_data.find())
    for entry in info:
        if 'data' in entry:
            useful_data[entry['APIR_code']] = entry['data']['_c']
    
    with open('fund_managers.csv', 'w', newline='') as managers:
        man_writer = csv.writer(managers)
        top_row = "Fund Manager,APIR,Name,Performance Fee,Management Fee,Admin Fee,Buy/Sell Spread,NAV,Performance,Asset Allocation,Ranges,Top Holdings,Bottom Holdings,Class Size,Fund Sizr,Strategy Size".split(",")
        man_writer.writerow(top_row)
        for man in fund_managers:
            #print("+---- " + man)
            for f in fund_managers[man]:

                if f in useful_data:
                    #print("|-- " + f)
                    cur_data = useful_data[f]
                    name = "Not Currently Available"
                    apir = f
                    perf_fee = "Not Currently Available"
                    admin_fee = "Not Currently Available"
                    mgmt_fee = "Not Currently Available"
                    buy_sell = "Not Currently Available"
                    nav = "Not Currently Available"
                    performance = "Not Currently Available"
                    allocation = "Not Currently Available"
                    ranges = "Not Currently Available"
                    top_hold = "Not Currently Available"
                    bot_hold = "Not Currently Available"
                    class_size = "Not Currently Available"
                    fund_size = "Not Currently Available"
                    strat_size = "Not Currently Available"

                    if "Performance Fee" in cur_data:
                        perf_fee = cur_data['Performance Fee']['extracted_value']

                    if "Management Fee" in cur_data:
                        mgmt_fee = cur_data['Management Fee']['extracted_value']
                    
                    if "Buy/Sell spread" in cur_data:
                        buy_sell = cur_data['Buy/Sell spread']['extracted_value']

                    if "NAV" in cur_data:
                        nav = cur_data['NAV']['extracted_value']

                    if "Performance" in cur_data:
                        performance = json.dumps(cur_data['Performance']['extracted_value'])

                    if "Asset Allocation" in cur_data:
                        allocation = json.dumps(cur_data['Asset Allocation']['extracted_value'])

                    ## Ranges

                    if "Top Holdings" in cur_data:
                        top_hold = json.dumps(cur_data['Top Holdings']['extracted_value'])

                    if "Bottom Holdings" in cur_data:
                        bot_hold = json.dumps(cur_data['Bottom Holdings']['extracted_value'])

                    if "Class Size" in cur_data:
                        class_size = cur_data['Class Size']['extracted_value']
                    if "Fund Size" in cur_data:
                        fund_size = cur_data['Fund Size']['extracted_value']
                    if "Strategy Size" in cur_data:
                        strat_size = cur_data['Strategy Size']['extracted_value']
                    
                    
                    row = []
                    row.append(man)
                    row.append(apir)
                    row.append(name)
                    row.append(perf_fee)
                    row.append(mgmt_fee)
                    row.append(admin_fee)
                    row.append(buy_sell)
                    row.append(nav)
                    row.append(performance)
                    row.append(allocation)
                    row.append(ranges)
                    row.append(top_hold)
                    row.append(bot_hold)
                    row.append(class_size)
                    row.append(fund_size)
                    row.append(strat_size)
                    man_writer.writerow(row)
            #print("+-------------")
    print(str(datetime.datetime.now()) + ": Fund Managers Extracted")



    

def extract():
    extractSuper()
    extractFundManagers()


if __name__ == '__main__':
    extract()