from BaseAnalyzer import BaseAnalyzer

class Analyzer(BaseAnalyzer):
	def __init__(self, config, reportingInterval, workingdir):
		BaseAnalyzer.__init__(self, config, reportingInterval, workingdir)

	def processFlow(self, flow):
		print flow
