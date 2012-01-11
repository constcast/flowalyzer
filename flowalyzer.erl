-module(flowalyzer).
-export([start/0]).


start() ->
    io:format("FlowAlyzer starting up!~n"),
    Reader = mysqlreader:start(mysqldb),
    halt(0).

usage() ->
    io:format("usage: <progname>: "),
    halt(1).
