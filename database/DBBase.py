class DBBase:
	def __init__(self, dbname, host, user, password):
		self.dbname = dbname
		self.host = host 
		self.user = user
		self.password = password

	def connect(self):
		raise Exception("connect() not implemented ...")

	def createSpan(self, startTime = None, endTime = None, tableName = None):
		raise Exception("createCompleteSpan() not implemented ...")
	
	

class TableSpanBase:
	def __init__(self, startTime, endTime, tableName):
		self.startTime = startTime
		self.endTime = endTime
		self.tableName = tableName

	def getTableNames(self):
		raise Exception("getTableNames() not implemented ...")

	def getAllTables(self):
		raise Exception("getTables() not implemented ...")
	
	def getFirstTimestamp(self):
		raise Exception("getFirstTimestamp() not implemented ...")
	
	def getLastTimestamp(self):
		raise Exception("getLastTimestamp() not implemented ...")

	def getFlows(self, table, query):
		raise Excpetion("getFlows() not implemented ...")

