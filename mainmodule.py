
import sys, new

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

		print "Loading DB Connection ..."
		if self.config['db_engine'] == "mysql": 
			from database import MySQLReader
			dbreader = MySQLReader.MySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
		elif self.config['db_engine'] == "postgres":
			from database import PySQLReader
			dbreader = PySQLReader.PySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
			
		else:
			print "FATAL: Unknown DB backend configured: %s" % (self.config['db_engine'])
			sys.exit(-1)

		if not "analyzers" in self.config:
			print "FATAL: You need to specify at least one analyzer for your flow data!"
			sys.exit(-1)
		print "Loading analyzers ..."
		sys.path.append("analyzers/")
		if not "analyzers" in self.config:
			raise Exception("Could not find analyzers section in config file!")
		for moduleName in self.config["analyzers"]:
			importName = __import__(moduleName)
			moduleConfigName = moduleName + "Config"
			if not moduleConfigName in self.config:
				print self.config
				raise Exception("Could not find section %s for module %s in configuration" % (moduleConfigName, moduleConfigName))
			analyzer = importName.Analyzer(self.config[moduleConfigName])
		

		print "Processing flows ..."

		(first, last) = dbreader.getDBInterval()
		dbreader.setStartTime(first)
		dbreader.setStepSize(1000)
		flows = dbreader.getNextFlows()
		while dbreader.getCurrentStartTime() < last:
			analyzer.processFlows(flows)
			flows = dbreader.getNextFlows();

