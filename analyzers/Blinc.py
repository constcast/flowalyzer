"""
Reassembles the classifcation algorithm presented in "BLINC: Multilevel Traffic Classification in the Dark"
"""

class Host:
	def __init__(self):
		pass

	def update(self, flow):
		pass

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
		pass
		
	def generateReport(self, reportNumber, reportTime):
		pass
		
		

