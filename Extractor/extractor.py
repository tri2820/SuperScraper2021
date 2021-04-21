import pymongo
import csv
import math

def extract():
    #Connect with the export user
    client = pymongo.MongoClient("mongodb+srv://extractor:I62EK5HE5yBL59Yz@cluster0.tadma.mongodb.net/SuperScrapper?retryWrites=true&w=majority")
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
        print('+-- Getting ' + fundID + ' Data --+')
        #get list of offerings for each fund
        offerings = list(offeringCol.find({"fund_id": fundID}, {'fund_id' : 1, 'name' : 1, 'monthly_performances' : 1, 'historical_performances' : 1}))
        
        for offering in offerings:
            print("\t" + offering['name'])
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
