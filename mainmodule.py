
import sys, new, signal, os

running = True
mainmodule = None
dbreaderpid = None

def sig_int_handler(signum, frame):
	print "Received shutdown signal ..."
	if dbreaderpid != None:
		print "Killing dbreader ..."
		os.kill(dbreaderpid, 9)
	global running
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

		# get starting time of the DB intervals
		(first, last) = dbreader.getDBInterval()
		dbreader.setStartTime(first)
		dbreader.setStopTime(last)

		#initialize analyzers

		if not "analyzers" in self.config:
			print "FATAL: You need to specify at least one analyzer for your flow data!"
			sys.exit(-1)
		print "Loading analyzers ..."
		sys.path.append("analyzers/")
		if not "analyzers" in self.config:
			raise Exception("Could not find analyzers section in config file!")


		if 'db_stepsize' in self.config:
			dbreader.setStepSize(int(self.config['db_stepsize']))
		else: 
			# use 5 minutes step size by default
			dbreader.setStepSize(300)

		for moduleName in self.config["analyzers"]:
			importName = __import__(moduleName)
			moduleConfigName = moduleName + "Config"
			if not moduleConfigName in self.config:
				print self.config
				raise Exception("Could not find section %s for module %s in configuration" % (moduleConfigName, moduleConfigName))

			# define default reporting intervals. We want the intervals
			# - 30 minutes
			# - 1 hour
			# - 1 day
			# - 1 week
			# - 1 month
			# - 1 year
			# - cont
			import BaseAnalyzer
			reportingIntervals = []
			for i in [ 1800, 3600, 86400, 604800, 2419200, 29030400 ]:
				interval = BaseAnalyzer.ReportingInterval(i, first)
				reportingIntervals.append(interval)

			# create the analyzer
			if 'workdir' in self.config:
				analyzer = importName.Analyzer(self.config[moduleConfigName], reportingIntervals, self.config['workdir'])
			else:
				analyzer = importName.Analyzer(self.config[moduleConfigName], reportingIntervals, 'workingdir/')
		

		print "Processing flows ..."

		# fork out processes and process flows 
		queue = dbreader.getQueue()
		dbreader.start()
		dbreaderpid = dbreader.pid
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
				break
			try:
				print "Processing more flows ..."
				analyzer.processFlows(flows)
			except Exception as inst:
				# ignore errors 
				# TODO: FIX this with some proper error handling
				print "ERROR: There has been an analysis exception: %s" % (inst)
				import traceback
				traceback.print_exc(file=sys.stdout)
				running = False

		print "Terminating dbReader ... This may take a while ..."
		dbreader.terminate()
		print "Joining dbReader ..."
		wait_for_processes = True
		while wait_for_processes:
			try:
				# try until we succeeded
				dbreader.join()	
				wait_for_processes = False
			except OSError:
				pass
