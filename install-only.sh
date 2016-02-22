#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Building Library..."
make > /dev/null
make clean > /dev/null

echo "Installing RFID libraries"

cp lib/libltkc.so.1 /usr/lib/libltkc.so.1
cp lib/libltkctm.so.1 /usr/lib/libltkctm.so.1
cp lib/libmercuryapi.so.1 /usr/lib/libmercuryapi.so.1
cp lib/libmercuryrfid.so.1 /usr/lib/libmercuryrfid.so.1

echo "Installing Python Module"

cp lib/rfid.py /usr/lib/python2.7/rfid.py

echo "Finished Installing"
