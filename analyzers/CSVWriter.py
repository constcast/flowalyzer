"""
This is a simple test module that writes incoming flows to CSV files.
These can be read by database/CSVReader in testing environments where you
do not want to have databases installed (e.g. on your development laptop)
"""

from BaseAnalyzer import BaseAnalyzer
import csv

class Analyzer(BaseAnalyzer):
	def __init__(self, config):
		print "Initializing CSVWriter module ..."
		if not 'outputfile' in config:
			raise Exception("CSVWriter: No 'outputfile' configured for CSVWriter.")
		self.outputfile = config['outputfile']
		self.fd = open(self.outputfile, 'wb')
		self.csv_writer = csv.writer(self.fd)

	def processFlows(self, flows):
		print "Writing flows to CSV ..."
		self.csv_writer.writerows(flows)
			
