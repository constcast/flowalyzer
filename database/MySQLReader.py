import MySQLdb
import sys

from DBBase import DBBase, TableSpanBase

class MySQLReader(DBBase):
	def __init__(self, dbname, host, user, password):
		DBBase.__init__(self, dbname, host, user, password)
		self.connection = None
		self.cursor = None
		self.connect()

	def connect(self):
		try:
			self.connection = MySQLdb.connect(self.host, self.user, self.password, self.dbname)
		except MySQLdb.OperationalError, message:
			print '%d: Error connecting to database: %s' % (message[0], message[1])
			sys.exit(-1)

		self.cursor = self.connection.cursor()

		
class MySQLTableSpan(TableSpanBase):
	def __init__(self, startTime, endTime, cursor):
		TableSpanBase.__init__(self, startTime, endTime)

		self.cursor = cursor
		self.tables = []

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
		self.cursor.execute("SHOW TABLES LIKE 'h\\_%'")
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
