#!/usr/bin/env python

from optparse import OptionParser

from mainmodule import MainModule

import sys, yaml

if __name__ == "__main__":
	parser = OptionParser("usage: %prog [options]")
	parser.add_option('-c', '--config', dest="configfile",
			  help = "config file in yml format (required)")
			  
	(options, args) = parser.parse_args()

	if options.configfile != None:
		try:
			cf = file(options.configfile, 'r')
			config = yaml.load(cf)
		except Exception, e:
			print "Could not open config file \"%s\": %s" % (options.configfile, e)
			sys.exit(-1)
	else:
		parser.print_help()
		sys.exit(-1)

	main = MainModule(config)
	main.run()


