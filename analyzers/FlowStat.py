from  BaseAnalyzer import BaseAnalyzer

import os

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
		self.rrdDBName = rrdDir + "db-%s-%d.rrd"

		if not os.access(self.rrdDir, os.R_OK | os.W_OK):
			os.mkdir(self.rrdDir)

	def checkRRD(self, currTime):
		for i in range(0, len(self.intervals)):
			rrdName = self.rrdDBName % (self.reportname, i)
			if not os.access(rrdName, os.R_OK | os.W_OK):
				os.system("rrdtool create %s --start %d --step=%d DS:input:ABSOLUTE:%d:U:U RRA:AVERAGE:0.5:%d:10000 RRA:MIN:0.5:%d:10000 RRA:MAX:0.5:%d:10000" % (rrdName, currTime, self.stepSize, self.intervals[i] * 10, self.intervals[i], self.intervals[i], self.intervals[i]))
			if (currTime > (self.intervalStart[i] + self.intervals[i] * self.stepSize)):
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
		self.checkRRD(flow_record[8])

	def createImages(self, imgDir, endTime):
		pngImg = imgDir + '/%s-%d.png'
		for i in range(0, len(self.intervals)):
			rrdName = self.rrdDBName % (self.reportname, i)
			command = "rrdtool graph %s --width=800 --height=600 --end %d --start %d-%dm DEF:ds0b=%s:input:MAX LINE1:ds0b#9999FF:\"min/max\" DEF:ds0c=%s:input:MIN LINE1:ds0c#9999FF DEF:ds0a=%s:input:AVERAGE LINE2:ds0a#0000FF:\"average\"" % (pngImg % (self.reportname, self.intervals[i]), endTime, endTime, self.graphHistory[i], rrdName, rrdName, rrdName)
			os.system(command)
			#print command

class Analyzer(BaseAnalyzer):
	def __init__(self, config):
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
		#self.packetReport = RRDGenerator("Packets", self.rrdDir, rrdintervals, rrdgraphhist, 7)
		#self.bytesReport  = RRDGenerator("Bytes"  , self.rrdDir, rrdintervals, rrdgraphhist, 6)
	
	def processFlows(self, flows):
		for flow in flows:
			for report in self.reports:
				report.update(flow)
		if len(flows) > 1:
			for report in self.reports:
				report.createImages(self.imgDir, flows[-1][8])
