OBJS = lib/libmercuryrfid.o lib/enums.o
CC = gcc
IFLAGS = -Isrc/lib/mercury/api/lib/LTK/LTKC/Library -Isrc/lib/mercury/api/lib/LTK/LTKC/Library/LLRP.org -Isrc/lib/mercury/api
CFLAGS = -fPIC -Wall -Werror -c
LFLAGS = -shared -Wall -Wl,-soname,libmercuryrfid.so.1
LIBS = src/lib/mercury/api/libmercuryapi.so.1 -lpthread  src/lib/mercury/api/lib/LTK/LTKC/Library/libltkc.so.1 src/lib/mercury/api/lib/LTK/LTKC/Library/LLRP.org/libltkctm.so.1

lib/libmercuryrfid.so.1.0 : $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o lib/libmercuryrfid.so.1.0  $(IFLAGS) $(LIBS)

lib/libmercuryrfid.o: src/lib/libmercuryrfid.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/libmercuryrfid.c -o lib/libmercuryrfid.o

lib/enums.o: src/lib/enums.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/enums.c -o lib/enums.o

clean:
	@rm -f *~
	@rm -f lib/*.o lib/*~
	@rm -f src/*~

