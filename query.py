#!/usr/bin/env python

from optparse import OptionParser

from mainmodule import getMainModule

import sys

def int2ip(i):
	# convert an intege to dottet format
	return str(i//2**24)+"."+str((i//2**16)%256)+"."+str((i//2**8)%256)+"."+str(i%256)

def printflow(flow):
	srcIP = int2ip(flow.srcIP)
	dstIP = int2ip(flow.dstIP)
	
	print srcIP, 
	if len(srcIP) >= 15:
		print "\t",
	else:
		print "\t\t",
	print dstIP, 
	if len(dstIP) >= 15:
		print "\t",
	else:
		print "\t\t",
	print  flow.srcPort, "\t", flow.dstPort, "\t", flow.proto, "\t", flow.bytes, "\t", flow.pkts, "\t", flow.firstSwitched, "\t", flow.lastSwitched

if __name__ == "__main__":
	parser = OptionParser("usage: %prog --start <second> --end <second> [query]")
	parser.add_option('-s', '--start', type=int, dest="startTime",
			  default=0, help = "FirstSwitched timestamp in unix seconds at which query should start")
        parser.add_option('-e', '--end', type=int, dest="endTime",
                          default=0, help = "FirstSwitched timestamp in unix seconds at which query should terminate ")
        parser.add_option('-d', '--database', default="MySQLReader", dest="databaseType",
                          help = "Database Reader")
        parser.add_option( '--host', dest="host", default="localhost", help = "Database host")
        parser.add_option('--port', dest="port", default=3306, type=int, help="Database port")
        parser.add_option('--user', dest="user", default="", help="Database user")
        parser.add_option('--password', dest="password", default="", help="Password for Database")
	parser.add_option('--dbname', dest="dbname", default="flows", help=" Name of the database containing the flows")
			  
	(options, args) = parser.parse_args()

        # if not options.startTime:
        #     print "You need to specify a start time with -s <unix seconds>"
        #     sys.exit(-1)

        # if not options.endTime:
        #     print "You need to specify a end time with -e <unix seconds>"
        #     sys.exit(-1)
            
	# if options.configfile != None:
	# 	try:
	# 		cf = file(options.configfile, 'r')
	# 		config = yaml.load(cf)
	# 	except Exception, e:
	# 		print "Could not open config file \"%s\": %s" % (options.configfile, e)
	# 		sys.exit(-1)
	# else:
	# 	# try to read default config file config.yml if no other config has been read
	# 	try:
	# 		cf = file('config.yml', 'r')
	# 		config = yaml.load(cf)
	# 	except Exception, e:
	# 		parser.print_help()
	# 		sys.exit(-1)

	# TODO: FIX this and make it generic ...
        from database import MySQLReader
        #reader = MySQLReader.MySQLReader(self.config['db_name'], self.config['db_host'], self.config['db_user'], self.config['db_password'])
	query = ' '.join(map(str, args))
        reader = MySQLReader.MySQLReader(options.dbname, options.host, options.user, options.password)
	reader.runQuery(query, options.startTime, options.endTime, printflow)

