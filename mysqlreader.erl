-module(mysqlreader).
-export([start/1]).

-include("config.hrl").
-include("mysqlreader.hrl").

% connectects to  adatabase using username and password
%start({Username, Password}) ->
start({_,_}) ->
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
    end,
    getTables(Connection),
    data = #mySQLData{conn = Connection }.
    %run(Conn, PID).

getTables(Conn) ->
    Results = odbc:sql_query(Conn, "SHOW TABLES LIKE 'h\\_%'"),
    lists:foreach(fun(X) -> io:format("~p~n", [X]) end, Results).

%%% run(Conn, PID)
%%%      Main mysqldbreader loop. Starts pulling flows from the Database and 
%%%      pushes the results to the process defined in PID. 
%%%      We let the database pull out data for SEND_PID (defined in config.hrl)
%%%      worth of flows and push them in one bunch to the receiving ends.
%run(mysqldata, PID) ->
%    ok.
    
