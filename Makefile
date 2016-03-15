OBJS = build/libmercuryrfid.o build/enums.o
CC = gcc
IFLAGS = -Isrc/lib/mercury/api/lib/LTK/LTKC/Library -Isrc/lib/mercury/api/lib/LTK/LTKC/Library/LLRP.org -Isrc/lib/mercury/api
CFLAGS = -fPIC -Wall -Werror -c
LFLAGS = -shared -Wall -Wl,-soname,libmercuryrfid.so.1
LIBS = src/lib/mercury/api/libmercuryapi.so.1 -lpthread  src/lib/mercury/api/lib/LTK/LTKC/Library/libltkc.so.1 src/lib/mercury/api/lib/LTK/LTKC/Library/LLRP.org/libltkctm.so.1

build/libmercuryrfid.so.1.0 : $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o build/libmercuryrfid.so.1.0  $(IFLAGS) $(LIBS)

build/libmercuryrfid.o: src/lib/libmercuryrfid.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/libmercuryrfid.c -o build/libmercuryrfid.o

build/enums.o: src/lib/enums.c
	$(CC) $(CFLAGS) $(IFLAGS) src/lib/enums.c -o build/enums.o

clean:
	@rm -f *~
	@rm -f build/*.o build/*~
	@rm -f src/*~

