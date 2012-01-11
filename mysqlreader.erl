-module(mysqlreader).
-export([start/1]).
-include("config.hrl").

% connectects to  adatabase using username and password
start({Username, Password}) ->
    ok;
% connects to the database using hte odbc database identifier in ~/.odbc.ini
start(DSN) ->
    application:start(odbc),
    ConnectString = io_lib:format("DSN=~w", [DSN]),
    {Ret, Connection} = odbc:connect(ConnectString, []),
    if Ret == ok ->
	    Connection;
       true  ->
	    io:format("Could not connect to database: ~p~n", [Connection])
    end.
    
