%%% Oracle Reader Module
%%%
%%% Reads flows from a Oracle database and pushes Flow (see flows.hrl)
%%% to the successor modules. 

-module(oraclereader).
-export([start/2]).

-include("config.hrl").
-include("reader.hrl").

% connects to the database using hte odbc database identifier in ~/.odbc.ini
start(FlowDest, DSN) ->
    application:start(odbc),
    ConnectString = io_lib:format("DSN=~w", [DSN]),
    {Ret, Connection} = odbc:connect(ConnectString, [{scrollable_cursors, off}]),
    if Ret == ok ->
	    Connection;
       true  ->
	    io:format("Could not connect to database: ~p~n", [Connection])
    end,
    TableStrings = getTables(Connection),
    Data = #readerData{handle = Connection, 
		       flowDest=FlowDest, 
		       firstEntry = getFirstTimestamp(Connection, lists:nth(1, TableStrings)),
		       lastEntry = getLastTimestamp(Connection, lists:last(TableStrings)),
		       winSize = ?SEND_INTERVAL,
		       firstQuery = getFirstTimestamp(Connection, lists:nth(1, TableStrings)),
		       lastQuery = getLastTimestamp(Connection, lists:last(TableStrings)),
		       currTime = getFirstTimestamp(Connection, lists:nth(1, TableStrings))},
    run(Data).

getTables(Conn) ->
%    case odbc:sql_query(Conn, "SHOW TABLES LIKE 'h\\_%'") of
    case odbc:sql_query(Conn, "SELECT * FROM user_objects WHERE object_type = 'TABLE' AND object_name LIKE 'H_%'") of
	{selected, _, Results} ->
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
    TableName = io_lib:format("H_~p~2.2.0w~2.2.0w_~2.2.0w_~p", [element(1, Date), element(2, Date), element(3, Date), element(1, Time), element(2, Time) div 30]),

    [TableName | getTableNames(AlignedStart + TableIntervalLen, Last)];
getTableNames(_, _) ->
    [].
   

getFirstTimestamp(Conn, Table) ->
    QueryString = io_lib:format("SELECT MIN(firstSwitched) FROM ~s", [Table]),
    case odbc:sql_query(Conn, QueryString) of
	{selected, _, []} ->
	    io:format("Table is empty", []);
	{selected, _, Result} ->
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

getFlows(Conn, [FirstTable | Rest], First, Last) ->
    QueryString = io_lib:format("SELECT * FROM ~s where firstSwitched >= ~w and firstSwitched <= ~w ORDER BY firstSwitched", [FirstTable, First, Last]),
    case odbc:sql_query(Conn, QueryString) of 
	{selected, _, []} ->
	    getFlows(Conn, Rest, First, Last);
	{selected, _, Results} ->
	    Flows = lists:map(fun(X) -> flows:getFlowFromList(tuple_to_list(X)) end, Results),
	    Flows ++ getFlows(Conn, Rest, First, Last);
	{error, Reason} ->
	    io:format("Error selecting flows from Table ~s: ~s~n", [FirstTable, Reason])
    end;
getFlows(_, [], _, _) ->
    [].

%%% run(Conn, PID)
%%%      Main mysqldbreader loop. Starts pulling flows from the Database and 
%%%      pushes the results to the process defined in PID. 
%%%      We let the database pull out data for SEND_PID (defined in config.hrl)
%%%      worth of flows and push them in one bunch to the receiving ends.
run(Data) when Data#readerData.currTime < Data#readerData.lastQuery ->
    Last = min(Data#readerData.lastQuery, Data#readerData.currTime + Data#readerData.winSize),
    NewData = Data#readerData{currTime = Data#readerData.currTime + Data#readerData.winSize},
%    io:format("Fetching Flows...~n", []),
    Data#readerData.flowDest ! getFlows(Data#readerData.handle, getTableNames(Data#readerData.currTime, Last), Data#readerData.currTime, Last),
    run(NewData);
run(_) -> 
    ok.
    
