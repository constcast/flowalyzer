-module(flowalyzer).
-export([start/0]).

-include("config.hrl").

start() ->
    io:format("FlowAlyzer starting up!~n"),
    Reader = ?DBBACKEND:start(?DBDEF),
    halt(0).

usage() ->
    io:format("usage: <progname>: "),
    halt(1).
