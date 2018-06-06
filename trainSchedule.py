#! python3
#trainSchedule.py - Creates a JSON file of route of the train from train number

import requests,bs4,json
import os,sys

#Input
trainNum = input("Enter the 5-digit train number: ") 

if(len(trainNum)!=5):
	sys.exit('Invalid Train Number!!')

#working url for scraping train route
url = f'http://enquiry.indianrail.gov.in/xyzabc/ShowTrainSchedule?trainNo={trainNum}'
os.makedirs('trains',exist_ok=True) #store .json in ./trains

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
			'day': day,
			'sch_arrival': arrivalTime,
			'sch_depart': departTime,
			'distance': distance
	}

	schedule.append(rowData)


# JSON File
with open(f'./trains/{trainNum}.json', 'w') as outfile:
    json.dump(schedule, outfile)


print('Done!')
