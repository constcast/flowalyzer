-module(flowalyzer).
-export([start/0]).

-include("config.hrl").

start() ->
    io:format("FlowAlyzer starting up!~n"),

    % setup the flow readers and the distribution chain
    Distributor = spawn(distrib, start, []),

    % setup consumers
    HostAlyzer    = spawn(hostalyzer, start, []),
    FlowlenAlyzer = spawn(flowlenalyzer, start, []),
    
    % connect them to the distributor
%    Distributor ! {addConsumer, HostAlyzer},
    Distributor ! {addConsumer, FlowlenAlyzer},

    % start flow source
    spawn(?DBBACKEND, start, [Distributor, ?DBDEF]),    

    ok.
    
    % ok, we are finished. Tell the Distributor that we have finished ...
    %io:format("No more content to be read from the reader ..."),
    %Distributor ! eof.
