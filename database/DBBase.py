import multiprocessing

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
			flows = self.getNextFlows()
			if len(flows) == 0:
				# out of data, singal this by entering empty flows into queue
				self.queue.put(flows)
				return
			try:
				self.queue.put(flows)
			except:
				return

