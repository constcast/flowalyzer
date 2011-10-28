import MySQLdb
import sys

class DBBase:
	def __init__(self, dbname, host, user, password):
		self.dbname = dbname
		self.host = host 
		self.user = user
		self.password = password

	def connect(self):
		pass
	

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
