gcc -fPIC -Wall -Werror -g -Imercury/lib/LTK/LTKC/Library -Imercury/lib/LTK/LTKC/Library/LLRP.org -Imercury -c rfid.c enums.c
gcc -shared -o rfid.so rfid.o enums.o -Wl,-rpath '-Wl,$ORIGIN' -Imercury/lib/LTK/LTKC/Library -Imercury/lib/LTK/LTKC/Library/LLRP.org -Imercury mercury/libmercuryapi.so.1 -lpthread  mercury/lib/LTK/LTKC/Library/libltkc.so.1 mercury/lib/LTK/LTKC/Library/LLRP.org/libltkctm.so.1
rm *.o 2> /dev/null
rm *~ 2> /dev/null
