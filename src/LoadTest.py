from Queue import Queue
from threading import Thread
import traceback
import time
import json
import ast
import requests
import numpy as np
import sys

class Worker(Thread):
	"""Thread executing tasks from a given tasks queue"""
	def __init__(self, tasks,name):
		Thread.__init__(self)
		self.tasks = tasks
		self.daemon = True
		self.name=name
		self.start()				
	def run(self):
		while True:
			func= self.tasks.get()
			try:
				func()
			except Exception, e:
				print e		
class ThreadPool:
        """Pool of threads consuming tasks from a queue"""
        def __init__(self, num_threads):
			self.tasks = Queue(num_threads)
			for i in range(num_threads):
				Worker(self.tasks,"Thread-"+str(i))
        def add_task(self, func):
			"""Add a task to the queue"""
			self.tasks.put((func))
        def wait_completion(self):
            """Wait for completion of all the tasks in the queue"""
            self.tasks.join()
class Requester:
	
	def __init__(self,Url,EmailId,num_request):
		self.Url = Url# varibale holding to which url it have to make request
		self.EmailId = EmailId
		#self.TotalLog=[]
		self.API2TimeLog=[]# Array holding the time for each request to complete
		self.API1TimeLog=[]# Array holding the time for each request to complete
		self.ResponseCount=0# this variable get increamented after each complete cycle (completion of request to two apis in sequence) 
		self.num_request=num_request#Variable holding nof request to make
	def CalculateLoadStatiscs(self):
		LoadStatstics={
					'API1LoadStatics':{
						"10th percentile":np.percentile(self.API1TimeLog,10),
						"50th percentile":np.percentile(self.API1TimeLog,50),
						"90th percentile":np.percentile(self.API1TimeLog,90),
						"95th percentile":np.percentile(self.API1TimeLog,95),
						"99th percentile":np.percentile(self.API1TimeLog,99),
						"Mean":np.mean(self.API1TimeLog),
						"StandardDeviation":np.std(self.API1TimeLog)
					},
					'API2LoadStatics':{
						"10th percentile":np.percentile(self.API2TimeLog,10),
						"50th percentile":np.percentile(self.API2TimeLog,50),
						"90th percentile":np.percentile(self.API2TimeLog,90),
						"95th percentile":np.percentile(self.API2TimeLog,95),
						"99th percentile":np.percentile(self.API2TimeLog,99),
						"Mean":np.mean(np.array(self.API2TimeLog)),
						"StandardDeviation":np.std(np.array(self.API2TimeLog))
					}
				}	
		print"****************Load Statsics For API1:*************"
		print LoadStatstics['API1LoadStatics']
		print"****************Load Statsics For API2:*************"
		print LoadStatstics['API2LoadStatics']
		sys.exit(0)
	''' Function to send request to our apis '''	
	def MakeRequest(self):
		headers={'X-Surya-Email-Id':self.EmailId}
		Log={'API1':{'TimeTaken':None,'Requeststatus':None},'API2':{'TimeTaken':None,'Requeststatus':None}}
		#print headers
		''' This Code will get executed only when the user had provided the url and email id '''
		try:
			if ((self.EmailId !="") & (self.Url !="") ):
				API1_Response=None # variable to hold the response of the API1
				API2_Response=None # variable to hold the response of the API2			
				start = time.time() #variable to hold the startind time 
				API1_Response=requests.get(self.Url,headers=headers)
				if(API1_Response.status_code==200):#this line checks whether request is sucess or not and excute the block inside it 
					API1EndTime = time.time()- start# varibale to hold the end time
					#Log['API1']['Requeststatus']=API1_Response.status_code
					#Log['API1']['TimeTaken']=API1EndTime# it will gives us time taken to complete the request 
					self.API1TimeLog.append(API1EndTime)
					payload=json.dumps(ast.literal_eval(API1_Response.content))# it will get the respose data from request. by default response will be in string so we are converting to orginal type using ast package. and adding to payload varialbe which is payload for seconfd request
					start = time.time()
					API2_Response=requests.post(self.Url,data=payload)
					if(API2_Response.status_code==200):#this line checks whether request is sucess or not
						API2EndTime = time.time()- start# varibale to hold the end time
						#Log['API2']['Requeststatus']=API2_Response.status_code
						#Log['API2']['TimeTaken']=API2EndTime# it will gives us time taken to complete the request 
						if(API2_Response.content=="Success"):
							#print("Total Request completed:",self.ResponseCount )
							#self.TotalLog.append(Log)
							self.API2TimeLog.append(API2EndTime)
							self.ResponseCount +=1
							if (self.ResponseCount >=self.num_request):
								self.CalculateLoadStatiscs()		
					else:#this block will get executed when the status of request is other than 200
						print("request to API 2 Got Failed")
						print("Request to API 2 Status:"+ API2_Response.status_code)
				else:#this block will get executed when the status of request is other than 200
					print("Request to API 1 got failed")
					print("Request to API 1 Status:"+ API1_Response.status_code)
			else:
				print ("No url is passed to test")
		except Exception as e:
				traceback.print_exc()	
				
if __name__ == '__main__':
	try:
		ConfigureableArguments=sys.argv[1:]
		num_threads=10
		num_request=100
		if(len(ConfigureableArguments)>0):
			if(num_threads!='' & int(ConfigureableArguments[0])>10):
				num_threads=int(ConfigureableArguments[0])
				print num_threads
		else:
			print " you have not entered your desired no of workers to create .so we started with default value 10"
		pool = ThreadPool(num_threads)# This Creates The Thread Pool Object With num_threads as input and create the threads
		Requestobj=Requester("http://surya-interview.appspot.com/message","gps@surya-soft.com",num_request)
		for _ in range(num_request):
			pool.add_task(Requestobj.MakeRequest)
		pool.wait_completion()
	except Exception as e:
		print "Error in the Starting of Programm"
		traceback.print_exc()
