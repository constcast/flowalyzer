import MySQLdb
import sys

from DBBase import DBBase, TableSpanBase

class MySQLReader(DBBase):
	def __init__(self, dbname, host, user, password):
		DBBase.__init__(self, dbname, host, user, password)
		self.connection = None
		self.cursor = None
		self.connect()

	def getTableNames(self, startTime, endTime):
		tables = list()
		tmpTables = self.getTables()
	        for i in tmpTables: 
			tabletime = calendar.timegm([string.atoi(row[0][2:6]), string.atoi(row[0][6:8]), string.atoi(row[0][8:10]), string.atoi(row[0][11:13]), string.atoi(row[0][14])*30, 0, 0, 0, 0])
			# one table is 30 minutes == 30*60
			tableLength = 30*60
			alignedStart = startTime - mod(startTime, tableLength)
			alignedEnd = endTime + tableLength - mod(endTime + tableLength, tableLength)
			if tabletime >= alignedStart and tabletime < alignedEnd:
				tables.append(row[0])

	def connect(self):
		try:
			self.connection = MySQLdb.connect(self.host, self.user, self.password, self.dbname)
		except MySQLdb.OperationalError, message:
			print '%d: Error connecting to database: %s' % (message[0], message[1])
			sys.exit(-1)

		self.cursor = self.connection.cursor()

	def getTables(self):
		self.cursor.execute("SHOW TABLES LIKE 'h\\_%'")
		self.allTables = self.fetchall()

	def getDBInterval(self):
		firstTable = self.getTables()[0]
		self.cursor.execute("SELECT firstSwitched from %s LIMIT 1" % (firstTable))
		first =  int(c.fetchall()[0][0])
		lastTable = self.getTables()[-1]
		self.cursor.execute("SELECT MAX(firstSwitched) from %s" % (lastTable))
		last = int(c.fetchall()[0][0])
		return (first, last)

	def getNextFlows(self):
		tableNames = getTableNames(self.nextSlide, self.nextSlide + self.stepSize);
		flows = list()
		for i in tableNames:
			self.cursor.execute("SELECT * FROM %s WHERE firstSwitched >= %d and lastSwitched < %d" % (i, self.nextSlide, self.nextSlide + self.stepSize))
			print self.fetchAll()
		self.nextSlide = self.nextSlide + self.stepSize
		return flows

	def getNextWindow(self, table, query):
		raise Excpetion("getFlows() not implemented ...")
	
class MySQLTableSpan(TableSpanBase):
	def __init__(self, startTime, endTime, cursor):
		TableSpanBase.__init__(self, startTime, endTime)

		self.cursor = cursor
		self.tables = []

		if len(tables) == 0:
			raise Exception("No table found!")

	def getAllTables(self):
		return self.cursor.fetchall()
	
	def getFirstTimestamp(self):
		firstTable = self.getTables()[0]
		self.cursor.execute("SELECT firstSwitched from %s LIMIT 1" % (firstTable))
		return int(c.fetchall()[0][0])
	
	def getLastTimestamp(self):
		lastTable = self.getTables()[-1]
		self.cursor.execute("SELECT lastSwitched from %s" % (lastTable))
		return int(c.fetchall()[-1][0])

	def getTableNames(self):
		return self.tables

	def getFlows(self, table, query):
		self.cursor.execute(query)
		return self.cursor.fetchall()
