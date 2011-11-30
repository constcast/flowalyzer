import MySQLdb
import sys, calendar, string

from DBBase import DBBase
from operator import mod

class MySQLReader(DBBase):
	def __init__(self, dbname, host, user, password):
		DBBase.__init__(self, dbname, host, user, password)
		self.connection = None
		self.cursor = None
		self.connect()

	def getTableNames(self, startTime, endTime):
		tables = list()
		tmpTables = self.getTables()
	        for tab in tmpTables: 
			tabletime = calendar.timegm([string.atoi(tab[0][2:6]), string.atoi(tab[0][6:8]), string.atoi(tab[0][8:10]), string.atoi(tab[0][11:13]), string.atoi(tab[0][14])*30, 0, 0, 0, 0])
			# one table is 30 minutes == 30*60
			tableLength = 30*60
			alignedStart = startTime - mod(startTime, tableLength)
			alignedEnd = endTime + tableLength - mod(endTime + tableLength, tableLength)
			if tabletime >= alignedStart and tabletime < alignedEnd:
				tables.append(tab[0])
		return tables

	def connect(self):
		try:
			self.connection = MySQLdb.connect(self.host, self.user, self.password, self.dbname)
		except MySQLdb.OperationalError, message:
			print '%d: Error connecting to database: %s' % (message[0], message[1])
			sys.exit(-1)

		self.cursor = self.connection.cursor()

	def getTables(self):
		self.cursor.execute("SHOW TABLES LIKE 'h\\_%'")
		tables = self.cursor.fetchall()
		if tables == None:
			raise Exception("No flow tables in database")
		return tables

	def getDBInterval(self):
		firstTable = self.getTables()[0]
		self.cursor.execute("SELECT MIN(firstSwitched) from %s" % (firstTable))
		first =  int(self.cursor.fetchall()[0][0])
		lastTable = self.getTables()[-1]
		self.cursor.execute("SELECT MAX(firstSwitched) from %s" % (lastTable))
		last = int(self.cursor.fetchall()[0][0])
		return (first, last)

	def getNextFlows(self):
		tableNames = self.getTableNames(self.nextSlide, self.nextSlide + self.stepSize);
		flows = list()
		for i in tableNames:
			print "Executing statement ..."
			self.cursor.execute("SELECT * FROM %s WHERE firstSwitched >= %d and lastSwitched < %d ORDER BY firstSwitched" % (i, self.nextSlide, self.nextSlide + self.stepSize))
			print "Fetching next bunch of flows ..."
			flowsFromTable = self.cursor.fetchall()
			print "Joining flow tables ..."
			if flowsFromTable:
				flows.extend(list(flowsFromTable))
		self.nextSlide = self.nextSlide + self.stepSize
		return flows

	def getNextWindow(self, table, query):
		raise Excpetion("getFlows() not implemented ...")
	
