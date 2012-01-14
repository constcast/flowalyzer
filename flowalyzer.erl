-module(flowalyzer).
-export([start/0]).

-include("config.hrl").

start() ->
    io:format("FlowAlyzer starting up!~n"),

    % setup the flow readers and the distribution chain
    Distributor = spawn(distrib, start, []),
%    Distributor ! eof,
    Reader = spawn(?DBBACKEND, start, [Distributor, ?DBDEF]),

    ok.
    
    % ok, we are finished. Tell the Distributor that we have finished ...
    %io:format("No more content to be read from the reader ..."),
    %Distributor ! eof.

usage() ->
    io:format("usage: <progname>: "),
    halt(1).
