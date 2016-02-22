OBJS = lib/libmercuryrfid.o lib/enums.o
CC = gcc
IFLAGS = -Imercury/api/lib/LTK/LTKC/Library -Imercury/api/lib/LTK/LTKC/Library/LLRP.org -Imercury/api
CFLAGS = -fPIC -Wall -Werror -c
LFLAGS = -shared -Wall -Wl,-rpath '-Wl,$ORIGIN'
LOBJS = mercury/api/libmercuryapi.so.1 -lpthread  mercury/api/lib/LTK/LTKC/Library/libltkc.so.1 mercury/api/lib/LTK/LTKC/Library/LLRP.org/libltkctm.so.1

lib/libmercuryrfid.so.1 : $(OBJS)
	$(CC) $(LFLAGS) $(OBJS) -o lib/libmercuryrfid.so.1  $(IFLAGS) $(LOBJS)

lib/libmercuryrfid.o: src/libmercuryrfid.c
	$(CC) $(CFLAGS) $(IFLAGS) src/libmercuryrfid.c -o lib/libmercuryrfid.o

lib/enums.o: src/enums.c
	$(CC) $(CFLAGS) $(IFLAGS) src/enums.c -o lib/enums.o

clean:
	rm -f *~
	rm -f lib/*.o lib/*~
	rm -f src/*~

