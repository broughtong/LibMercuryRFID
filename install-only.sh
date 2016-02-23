#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Building Library..."
make > /dev/null
make clean &> /dev/null

echo "Installing RFID libraries"

ln -s libmercuryrfid.so.1.0 lib/libmercuryrfid.so.1 &> /dev/null

cp lib/libltkc.so.1 /usr/lib/
cp lib/libltkctm.so.1 /usr/lib/
cp lib/libmercuryapi.so.1 /usr/lib/
cp lib/libmercuryrfid.so.1.0 /usr/lib/
cp lib/libmercuryrfid.so.1 /usr/lib

echo "Installing Python Module"

cp src/rfid.py lib/rfid.py
chmod +x lib/rfid.py
cp lib/rfid.py /usr/lib/python2.7/rfid.py

echo "Finished Installing"
