from BaseAnalyzer import BaseAnalyzer
import csv, socket, re, os
import SubnetTree

class Analyzer(BaseAnalyzer):
	def __init__(self, config, reportIntervals, workingdir):
		BaseAnalyzer.__init__(self, config, reportIntervals, workingdir)
		subnetFile = self.config['subnets']
		self.subnets = 	SubnetTree.SubnetTree()
		for line in open(subnetFile):
			line = line.rstrip('\n')
			self.subnets[line] = line

		self.outputFile = open(self.config['outputFile'], 'w+')
		self.outputFile.write('# startTime endTime subnet in/out(0 == going into the subnet / 1 == coming from the subnet)\n')

	def int2ip(self, i):
		# convert an intege to dottet format
		return str(i//2**24)+"."+str((i//2**16)%256)+"."+str((i//2**8)%256)+"."+str(i%256)


	def processFlow(self, flow):
		src = self.int2ip(flow.srcIP)
		dst = self.int2ip(flow.dstIP)
		if src in self.subnets:
			self.outputFile.write("%u %u %s 0\n" % (flow.firstSwitched, flow.lastSwitched, self.subnets[src]))
			print "%u %u %s 0" % (flow.firstSwitched, flow.lastSwitched, self.subnets[src])
			
		if dst in self.subnets:
			self.outputFile.write("%u %u %s 1\n" % (flow.firstSwitched, flow.lastSwitched, self.subnets[dst]))
			print "%u %u %s 1" % (flow.firstSwitched, flow.lastSwitched, self.subnets[dst])
	
