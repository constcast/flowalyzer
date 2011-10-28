import MySQLdb, os, sys, calendar, string, time
from operator import mod

def int2ip(i):
        # konvertiert einen Integer in eine IP im dotted-quad Format
        return str(i//2**24)+"."+str((i//2**16)%256)+"."+str((i//2**8)%256)+"."+str(i%256)

def dropTempTable(name, c):
        c.execute("DROP TEMPORARY TABLE IF EXISTS " + name)

def getTempTable(startTime, endTime, c):
        tables = []
        c.execute("SHOW TABLES LIKE 'h\\_%'")
        for row in c.fetchall():
                tabletime = calendar.timegm([string.atoi(row[0][2:6]), string.atoi(row[0][6:8]), string.atoi(row[0][8:10]), \
                        string.atoi(row[0][11:13]), string.atoi(row[0][14])*30, 0, 0, 0, 0])
                # one table is 30 minutes == 30*60
                tableLength = 30*60
                alignedStart = startTime - mod(startTime, tableLength)
                alignedEnd = endTime + tableLength - mod(endTime + tableLength, tableLength)
                if tabletime >= alignedStart and tabletime < alignedEnd:
                        tables.append(row[0])

        if len(tables) == 0:
                raise Exception("No table found!")
                return False

        # FIXME: this is buggy if we have more than one instance working on the database ....
        retTable = tables[0] + "_temp"

        #c.execute(

        # create a temporary merge table in memory
        c.execute("SET max_heap_table_size=512*1024*1024")
        c.execute("SHOW CREATE TABLE " +  tables[0])
        tmp = (c.fetchone())[1]
        tmp = tmp.replace("CREATE TABLE", "CREATE TEMPORARY TABLE", 1)
        tmp = tmp.replace(tables[0], retTable)
        tmp = tmp.replace("MyISAM", "MEMORY", 1)
        c.execute(tmp)

        # pull all interesting flows into the temporary merge table
        for t in tables:
                # FIXME: Find the resoan for flow records with srcIP == 0
                tmp = "INSERT "+retTable+" SELECT * FROM "+t+" WHERE firstSwitched BETWEEN "+str(startTime)+" AND "+str(endTime)+" AND srcIp != 0"
                c.execute(tmp)

        return retTable

def getExporterStats(c):
        ret = list()

        exporterStats = open("exporterStats.txt", "w")
        c.execute("SELECT id,sourceID,inet_ntoa(srcIP) from exporter")
        for i in c.fetchall():
                ret.append(i[0])
                exporterStats.write("%d %s %d\n" %(i[0], i[2], i[1]))

        exporterStats.close()
        return ret


def exportFromQuery(c, query, exporterFile):
        c.execute(query)
        for i in c.fetchall():
                if i[0]:
                        exporterFile.write("\t%u" % i[0])
                else:
                        exporterFile.write("\t0")
 

def do_temp_stuff(config, c):
	starttime = 1313594804
	endtime   = 1316526512
	stepsize = 300
	rows = int((endtime - starttime) / stepsize)

        exporterIDs = getExporterStats(c)
        statsPerExp = dict()
        for i in exporterIDs:
                statsPerExp[i] = open("traffStat_exp_" + str(i) + ".dat", "w")
                if not statsPerExp[i]:
                        print "Could not open file!!!!"
                        sys.exit(-1)
		statsPerExp[i].write("# Format: timestamp in unixseconds, number of packets, number of bytes, average flow duration in seconds, distinct srcIPs, distinct dstIPs, distinct IPs\n")
        

        j = starttime
        for i in range(rows):
                print "Processing data for interval %u - %u (final %u, %u intervals to go at intervall size %u) ..." % (j, j + stepsize, endtime, rows - i, stepsize)
                j = j + stepsize
                myTable = getTempTable(j, j + stepsize, c)
                if myTable:
                        # get stats from tmpTable for each exporter
                        for exporter in exporterIDs:
                                expFile = statsPerExp[exporter]

                                # record time stamp
                                expFile.write("%u " % j)

                                cmd = "SELECT SUM(pkts) from " + myTable + " where exporterID = " + str(exporter)
                                exportFromQuery(c, cmd, expFile)

                                cmd = "SELECT SUM(bytes) from " + myTable + " where exporterID = " + str(exporter)
                                exportFromQuery(c, cmd, expFile)

                                cmd = "SELECT avg(lastSwitched-firstSwitched) from " + myTable + " where exporterID = " + str(exporter)
                                exportFromQuery(c, cmd, expFile)


                                cmd = "SELECT COUNT(DISTINCT(srcIP)) from " + myTable + " where exporterID = " + str(exporter)
                                exportFromQuery(c, cmd, expFile)
                        
                                cmd = "SELECT COUNT(DISTINCT(dstIP)) from " + myTable + " where exporterID = " + str(exporter)
                                exportFromQuery(c, cmd, expFile)
                                
 				# TODO: this does not work!
                                #cmd = "select count(*) from (SELECT srcIP from " + myTable + " where exporterID = " + str(exporter) + " union select dstIP from " + myTable + " where exporterID = " + str(exporter) + ") as bla"
				#print cmd
				#exportFromQuery(c, cmd, expFile)
				# This works instead:
				uniqIPs = set()
				cmd = "SELECT DISTINCT srcIP from " + myTable + " where exporterID = " + str(exporter)
				c.execute(cmd)
				uniqIPs.update(c.fetchall())
				cmd = "SELECT DISTINCT dstIP from " + myTable + " where exporterID = " + str(exporter)
				c.execute(cmd)
				uniqIPs.update(c.fetchall())
				expFile.write("\t%u" % (len(uniqIPs)))

                                expFile.write("\n")

                        # we have all we need. Drop the table
                        dropTempTable(myTable, c)

        for i in statsPerExp.keys():
                statsPerExp[i].close()


def BA_TEMP_STUFF(config):
        # get to the flow database, aggregate new data and push it to RDD
        try:
                connection = MySQLdb.connect(config['db_host'], config['db_user'], config['db_password'], config['db_name'])
        except MySQLdb.OperationalError, message:
                print('%d: Error connecting to database: %s' %(message[0], message[1]))
                sys.exit(-1)
        c = connection.cursor()

	do_temp_stuff(config, c)


