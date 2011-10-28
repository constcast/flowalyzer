#!/usr/bin/env python

import MySQLdb, os, sys, calendar, string, time

from operator import mod

import config
import utils import *


if __name__ == "__main__":
        # get to the flow database, aggregate new data and push it to RDD
        try:
                connection = MySQLdb.connect(config.db_host, config.db_user, config.db_password, config.db_name)
        except MySQLdb.OperationalError, message:
                print('%d: Error connecting to database: %s' %(message[0], message[1]))
                sys.exit(-1)
        c = connection.cursor()

	do_temp_stuff(c)


