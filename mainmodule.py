
import sys

class MainModule:
	def __init__(self, config):
		self.config = config

	def run(self):
		if 'baTestMode' in self.config:
			# we are now running the testing stuff we did for the BA
			import utils
			print "Running in BA test mode!"
			utils.BA_TEMP_STUFF(self.config)
			print "Finished BA mode. Exiting program!"
			return

		if not "db_engine" in self.config:
			print "FATAL: You need to configure a DB backend in your config file!"
			sys.exit(-1)

		if self.config['db_engine'] == "mysql": 
			from database import MySQLReader
			dbreader = MySQLReader.MySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
		elif self.config['db_engine'] == "postgres":
			from database import PySQLReader
			dbreader = PySQLReader.PySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
			
		else:
			print "FATAL: Unknown DB backend configured: %s" % (self.config['db_engine'])
			sys.exit(-1)
