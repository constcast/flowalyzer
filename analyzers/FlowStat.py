from  BaseAnalyzer import BaseAnalyzer

import os, datetime

class RRDGenerator:
	def __init__(self, reportname, rrdDir, rrdIntervals, rrdGraphHist, statField):
		print "Initializing report \"%s\"..." % (reportname)
		self.reportname = reportname
		self.rrdDir = rrdDir
		self.intervals = rrdIntervals
		self.intervalStart = list(rrdIntervals)
		self.counter = list(rrdIntervals)
		self.stepSize = 5
		for i in range(0, len(rrdIntervals)):
			self.intervalStart[i] = 0
			self.counter[i] = 0
		self.graphHistory = rrdGraphHist
		self.filter = None
		self.statField = statField
		self.rrdDBName = rrdDir + "db-%s-%s.rrd"
		self.imgNames = [ "Short", "Mid", "Long" ]


		# try to create rrd directory
		if not os.access(self.rrdDir, os.R_OK | os.W_OK):
			os.mkdir(self.rrdDir)

		# we cannot create the rrd databases right know. We have to know
		# the start time in order to do so. Since it is not known a priory
		# we have to create it when the first flows arrive. Store whether
		# we already created the rrds in order to avoid file system checks
		self.rrdsCreated = False

		# lastupdate 
		self.lastupdate = 0

	def createRRD(self, currTime):
		for i in range(0, len(self.intervals)):
			rrdName = self.rrdDBName % (self.reportname, self.imgNames[i])
			if  os.access(rrdName, os.R_OK | os.W_OK):
				os.remove(rrdName)
			os.system("rrdtool create %s --start %d --step=%d DS:input:ABSOLUTE:%d:U:U RRA:AVERAGE:0.5:%d:10000 RRA:MIN:0.5:%d:10000 RRA:MAX:0.5:%d:10000" % (rrdName, currTime, self.stepSize, self.intervals[i] * 10, self.intervals[i], self.intervals[i], self.intervals[i]))
		self.rrdsCreated = True

	def checkRRD(self, currTime):
		if not self.rrdsCreated:
			self.createRRD(currTime)

		for i in range(0, len(self.intervals)):
			if (currTime > (self.intervalStart[i] + self.intervals[i] * self.stepSize)):
				rrdName = self.rrdDBName % (self.reportname, self.imgNames[i])
				print "Updating: ", currTime
				command = "rrdtool update %s %d:%d" % (rrdName, currTime, self.counter[i])
				#print command
				os.system(command)
				self.counter[i] = 0
				self.intervalStart[i] = currTime

	def update(self, flow_record):
		for i in range(0, len(self.intervals)):
			self.counter[i] += flow_record[self.statField]
			# this is probably the first record that we see so far
			if (self.intervalStart[i] == 0):
				self.intervalStart[i] = flow_record[8]
		
		# check every second if we need to update the rrds
		# TODO: this can be optimized ...
		if self.lastupdate < flow_record[8]:
			self.checkRRD(flow_record[8])
			self.lastupdate = flow_record[8]

	def createImages(self, imgDir, endTime):
		pngImg = imgDir + '/%s-%s.png'
		for i in range(0, len(self.intervals)):
			rrdName = self.rrdDBName % (self.reportname, self.imgNames[i])
			command = "rrdtool graph %s --width=800 --height=600 --end %d --start %d-%dm DEF:ds0b=%s:input:MAX LINE1:ds0b#9999FF:\"min/max\" DEF:ds0c=%s:input:MIN LINE1:ds0c#9999FF DEF:ds0a=%s:input:AVERAGE LINE2:ds0a#0000FF:\"average\"" % (pngImg % (self.reportname, self.imgNames[i]), endTime, endTime, self.graphHistory[i], rrdName, rrdName, rrdName)
			os.system(command)
			#print command

class Analyzer(BaseAnalyzer):
	def __init__(self, config, reportingInterval):
		BaseAnalyzer.__init__(self, config, reportingInterval)

		print "Initializing FlowStat module ..."
		if len(config) == 0 or not isinstance(config[0], dict):
			raise Exception("Configuration error cannot configure FlowStat!")
	
		self.configDict = config.pop(0)

		if not 'imgDir' in self.configDict:
			raise Exception("FlowStat: imgDir not configured!")
		self.imgDir = self.configDict['imgDir']

		if not 'rrdDir' in self.configDict:
			raise Exception("FlowStat: rrdDir not configured!")
		self.rrdDir = self.configDict['rrdDir']

		if not os.access(self.imgDir, os.R_OK | os.W_OK):
			os.mkdir(self.imgDir)

		rrdintervals = (60, 180, 720)
		rrdgraphhist = (120, 1440, 43200)

		# generate report objects from config file
		self.reports = []
		for reportConfig in config:
			if not 'reportName' in reportConfig:
				raise Exception("FlowStat: Found report configuration without \'reportName\' field: %s" % (reportConfig))
			if not 'idx' in reportConfig:
				raise Exception("FlowStat: Found report configuration without \'idx\' field: %s" % (reportConfig))
			if not 'filter' in reportConfig:
				raise Exception("FlowStat: Found report configuration without \'filter\' field: %s" % (reportConfig))
			self.reports.append(RRDGenerator(reportConfig['reportName'], self.rrdDir, rrdintervals, rrdgraphhist, reportConfig['idx']))
	
	def processFlow(self, flow):
		#print "Updating flow stats for " + str(len(flows)) + " flows ... " + str(datetime.datetime.now())
		for report in self.reports:
			report.update(flow)

	def generateReport(self, reportNumber, reportTime):
		print "Generating images ..." + str(datetime.datetime.now())
		report[reportNumber].createImages(self.imgDir, reportTime)
		#report[reportNumber].createImages(self.imgDir, flows[-1][8])
