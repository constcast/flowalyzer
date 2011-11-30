
import sys, new, signal

running = True
mainmodule = None

def sig_int_handler(signum, frame):
	print "Received shutdown signal ..."
	running = False


def getMainModule(config):
	mainmodule = MainModule(config)
	return mainmodule
	

class MainModule:
	def __init__(self, config):
		self.config = config

	def run(self):
		if not "db_engine" in self.config:
			print "FATAL: You need to configure a DB backend in your config file!"
			sys.exit(-1)

		signal.signal(signal.SIGINT, sig_int_handler)

		print "Loading DB Connection ..."
		if self.config['db_engine'] == "mysql": 
			from database import MySQLReader
			dbreader = MySQLReader.MySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
		elif self.config['db_engine'] == "postgres":
			from database import PySQLReader
			dbreader = PySQLReader.PySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])	
		elif self.config['db_engine'] == "csv":
			from database import CSVReader
			dbreader = CSVReader.CSVReader(self.config['db_name'])
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
		dbreader.setStopTime(last)
		dbreader.setStepSize(1200)

		queue = dbreader.getQueue()
		dbreader.start()
		flows = []

		global running

		while running:
			try:
				flows = queue.get()
			except:
				running = False
				continue
			if len(flows) == 0:
				print "Finished processing flows ..."
				return
			analyzer.processFlows(flows)

		print "Terminating dbReader ... This may take a while ..."
		dbreader.terminate()
		print "Joining dbReader ..."
		dbreader.join()	

