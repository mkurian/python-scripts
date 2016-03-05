import string
import os
import pymongo
import datetime

def readReportAndProcess():

	#for every file in 'dailyreports1/emails1/'
	for file in os.listdir('dailyreports/emails/'):
		dateStr = file.partition('.')[0]
		
	#for only one file, comment the lines above, uncomment the line below and specify the date(filename)
		#dateStr = '2011-03-12'
		
		reportIds = []
		#split the daily report into individual reports	
		splitReportIntoFiles(dateStr,reportIds)
			#process each report and generate data
		for report in reportIds:
			if report == '2':
				colNames =['pubdownloaded', 'initsyncstart', 'initsyncend', 'avgsynctime', 'mediansynctime', 'minsynctime', 'maxsynctime']
				processSummaryReport(dateStr,colNames, '2')
			elif report == '3':
				colNames =['initsyncnum', 'initsyncsize', 'incsyncnum', 'incsyncsize']
				processSummaryReport(dateStr,colNames, '3')
			elif report == '4':
				colNames =['companynum_4', 'readnum_4', 'onesec_4', 'tensec_4', 'avg_4', 'median_4', 'max_4']
				processSummaryReport(dateStr,colNames, '4')
			elif report == '5':
				colNames =['company_5', 'write_5', 'writefailure_5', 'writefailure_percent_5']
				processSummaryReport(dateStr,colNames, '5')
			elif report == '5.1':
				colNames =['company_51', 'companyfail_51', 'companyfail_percent_51', 'wbreq_51', 'wbreqfail_51','wbreqfail_percent_51', 'wbrec_51','wbrec_fail_51','wbrec_fail_percent_51']
				processSummaryReport(dateStr,colNames, '5.1')		
			elif report == '1':
				colNames =['total_1', 'last30_1', 'royalty_1']
				processSummaryReport(dateStr,colNames, '1')
			elif report == '1.1':
				colNames =['last7_use_11']
				processSummaryReport(dateStr,colNames, '1.1')
			elif report == '1.11':
				colNames =['last7_upload_111']
				processSummaryReport(dateStr,colNames, '1.11')
			elif report == '1.3':
				colNames =['number_13', 'date_13','time_13']
				processSummaryReport(dateStr,colNames, '1.3')
			elif report == '6':
				colNames =['company_6', 'rows_6', 'avgrows_6','size_6']
				processSummaryReport(dateStr,colNames, '6')			
			elif report == '8':
				colNames =['users_8']			
				processDailyReportPubVersion(dateStr,colNames, '8')
			elif report == '9':
				colNames =['forcesync_9','forcesync_company_9', 'cleanup_9', 'cleanup_company_9']			
				processSummaryReport(dateStr,colNames, '9')

			

def splitReportIntoFiles(dateStr, reportIds):

	list = []
	filename ='test'	

	f = open('dailyreports/emails/'+dateStr+'.txt')
	for line in f:
		if line.rfind('rpt_id=') != -1:		
			f1 = open('dailyreports/reports1/file'+filename+'-'+dateStr+'.txt', 'w')
			reportIds.append(filename.partition('=')[2])
			for str in list:
				f1.write(str)				
			list = [""]
			list.append(line)		
			filename = line.partition(':')[0]
			f1.close()
		else:		
			list.append(line)
	f.close()
	
#process a summary report
def processSummaryReport(dateStr, colNames, reportId):
	
	collistLine = -1	
	date = []	
	values = []
	for idx in range(len(colNames)):
		list = []
		values.append(list)
			
	#read the new report and add to the existing values	
	try:
		filename = 'dailyreports/reports1/filerpt_id='+reportId+'-'+dateStr+'.txt'
		print(filename)
		lineNo = 0	
		f = open(filename, 'r')
		for line in f:		
			if line.rfind('Date') != -1:			
				collistLine = lineNo						
			elif lineNo == collistLine +1 :
				print('data begins')
			elif line.rfind('rows selected.') != -1:
				print('skip')
			else:	
				i = 0
				for part in line.split():															
					if i==0 :
						if part in date: 														
							break
						else:							
							date.append(part)
					else:
						part = part.replace(',', '')	
						part = part.replace('%', '')												
						values[i-1].append(part)						
					i += 1
					
			lineNo += 1
	except IOError as e:
		print("({})".format(e))		
			
	from pymongo import Connection
	connection = Connection()
	db = connection["reportdataDB"]
	
	k = 0	
	while k < len(colNames): 		
		j = 0
		while j < len(date):	
			obj = {"type": colNames[k], "date": date[j], "value": values[k][j]}
			repdataDB = db.reportdataDB
			if repdataDB.find({"type": colNames[k], "date": date[j]}) != None:
				repdataDB.remove({"type": colNames[k], "date": date[j]})	
			repdataDB.insert(obj)	
			j +=1
		k += 1
	
	
#process a daily report
def processDailyReportPubVersion(dateStr, colNames, reportId):
	
	collistLine = -1	
	date = []	
	values = []
	pubVersionNames =[]
	
		
	#read the new report and add to the existing values	
	try:
		filename = 'dailyreports/reports1/filerpt_id='+reportId+'-'+dateStr+'.txt'
		print(filename)
		lineNo = 0	
		counter = 1
		date.append(dateStr)
		f = open(filename, 'r')
		for line in f:		
			if line.rfind('Date') != -1:			
				collistLine = lineNo						
			elif lineNo == collistLine +1 :
				print('data begins')
			elif line.rfind('rows selected.') != -1:
				print('skip')
			else:	
				i = 0
				for part in line.split():						
					if i==1:	
						str  = 'pub'+part
						str = str.replace('.', '')							
						if str in pubVersionNames: 																					
							print(str +' present')
						else:													
							pubVersionNames.append(str)							
					elif i==2:
						part = part.replace(',', '')	
						part = part.replace('%', '')							
						if len(values) < counter:	
							list = [] 
							values.append(list)
						values[counter - 1].append(part)	
						counter += 1					
								
					i += 1					
			lineNo += 1			
						
	except IOError as e:
		 print("({})".format(e))		
		
	from pymongo import Connection
	connection = Connection()
	db = connection["reportdataDB"]
	
	k = 0	
	while k < len(pubVersionNames): 		
		j = 0
		while j < len(date):	
			obj = {"type": pubVersionNames[k], "date": date[j], "value": values[k][j]}
			repDB = db.reportdataDB
			if repDB.find({"type": pubVersionNames[k], "date": date[j]}) != None:
				repDB.remove({"type": pubVersionNames[k], "date": date[j]})	
			repDB.insert(obj)	
			j +=1
		k += 1
	

readReportAndProcess()
