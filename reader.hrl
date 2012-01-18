-record(readerData, {handle,       % DB handle
		    flowDest,      % Process id of flow sink
		    startTime = 0, % Timestamp of process stat
		    firstEntry = 0,% Timestamp of the first flow in the DB
		    lastEntry = 0, % Timestamp of the last flow in the DB (at startup time)
		    firstQuery = 0,% Get flows with firstSwiched >= firstQuery
		    lastQuery  = 0,% Get flows with firstSwitched <= lastQuery
		    currTime = 0,  % Current time stamp in flow table (points to the flow firstswitchedTime of the last send flow)
		    winSize = 0    % Window size for flows to get as chunk from the DB
		    }).
