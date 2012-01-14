-module(csvreader).
-export([start/2]).

-include("config.hrl").
-include("reader.hrl").
-include("flows.hrl").


%%% Main function of this module. Should be called  in a process
start(FlowDest, _) ->
    Input = ?CSVINPUT,
    {Ret, Dev} = file:open(Input, read),
    if Ret == ok ->
	    ok;
       true ->
	    io:format("Could not open CSV input file ~p: ~p~n", [Input, Dev])
    end,
    
    ReaderData = #readerData{handle = Dev, flowDest = FlowDest, startTime = now()},
    run(ReaderData).

%%%
%%% fileOutput(output)
%%%    handle output from the CSV line. Remove trailing newline
%%%    and split line into individual parts. These are then transformed
%%%    into a flow object and returned by the function
fileOutput({ok, Line}) ->
    % remove trailing 
    CSVLine = string:substr(Line, 1, string:len(Line) - 1),
    CSVLine;
fileOutput(eof) ->
    io:format("Finished reading input file ...~n"),
    eof;
fileOutput({error, Reason}) ->
    io:format("Error reading CSV input file: ~p~n", [Reason]),
    eof.

run(ReaderData) ->
    Res = fileOutput(file:read_line(ReaderData#readerData.handle)),
    if 
	Res == eof ->
	    ReaderData#readerData.flowDest ! eof,
	    ok;
	true ->
	    Tokens = string:tokens(Res, ","),
	    Flow = flows:getFlowFromList(Tokens),
	    ReaderData#readerData.flowDest ! Flow,
	    run(ReaderData)
    end.
