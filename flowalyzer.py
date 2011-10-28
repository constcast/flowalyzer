#!/usr/bin/env python

from optparse import OptionParser

from analyzer import MainModule

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

	main = MainModule(config)
	main.run()


