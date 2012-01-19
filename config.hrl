%-define(DBDEF, mysqldb).
%-define(DBBACKEND, mysqlreader).

-define(DBBACKEND, csvreader).
-define(DBDEF, "flows-test.csv").

-define(SEND_INTERVAL, 300).
