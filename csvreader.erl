-module(csvreader).
-export([start/1]).

-include("config.hrl").
-include("reader.hrl").
-include("flows.hrl").


%%% Main function of this module. Should be called by in a process
start(_) ->
    Input = ?CSVINPUT,
    {Ret, Dev} = file:open(Input, read),
    if Ret == ok ->
	    ok;
       true ->
	    io:format("Could not open CSV input file ~p: ~p~n", [Input, Dev])
    end,
    
    ReaderData = #readerData{handle = Dev},
    run(ReaderData).

%%%
%%% fileOutput(output)
%%%    handle output from the CSV line. Remove trailing newline
%%%    and split line into individual parts. These are then transformed
%%%    into a flow object and returned by the function
fileOutput({ok, Line}) ->
    % remove trailing 
    CSVLine = string:substr(Line, 1, string:len(Line) - 1),
    io:format("~p~n", [CSVLine]),
    CSVLine;
fileOutput(eof) ->
    io:format("Finished reading input file ...~n"),
    eof;
fileOutput({error, Reason}) ->
    io:format("Error reading CSV input file: ~p~n", [Reason]),
    eof.

getRec([DstIP, SrcIP, SrcPort, DstPort, Proto, DstTos, Bytes, Pkts, FirstSwitched, LastSwitched, FirstSwitchedMillis, LastSwitchedMillis, ExporterID]) ->
    #flow{dstIP = DstIP, srcIP = SrcIP, srcPort = SrcPort, dstPort = DstPort, proto = Proto, dstTos = DstTos, bytes = Bytes, pkts = Pkts, firstSwitched = FirstSwitched, lastSwitched=LastSwitched, firstSwitchedMillis = FirstSwitchedMillis, lastSwitchedMillis = LastSwitchedMillis, exporterID = ExporterID}.

run(ReaderData) ->
    Res = fileOutput(file:read_line(ReaderData#readerData.handle)),
    if 
	Res == eof ->
	    ok;
	true ->
	    Tokens = string:tokens(Res, ","),
	    Flow = getRec(Tokens),
	    io:format("~p~n", [Flow])
	    %run(ReaderData)
    end.
