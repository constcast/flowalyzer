#!/usr/bin/env python

from optparse import OptionParser

from mainmodule import getMainModule

import sys

if __name__ == "__main__":
	parser = OptionParser("usage: %prog --start <second> --end <second> [query]")
	parser.add_option('-s', '--start', type=int, dest="startTime",
			  default=0, help = "FirstSwitched timestamp in unix seconds at which query should start")
        parser.add_option('-e', '--end', type=int, dest="endTime",
                          default=0, help = "FirstSwitched timestamp in unix seconds at which query should terminate ")
        parser.add_option('-d', '--database', default="MySQLReader", dest="databaseType",
                          help = "Database Reader")
        parser.add_option( '--src-host', dest="host", default="localhost", help = "Database host")
        parser.add_option('--src-port', dest="port", default=3306, type=int, help="Database port")
        parser.add_option('--user', dest="user", default="", help="Database user")
        parser.add_option('--password', dest="password", default="", help="Password for Database")
			  
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
        #from database import config.
        #reader = MySQLReader
