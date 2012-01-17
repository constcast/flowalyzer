-module(hostalyzer).
-export([start/0]).

-record(state, {hostMap}).
-record(host, {ip, srcPorts, dstPorts, dstIPs}).

processFlow(Flow, State) ->
    
    State.

start() ->
    State = #state{hostMap = dict:new()},
    run(State).

run(State) ->
    receive 
	eof ->
	    ok;
	Flow ->
	    NewState = processFlow(Flow, State),
	    run(NewState)
    end.
