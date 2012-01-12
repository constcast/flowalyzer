-module(flows).
-export([getFlowFromList/1]).

-include("flows.hrl").

getFlowFromList([DstIP, SrcIP, SrcPort, DstPort, Proto, DstTos, Bytes, Pkts, FirstSwitched, LastSwitched, FirstSwitchedMillis, LastSwitchedMillis, ExporterID]) ->
    #flow{dstIP = DstIP, 
	  srcIP = SrcIP, 
	  srcPort = SrcPort, 
	  dstPort = DstPort, 
	  proto = Proto, 
	  dstTos = DstTos, 
	  bytes = Bytes, 
	  pkts = Pkts, 
	  firstSwitched = FirstSwitched, 
	  lastSwitched=LastSwitched, 
	  firstSwitchedMillis = FirstSwitchedMillis, 
	  lastSwitchedMillis = LastSwitchedMillis, 
	  exporterID = ExporterID}.
