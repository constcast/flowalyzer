from BaseAnalyzer import BaseAnalyzer

class TopActiveHosts(BaseAnalyzer):
	def __init__(self, tableSpan):
		BaseAnalyzer.__init__(self, tableSpan)
		self.hostMap = dict()
	
	def processFlows(self, flows):
		print flows

	def getQuery(self, table):
		return "SELECT * FROM %s"
