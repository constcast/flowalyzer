class DBBase:
	def __init__(self, dbname, host, user, password):
		self.dbname = dbname
		self.host = host 
		self.user = user
		self.password = password

		self.stepSize = 300
		self.starttime = 0

	def connect(self):
		raise Exception("connect() not implemented ...")

	def getDBInterval(self):
		raise Exception("getInterval() not implemented ...")

	def setStepSize(self, stepsize):
		self.stepSize = stepsize

	def setStartTime(self, starttime):
		self.starttime = starttime

	def getNextWindow(self, table, query):
		raise Excpetion("getFlows() not implemented ...")

