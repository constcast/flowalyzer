"""
This module takes a CSV file as input, which contains the network description of the monitoried
network (optionally). It then extracts the subnets from this file and matches incoming flows
against these subnets (performing subnet aggregation on the incoming flows. Unknown-subnets are
assumed to belong to /24 subnets. 
SubnetGrapher will periodically plot the communicating subnets and the flows between them to 
graphviz dot files."""

from BaseAnalyzer import BaseAnalyzer
import csv, socket, re, os
import SubnetTree

class SubnetStats:
	def __init__(self):
		self.inBytes = 0
		self.inPkts  = 0
		self.outBytes = 0 
		self.outPkts  = 0

	def addInTraffic(self, bytes, packets):
		self.inBytes += bytes
		self.inPkts  += packets
	
	def addOutTraffic(self, bytes, packets):
		self.outBytes += bytes
		self.outPkts  += packets


class ReportInstance:
	def __init__(self, startTime):
		self.startTime = startTime
		self.subnets = dict()

	def updateSubnet(self, substring, inBytes, inPkts, outBytes, outPkts):
		if not substring in self.subnets:
			self.subnets[substring] = SubnetStats()

		self.subnets[substring].addInTraffic(inBytes, inPkts)
		self.subnets[substring].addOutTraffic(outBytes, outPkts)
		
	def generateReport(self, fd, endtime):
		fd.write("Start Time:\t %d\nEnd Time:\t %d\n\n" % (self.startTime, endtime))
		fd.write("Subnet\t\tBytesIn PktsIn BytesOut PktsOut\n")
		for i in self.subnets:
			fd.write("%s\t\t" % (i))
			subnet = self.subnets[i]
			fd.write("%d %d %d %d\n" % (subnet.inBytes, subnet.inPkts, subnet.outBytes, subnet.outPkts))
		self.startTime = endtime
		

class Analyzer(BaseAnalyzer):
	def __init__(self, config, reportIntervals, workingdir):
		BaseAnalyzer.__init__(self, config, reportIntervals, workingdir)
		if 'subnetCSV' in self.config:
			self.parseSubnetCSV(self.config['subnetCSV'])
		self.subnets = SubnetTree.SubnetTree()
	
		self.reports = []
		for i in reportIntervals:
			# create a number of reportinstances
			self.reports.append(ReportInstance(0))

	def int2ip(self, i):
		# convert an intege to dottet format
		return str(i//2**24)+"."+str((i//2**16)%256)+"."+str((i//2**8)%256)+"."+str(i%256)

	def parseSubnetCSV(self, filename):
		self.subnetcsv = csv.reader(open(filename, 'r'))
		self.documentedSubnets = SubnetTree.SubnetTree()
		first = True
		for i in self.subnetcsv:
			# TODO REMOVE: hack. skip first line
			if first:
				first = False
				continue

			# this is a completely strange format which has grown
			# over time. We expect
			# i[0] = first byte ip address
			# i[1] = second byte ip address
			# i[2] = third byte ip address
			# i[3] = fourth byte ip address
			# i[6] = network mask (encoded as binary string of 8 bit)
			# i[10] = ip address byte at which mask needs to be applied (starting with 1)

			ip = i[0] + "." + i[1] + "." + i[2] + "." + i[3]

			# calculate network mask magic: 
			# 8-bit network mask in i[6] should be applied to byte i[10]
			# which means that all bits in the bytes before i[10] are set to 
			# 1 (hence the number of set bits is i[10] - 1
			# Afterwards, we have to add the number of 1s in the 8-bit mask
			# in order to derive the CIDR mask
			mask = (int(i[10]) - 1) * 8 + i[6].count('1')
			subnet = ip + "/" + str(mask)

			# TODO store more information about the network
			self.documentedSubnets[subnet] = subnet
	
	def getSubnet(self, ip):
		"""Get the subnet that is associated to IP address "ip" from the 
		   subnet documentation. If the IP address is not documented, assume
		   the associated subnet is a /24 subnet and generate a "new" subnet
		"""
		if not ip in self.subnets:
			if ip in self.documentedSubnets:
				# get subnet from documented list
				self.subnets[self.documentedSubnets[ip]] = self.documentedSubnets[ip]
			else:
				# generate a new /24 subnet and add it to the known 
				# list of subnets. null the last byte of the ip
				m = re.match("(.*)\..*$", ip)
				if not m:
					raise Exception("Tried to match ip against IP regex and failed. This is not an IPv4 address: %s" % (ip))
				
				net = m.group(1) + ".0/24"
				self.subnets[net] = net

		net = self.subnets[ip]
		return net
		
	
	def processFlow(self, flow):
		srcIP = self.int2ip(flow[0])
		dstIP = self.int2ip(flow[1])
		srcSubnet = self.getSubnet(srcIP)
		dstSubnet = self.getSubnet(dstIP)
		for i in self.reports:
			i.updateSubnet(dstSubnet, flow[6], flow[7], 0, 0)
			i.updateSubnet(srcSubnet, 0, 0, flow[6], flow[7])
		
	def generateReport(self, reportNumber, startTime, endTime):
		print "Generating Report", reportNumber, endTime
		reportFile = os.path.join(self.workdir, str(reportNumber) + "_" + str(endTime))
		try:
			fd = open(reportFile, 'w')
			self.reports[reportNumber].generateReport(fd, endTime)
			fd.close()
		except Exception as inst:
			print "Error writing report %s: %s" % (reportFile, inst)
				
		
		

