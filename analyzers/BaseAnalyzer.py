from database import DBBase

class BaseAnalyzer:
	def __init__(self, span):
		self.tableSpan = span
	
	def go(self):
		for i in self.tableSpan.getTableNames():
			self.processFlows(self.span.getFlows(i, self.getQuery()))

	def processFlows(self, flows):
		pass

	def getQuery(self):
		pass
