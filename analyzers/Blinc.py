"""
Reassembles the classifcation algorithm presented in "BLINC: Multilevel Traffic Classification in the Dark"
"""

class Host:
	def __init__(self, ip):
		self.ip = ip
		self.lastUpdated = 0

		self.srcPorts = {}
		self.dstPorts = {}
		self.dstIPs = {}
		self.proto = {}

	def update(self, flow):
		"""
		Updates the host statistics with the new incoming flow.
		"""
		# only consider flows that orignate from this host
		if flow.srcIP != self.ip:
			return
		
		self.dstIPs[flow.dstIP] = flow.firstSwitched
		
	def getActiveHosts(self, start, end):
		"""
		Calculates how many other hosts this host has sent data to.
		The function counts all occurences that lay between start and end
		(as in firstSwitched)
		"""
		counter = 0
		for (host, lastSeen) in self.dstIPs:
			if lastSeen > start and lastSeen < end:
				counter += 1
		return counter
			
			

class Graphlet:
	def __init__(self):
		pass

	def checkHost(self):
		pass

from BaseAnalyzer import BaseAnalyzer

class Analyzer(BaseAnalyzer):
	def __init__(self, config, reportIntervals, workingdir):
		BaseAnalyzer.__init__(self, config, reportIntervals, workingdir)

		self.hostmap = dict()
	
	
	def processFlow(self, flow):
		if not flow.srcIP in self.hostmap:
			self.hostmap[flow.srcIP] = Host(flow.srcIP)
		self.hostmap[flow.srcIP].update(flow)
		if not flow.dstIP in self.hostmap:
			self.hostmap[flow.dstIP] = Host(flow.dstIP)
		self.hostmap[flow.dstIP].update(flow)
		
	def generateReport(self, reportNumber, startTime, endTime):
		print reportNumber, " ", endTime
		
		

