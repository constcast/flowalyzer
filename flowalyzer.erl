#!/usr/bin/env escript

-mode(compile).

main(_) ->
    io:format("FlowAlyzer starting up!"),
    Reader = mysqlreader:start(mysqldb).

usage() ->
    io:format("usage: <progname>: "),
    halt(1).
