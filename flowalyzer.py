#!/usr/bin/env python

from optparse import OptionParser

import sys, yaml

#from utils import *


if __name__ == "__main__":
	parser = OptionParser("usage: %prog [options]")
	parser.add_option('-c', '--config', dest="configfile",
			  help = "config file in yml format")
			  
	(options, args) = parser.parse_args()

	if options.configfile != None:
		try:
			cf = file(options.configfile, 'r')
			config = yaml.load(cf)
		except Exception, e:
			print "Could not open config file \"%s\": %s" % (options.configfile, e)
			sys.exit(-1)
	else:
		print "You need to specify a yml config file. We do not yet support command line configuration, yet :("
		sys.exit(-1)


#        # get to the flow database, aggregate new data and push it to RDD
#        try:
#                connection = MySQLdb.connect(config.db_host, config.db_user, config.db_password, config.db_name)
#        except MySQLdb.OperationalError, message:
#                print('%d: Error connecting to database: %s' %(message[0], message[1]))
#                sys.exit(-1)
#        c = connection.cursor()
#
#	do_temp_stuff(c)
#

