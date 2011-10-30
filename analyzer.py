import utils
from database import MySQLReader

import sys

class MainModule:
	def __init__(self, config):
		self.config = config

	def run(self):
		if 'baTestMode' in self.config:
			# we are now running the testing stuff we did for the BA
			print "Running in BA test mode!"
			utils.BA_TEMP_STUFF(self.config)
			print "Finished BA mode. Exiting program!"
			return

		dbreader = MySQLReader.MySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
