import multiprocessing
import time
import collections

#Flow = collections.namedtuple('Flow', 'dstIP, srcIP, srcPort, dstPort, proto, dstTos, bytes, pkts, firstSwitched, lastSwitched, firstSwitchedMillis, lastSwitchedMillis, exporterID')
Flow = collections.namedtuple('Flow', 'dstIP, srcIP, srcPort, dstPort, proto, bytes, pkts, firstSwitched, lastSwitched, exporterID')

class DBBase(multiprocessing.Process):
	def __init__(self, dbname, host, user, password):
		self.dbname = dbname
		self.host = host 
		self.user = user
		self.password = password

		self.stepSize = 300
		self.starttime = 0
		self.stoptime = 0
		self.nextSlide = 0

		self.queue = multiprocessing.Queue()
		multiprocessing.Process.__init__(self)

	def connect(self):
		raise Exception("connect() not implemented ...")

	def getDBInterval(self):
		raise Exception("getInterval() not implemented ...")

	def getTableNames(self, first, last):
		raise Exception("getTableSpace() not implemented ...")

	def setStepSize(self, stepsize):
		self.stepSize = stepsize

	def setStartTime(self, starttime):
		self.starttime = starttime
		self.nextSlide = starttime

	def setStopTime(self, stoptime):
		self.stoptime = stoptime

	def getCurrentStartTime(self):
		return self.starttime

	def getNextFlows(self):
		raise Exception("getNextFlows() not implemented ...")

	def getNextWindow(self, table, query):
		raise Excpetion("getNextWindow() not implemented ...")

	def getQueue(self):
		return self.queue

	def run(self):
		while True:
			try: 
				flows = []
				for flow in map(Flow._make,  self.getNextFlows()):
					flows.append(flow)
			except Exception as inst:
				print "Finished processing flows: %s" % (inst)
				self.queue.put([])
				return
			
			if len(flows) > 0:
				try: 
					# some platforms such as Mac OS X do not
					# implement multiprocessing.Queue.qsize()
					# we will therefore only wait if we are on
					# a platform which supports this
					while self.queue.qsize() > 100000:
						print "Analyzers are running to slow. Queue is filling up. I'll just give them some time to process the queue content..."
						time.sleep(2)
				except:
					print "Cannot determine queue size. I'll therefore continue to fill the queue ..."
				self.queue.put(flows)


	def executeQuery(self, query, table):
		raise Exception("executeQuery() not implemented ...")

	def runQuery(self, query, first, last):
		tables = self.getTableNames(first, last)
		result = []
		for t in tables:
			for flow in map(Flow._make, self.executeQuery(query, t)):
				result.append(flow)
		return result
		
		
