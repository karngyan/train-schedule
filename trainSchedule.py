#! python3
#trainSchedule.py - Creates a JSON file of route of the train from train number

import requests,bs4,json
import os,sys
import xlsxwriter

#Input
trainNum = input("Enter the 5-digit train number: ") 

if(len(trainNum)!=5 or trainNum.isdigit()==False):
	sys.exit('Invalid Train Number!!')

#working url for scraping train route
url = f'http://enquiry.indianrail.gov.in/xyzabc/ShowTrainSchedule?trainNo={trainNum}'
os.makedirs(f'./trains/{trainNum}',exist_ok=True) #store .json in ./trains

res=requests.get(url)
res.raise_for_status()

#soupify
soup = bs4.BeautifulSoup(res.text,'lxml') #Parse the html as a string

#Invalid Train Number
if('Invalid train' in soup.find('body').text):
	sys.exit('Invalid Train Number!!')


#Get Train Details
trainDetails = soup.find('div',id='trainDetailDiv').select('b')

trainName = trainDetails[1].getText().strip()
trainType = trainDetails[2].getText().strip()
#trainNum (byUser)

#To store the entire route
schedule = [
		{

		'train_name': trainName,
		'train_number': trainNum,
		'train_type':trainType
	}
] 

#Scrape the Route table
table=soup.select('tbody tbody tr')

for row in table:

	station = row.find_all('td')

	stationName,stationCode=station[1].text.split('[')

	stationName=stationName.strip()
	stationCode = (stationCode.strip())[:-1]
	day = station[2].text.strip()
	
	time=station[3].select('div')
	arrivalTime = time[1].text.strip()
	departTime = time[2].text.strip()

	distance = station[4].text.strip()


	rowData = {
			'station_name': stationName,
			'station_code': stationCode,
			'day': int(day),
			'sch_arrival': arrivalTime,
			'sch_depart': departTime,
			'distance': int(distance)
	}

	schedule.append(rowData)


## JSON File
with open(f'./trains/{trainNum}/{trainNum}.json', 'w') as outfile:
    json.dump(schedule, outfile)


## EXCEL File
#xlsxwriter can't modify existing files
#delete if already exists
try:
	os.remove(f'./trains/{trainNum}/{trainNum}.xlsx')
except OSError:
	pass


#open workbook, add a sheet
workbook = xlsxwriter.Workbook(f'./trains/{trainNum}/{trainNum}.xlsx')
worksheet = workbook.add_worksheet(f'{trainName}')

#add formats
bold = workbook.add_format( { 'bold' : 1 } )

#write initial train details
worksheet.write(0,0,trainName)
worksheet.write(1,0,int(trainNum))
worksheet.write(2,0,trainType)

#make the table

#headers
worksheet.write(4,0,'S. No.',bold)
worksheet.write(4,1,'Station Name',bold)
worksheet.write(4,2,'Code',bold)
worksheet.write(4,3,'Day',bold)
worksheet.write(4,4,'Arrives',bold)
worksheet.write(4,5,'Departs',bold)
worksheet.write(4,6,'Distance',bold)

#set column width
worksheet.set_column('B:B',30)

#(i,j) = cell of the table
index=1 #serial number
i=5
j=1
for row in schedule[1:]:
	worksheet.write(i,0,index)
	for value in row.values():
		worksheet.write(i,j,value)
		j+=1

	i+=1
	index+=1
	j=1

workbook.close()


print('Done! (.json and .xlsx both)')
