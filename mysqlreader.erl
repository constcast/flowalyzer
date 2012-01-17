%%% MySQL Reader Module
%%%
%%% Reads flows from a MySQL database and pushes Flow (see flows.hrl)
%%% to the successor modules. 

-module(mysqlreader).
-export([start/2]).

-include("config.hrl").
-include("reader.hrl").

% connectects to  adatabase using username and password
%start({Username, Password}) ->
% start(FlowDest, {_,_}) ->
%     ok;

% connects to the database using hte odbc database identifier in ~/.odbc.ini
start(FlowDest, DSN) ->
    application:start(odbc),
    ConnectString = io_lib:format("DSN=~w", [DSN]),
    {Ret, Connection} = odbc:connect(ConnectString, []),
    if Ret == ok ->
	    Connection;
       true  ->
	    io:format("Could not connect to database: ~p~n", [Connection])
    end,
    TableStrings = getTables(Connection),
    lists:foreach(fun(X) -> io:format("Table: ~s~n", [X]) end, TableStrings),
    Data = #readerData{handle = Connection, 
		       flowDest=FlowDest, 
		       firstEntry = getFirstTimestamp(Connection, lists:nth(1, TableStrings)),
		       lastEntry = getLastTimestamp(Connection, lists:last(TableStrings)),
		       winSize = ?SEND_INTERVAL,
		       currTime = getFirstTimestamp(Connection, lists:nth(1, TableStrings))},
    io:format("~w~n", [Data]),
    run(Data, TableStrings).

getTables(Conn) ->
    case odbc:sql_query(Conn, "SHOW TABLES LIKE 'h\\_%'") of
%    case odbc:sql_query(Conn, "SELECT * from exporter") of
	{selected, DescList, Results} ->
	    io:format("~p~n", [DescList]),

	    % Results come as tuples in UTF16 binary format. Convert to string uinsg
	    Fun = fun(Tuple) ->
			  TabString = element(1, Tuple),
			  [Y || <<Y/utf16-little>> <= TabString ]
		  end,
	    lists:map(Fun, Results);
	{error, Reason} ->
	    io:format("Error reading tables: ~p~n", [Reason])
    end.

secToDate(Seconds) ->
    BaseDate      = calendar:datetime_to_gregorian_seconds({{1970,1,1},{0,0,0}}),
    FinSeconds    = BaseDate + Seconds,
    { Date,Time} = calendar:gregorian_seconds_to_datetime(FinSeconds),
    {Date, Time}.

% takes two unix time stamps and calculates the table names
% that are used to store all flows between [First, Last]
getTableNames(First, Last) when First < Last ->
    % tables span 30 minutes worth of data
    TableIntervalLen = 30 * 60,
    AlignedStart = First - (First rem TableIntervalLen),
    {Date, Time} = secToDate(AlignedStart),
    % build table name from timestamp
    TableName = io_lib:format("h_~p~p~p_~p_~p", [element(1, Date), element(2, Date), element(3, Date), element(1, Time), element(2, Time) div 30]),

    io:format("~s~n", [TableName]),
    [TableName | getTableNames(AlignedStart + TableIntervalLen, Last)];
getTableNames(First, Last) ->
    [].
   

getFirstTimestamp(Conn, Table) ->
    QueryString = io_lib:format("SELECT MIN(firstSwitched) FROM ~s", [Table]),
    case odbc:sql_query(Conn, QueryString) of
	{selected, DescList, []} ->
	    io:format("Table is empty", []);
	{selected, DescList, Result} ->
	    element(1, lists:nth(1, Result));
	{error, Reason} ->
	    io:format("Error selecting first timestamp: ~s~n", [Reason])
    end.
    

getLastTimestamp(Conn, Table) ->
    QueryString = io_lib:format("SELECT MAX(firstSwitched) FROM ~s", [Table]),
    case odbc:sql_query(Conn, QueryString) of
	{selected, _, []} ->
	    io:format("Table is empty", []);
	{selected, _, Result} ->
	    element(1, lists:nth(1, Result));
	{error, Reason} ->
	    io:format("Error selecting last timestamp: ~s~n", [Reason])
    end.


%%% run(Conn, PID)
%%%      Main mysqldbreader loop. Starts pulling flows from the Database and 
%%%      pushes the results to the process defined in PID. 
%%%      We let the database pull out data for SEND_PID (defined in config.hrl)
%%%      worth of flows and push them in one bunch to the receiving ends.
run(Mysqldata, [FirstTable | Rest]) ->
    getTableNames(Mysqldata#readerData.firstEntry, Mysqldata#readerData.lastEntry),
    QueryString = io_lib:format("SELECT * FROM ~s ORDER BY firstSwitched", [FirstTable]),
    case odbc:sql_query(Mysqldata#readerData.handle, QueryString) of
	{selected, DescList, Results} ->
	    io:format("~w~n~w~n", [DescList, Results]),
	    ok;
	{error, Reason} ->
	    io:format("Error selecting flows from database: ~s", [Reason])
    end,
    run(Mysqldata, Rest).

    
