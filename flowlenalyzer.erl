-module(flowlenalyzer).
-export([start/0]).

-include("flows.hrl").

-record(state, {biflowList, maxLen = 0}).
-record(biflowEntry, {minIP, maxIP, minPort, maxPort, proto}).
%-record(biflowStats, {bytes, packets}).

%%% Creates a new host record for storing the statistics on the
%%% given host
createBiflow(Flow) ->
    #biflowEntry{minIP   = min(Flow#flow.srcIP,   Flow#flow.dstIP),
		 maxIP   = max(Flow#flow.srcIP,   Flow#flow.dstIP),
		 minPort = min(Flow#flow.srcPort, Flow#flow.dstPort),
		 maxPort = max(Flow#flow.srcPort, Flow#flow.dstPort),
		 proto = Flow#flow.proto}.

dumpFlowStats(FlowDir1, FlowDir2) ->
    io:format("~p | ~p~n", [FlowDir1, FlowDir2]),
    ok.

processFlows([Flow|Rest], State) ->
    BiFlow = createBiflow(Flow),
    case dict:is_key(BiFlow, State#state.biflowList) of
       true ->
	    dumpFlowStats(Flow, dict:fetch(BiFlow, State#state.biflowList)),
	    NewBiflowList = dict:erase(BiFlow, State#state.biflowList);
       false ->
	    NewBiflowList = dict:append(BiFlow, Flow, State#state.biflowList)
    end,
    processFlows(Rest, State#state{biflowList = NewBiflowList});
processFlows([], State) ->
    State.

start() ->
    State = #state{biflowList = dict:new()},
    run(State).

run(State) ->
    receive 
	eof ->
	    io:format("Received End of Flow signal.~n", []),
	    ok;
	Flows ->
%	    io:format("Received flows ...~n", []),
	    NewState = processFlows(Flows, State),
%	    io:format("Finsihed processing flows!~n", []),
	    run(NewState)
    end.
