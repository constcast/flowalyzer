%%% Distribution module
%%% Takes flows from multiple destinations and pipes them
%%% to its successors. These must been added by sending a
%%% {addConsumer, Pid} message to the module

-module(distrib).
-export([start/0]).

-record(localState, {consumerList}).

start() ->
    % TODO: build some state
    State = #localState{consumerList = []},
    run(State).

handle_flow(Flow, ConsumerList) ->
    Fun = fun(Pid) -> Pid ! Flow end,
    lists:foreach(Fun, ConsumerList),
    ok.

shutdown(ConsumerList) ->
    io:format("Shutting down receiver ...~n"),
    Fun = fun(Pid) -> Pid ! eof end,
    lists:foreach(Fun, ConsumerList),
    ok.

run(State) ->
    receive 
	eof  ->
	    shutdown(State#localState.consumerList);
	{addConsumer, Consumer} ->
	    NewState = State#localState{consumerList = lists:append(State#localState.consumerList, [Consumer])},
	    run(NewState);
	{removeConsumer, Consumer} ->
	    ok;
	Flow ->
	    handle_flow(Flow, State#localState.consumerList),
	    run(State)
    end.
	    
	    
