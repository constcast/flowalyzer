"""
This module takes a CSV file as input, which contains the network description of the monitoried
network (optionally). It then extracts the subnets from this file and matches incoming flows
against these subnets (performing subnet aggregation on the incoming flows. Unknown-subnets are
assumed to belong to /24 subnets. 
SubnetGrapher will periodically plot the communicating subnets and the flows between them to 
graphviz dot files."""

from BaseAnalyzer import BaseAnalyzer
import csv, socket, re
import SubnetTree

class Analyzer(BaseAnalyzer):
	def __init__(self, config):
		self.config = config
		if 'subnetCSV' in self.config:
			self.parseSubnetCSV(self.config['subnetCSV'])
		self.subnets = SubnetTree.SubnetTree()

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
				self.subnets[self.documentedSubnets[ip]] = 1
			else:
				# generate a new /24 subnet and add it to the known 
				# list of subnets. null the last byte of the ip
				m = re.match("(.*)\..*$", ip)
				if not m:
					raise Exception("Tried to match ip against IP regex and failed. This is not an IPv4 address: %s" % (ip))
				
				net = m.group(1) + ".0/24"
				self.subnets[net] = 1

		net = self.subnets[ip]
		return net
		
	
	def processFlows(self, flows):
		for flow in flows:
			srcIP = self.int2ip(flow[0])
			dstIP = self.int2ip(flow[1])
			self.getSubnet(srcIP)
			
				

