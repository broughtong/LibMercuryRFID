# LibMercuryRFID
Library for interacting with the Mercury API RFID Library from Python

# Installation

Run ./install.sh to install

Run ./uninstall.sh to uninstall

# Test the reader

Run the python code rfid_test.py to check that everything is working

#Building from source

The code can be compiled from source using the makefile provided.

The shared object Mercury Library file can be compiled by
downloading the source from the ThingMagic website, and compiling with 
these commands. A compiled version is already provided in this directory, 
in accordance with the ThingMagic License.

gcc -fPIC -Wall -Werror -g -Imercury/lib/LTK/LTKC/Library -Imercury/lib/LTK/LTKC/Library/LLRP.org -Imercury -c rfid.c
gcc -shared -o rfid.so rfid.o -Wl,-rpath '-Wl,$ORIGIN' -Imercury/lib/LTK/LTKC/Library -Imercury/lib/LTK/LTKC/Library/LLRP.org -Imercury mercury/libmercuryapi.so.1 -lpthread  mercury/lib/LTK/LTKC/Library/libltkc.so.1 mercury/lib/LTK/LTKC/Library/LLRP.org/libltkctm.so.1
rm *.o 2> /dev/null
rm *~ 2> /dev/null

