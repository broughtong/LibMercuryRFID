SHELL := /bin/bash

OBJS = build/lib/libmercuryrfid.o build/lib/enums.o build/lib/queue.o
CC = gcc
IFLAGS = -Isrc/lib/mercury/lib/LTK/LTKC/Library -Isrc/lib/mercury/lib/LTK/LTKC/Library/LLRP.org -Isrc/lib/mercury/
CFLAGS = -fPIC -Wall -Werror -c
LFLAGS = -shared -Wall -Wl,-soname,libmercuryrfid.so.1
LIBS = lib/libmercuryapi.so.1 -lpthread lib/libltkc.so.1 lib/libltkctm.so.1

.PHONY: all
all: build/lib/libmercuryrfid.so.1.0

build/lib/libmercuryrfid.so.1.0: $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o build/lib/libmercuryrfid.so.1.0  $(IFLAGS) $(LIBS)

build/lib/libmercuryrfid.o: src/lib/libmercuryrfid.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/libmercuryrfid.c -o build/lib/libmercuryrfid.o

build/lib/enums.o: src/lib/enums.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/enums.c -o build/lib/enums.o

build/lib/queue.o: src/lib/queue.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/queue.c -o build/lib/queue.o

.PHONY: clean
clean:
	@rm -rf build
	@rm -rf *~

