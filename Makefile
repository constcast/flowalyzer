all:
	erl -pa ebin -make

clean:
	rm -f *.beam
	rm -f erl_crash.dump