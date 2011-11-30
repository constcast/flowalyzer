from DBBase import DBBase
import csv

class CSVReader(DBBase):
	def __init__(self, dbname):
		DBBase.__init__(self, dbname, '', '', '')
		self.connect()
		self.lastFlow = None

	def connect(self):
		self.csvreader = csv.reader(open(self.dbname, 'r'))


	def getDBInterval(self):
		self.lastFlow = [ int(x) for x in self.csvreader.next()]

		# we don't know about the last flow. Hence we will read the complete
		# file by returning 0 as end time
		return (self.lastFlow[8], 0)
	
	def getNextFlows(self):
		print "Reading next slice of flows ..."
		flows = []
		# take last flow if we have one
		if self.lastFlow != None:
			flows.append(self.lastFlow)
		go = True
		finishTime = self.nextSlide + self.stepSize
		# read lines until end of file or util we have read the complete slice
		while go:
			try:
				flow =  [ int(x) for x in self.csvreader.next()]
			except:
				self.lastFlow = None
				go = False
				continue
			if flow[8] >= finishTime:
				self.lastFlow = flow
				go = False
			else:
				flows.append(flow)
		self.nextSlide = self.nextSlide + self.stepSize
		return flows
			
