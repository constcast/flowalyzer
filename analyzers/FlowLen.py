from BaseAnalyzer import BaseAnalyzer

class Biflow:
    """
    Creates a biflow from the corresponding flow
    """
    def __init__(self, flow):
        self.minIP = min(flow.srcIP, flow.dstIP)
        self.maxIP = max(flow.srcIP, flow.dstIP)
        self.minPort = min(flow.srcPort, flow.dstPort)
        self.maxPort = max(flow.srcPort, flow.dstPort)
        self.proto = flow.proto
        

class Analyzer(BaseAnalyzer):
    def __init__(self, config, reportIntervals, workingdir):
        BaseAnalyzer.__init__(self, config, reportIntervals, workingdir)

        self.flowmap = dict()

    def processFlow(self, flow):
        biflow = Biflow(flow)
        if biflow in self.flowmap:
            print biflow
        else:
            self.flowmap[biflow] = flow

    def generateReport(self, reportNumber, starttime, endTime):
        print "foobar"
