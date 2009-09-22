#
# $Id: Makefile,v 1.6 2003/05/21 09:41:19 ludo Exp $
#

CFLAGS=-O2 -Wall
CC=gcc-3.4
BINARIES=getClientResponse getClientResponse.nostatic
OBJECTS=getClientResponse.o dictionary.o iniparser.o strlib.o

all: $(BINARIES)

getClientResponse: $(OBJECTS)
	$(CC) -s -o $@ $^ --static

getClientResponse.nostatic: $(OBJECTS)
	$(CC) -o $@ $^

clean:
	rm -f $(BINARIES) $(OBJECTS)
