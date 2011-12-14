from database import DBBase

import os

class ReportingInterval:
	def __init__(self, intervalTime, startTime):
		self.intervalLength = intervalTime
		self.lastReport = startTime

	def nextReportTime(self):
		return self.lastReport + self.intervalLength

	def updateNextReportTime(self):
		self.lastReport = self.lastReport + self.intervalLength
		
class BaseAnalyzer:
	def __init__(self, config, reportingIntervals, workdir):
		self.config = config
		self.reportingIntervals = reportingIntervals

		# append module name for specific analysis
		self.workdir = workdir + '/' + self.__module__ + '/'
		# create directory if they don't exist
		if not os.access(self.workdir, os.R_OK | os.W_OK):
			os.makedirs(self.workdir)

	def processFlows(self, flows):
		# check the flow time stamps in order to find the timestamp where we have
		# to generate reports (if this applies to this bunch of flows)
		reportTimes = list()
		# get last time
		lastTime = flows[-1][8]
		for interval in self.reportingIntervals:
			reportTime = interval.lastReport + interval.intervalLength
			if reportTime < lastTime:
				reportTimes.append(reportTime)
		# remove duplicate entries 
		reportset = set(reportTimes)
		reportTimes = list(reportset)
		reportTimes.sort()
		print reportTimes

		if len(reportTimes) > 0:
			nextReport = reportTimes.pop()
		else:
			nextReport = None

		for flow in flows:
			self.processFlow(flow)
			if nextReport != None and nextReport >= flow[8]:
				# ok, we need to generate at least one report
				# check each report on whether we need to generate it
				for i in range(len(self.reportingIntervals)):
					if nextReport == self.reportingIntervals[i].nextReportTime():
						self.generateReport(i, nextReport)
						self.reportingIntervals[i].updateNextReportTime()

				if len(reportTimes) > 0:
					nextReport = reportTimes.pop()
				else:
					nextReport = None


	def processFlow(self, flow):
		pass

	def generateReport(self, reportNumber, reportTime):
		pass

