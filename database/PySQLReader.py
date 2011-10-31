import sys

import pgdb

from DBBase import DBBase, TableSpanBase

class PySQLReader(DBBase):
	def __init__(self, dbname, host, user, password):
		DBBase.__init__(self, dbname, host, user, password)
		self.connection = None
		self.cursor = None
		self.connect()

	def connect(self):
		try:
			self.connection = pgdb.connect(database=self.dbname, host=self.host, user=self.user, password=self.password)
		except pgdb.OperationalError, message:
			print '%d: Error connecting to database: %s' % (message[0], message[1])
			sys.exit(-1)

		self.cursor = self.connection.cursor()

	def createSpan(self, startTime = None, endTime = None, tableName = None):
		span = PySQLTableSpan(startTime=startTime, endTime=endTime, tableName=tableName, cursor=self.cursor)
		return span

		
class PySQLTableSpan(TableSpanBase):
	def __init__(self, startTime = None, endTime = None, tableName = None, cursor = None):
		TableSpanBase.__init__(self, startTime, endTime, tableName)

		self.cursor = cursor
		self.tables = []

		return

		tmpTables = self.getTables()
	        for i in tmpTables: 
			tabletime = calendar.timegm([string.atoi(row[0][2:6]), string.atoi(row[0][6:8]), string.atoi(row[0][8:10]), string.atoi(row[0][11:13]), string.atoi(row[0][14])*30, 0, 0, 0, 0])
			# one table is 30 minutes == 30*60
			tableLength = 30*60
			alignedStart = startTime - mod(startTime, tableLength)
			alignedEnd = endTime + tableLength - mod(endTime + tableLength, tableLength)
			if tabletime >= alignedStart and tabletime < alignedEnd:
				tables.append(row[0])

		if len(tables) == 0:
			raise Exception("No table found!")

	def getAllTables(self):
		self.cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' and tablename like 'f_%'")
		return self.cursor.fetchall()
	
	def getFirstTimestamp(self):
		firstTable = self.getTables()[0]
		return self.getFirstFromTable(firstTable)
	
	def getLastTimestamp(self):
		lastTable = self.getTables()[-1]
		return self.getLastFromTable(lastTable)

	def getTableNames(self):
		return self.tables

	def getFlows(self, query):
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def getFirstFromTable(self, table):
		self.cursor.execute("select extract('epoch' from firstSwitched) AS UnixTime from %s LIMIT 1" % (table))
		#self.cursor.execute("select firstSwitched from %s LIMIT 1" % (table))
		return self.cursor.fetchall()[0][0]

	def getLastFromTable(self, table):
		#self.cursor.execute("select extract('epoch' from firstSwitched) AS UnixTime from %s" % (table))
		return int(self.cursor.fetchall()[-1][0])

	def getFlows(self, query, table, first, last):
		self.cursor.execute(query % (table, first, last))
		return self.cursor.fetchall()
