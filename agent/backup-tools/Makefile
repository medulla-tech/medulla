# $Id: Makefile 34 2004-04-27 13:57:55Z jblache $

CFLAGS = $(shell pkg-config glib-2.0 --cflags)
LIBS = $(shell pkg-config glib-2.0 --libs)

cdlist: cdlist.c
	gcc -Wall -g $(CFLAGS) $(LIBS) -o cdlist cdlist.c

clean:
	rm -f *~ *.o cdlist core
