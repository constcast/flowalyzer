-module(hostalyzer).
-export([start/0]).

-include("flows.hrl").

-record(state, {hostMap}).
-record(host, {ip, 
	       flowCount = 0, 
	       srcPorts = dict:new(), 
	       dstPorts = dict:new(), 
	       dstIPs = dict:new()}).

%%% Creates a new host record for storing the statistics on the
%%% given host
createHost(IP) ->
    #host{ip=IP}.

updateHostInfo(Host, Flow) ->
    FlowCount = Host#host.flowCount + 1,
    % for all dstPorts, srcPorts and dstIps update all statistics
    UpdateDict = fun(Dict, Value) -> dict:update_counter(Value, 1, Dict) end,
    % return updated hostinformation
    Host#host{flowCount = FlowCount,
	     srcPorts = UpdateDict(Host#host.srcPorts, Flow#flow.srcPort),
	     dstPorts = UpdateDict(Host#host.dstPorts, Flow#flow.dstPort),
	     dstIPs   = UpdateDict(Host#host.dstIPs,   Flow#flow.dstIP)}.


processFlows([Flow|Rest], State) ->
    % update the host map with new values
    case dict:is_key(Flow#flow.srcIP, State#state.hostMap) of
       true ->
	    Update = fun(X) ->  updateHostInfo(X, Flow) end,
	    NewHostMap = dict:update(Flow#flow.srcIP, Update, State#state.hostMap);
       false ->
	    Host = updateHostInfo(createHost(Flow#flow.srcIP), Flow),
	    NewHostMap = dict:store(Flow#flow.srcIP, Host, State#state.hostMap)
    end,
				     
    % return updated state
    processFlows(Rest, State#state{hostMap = NewHostMap});
processFlows([], State) ->
    State.

start() ->
    State = #state{hostMap = dict:new()},
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
