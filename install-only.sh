#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

sudo apt-get install -y python make

echo "Building Library..."
make > /dev/null
make clean &> /dev/null

echo "Installing RFID libraries"

ln -s libmercuryrfid.so.1.0 build/libmercuryrfid.so.1 &> /dev/null

cp build/libltkc.so.1 /usr/lib/
cp build/libltkctm.so.1 /usr/lib/
cp build/libmercuryapi.so.1 /usr/lib/
cp build/libmercuryrfid.so.1.0 /usr/lib/
cp build/libmercuryrfid.so.1 /usr/lib

echo "Installing Python Module"

cp src/clients/python/rfid.py build/clients/python/rfid.py
chmod +x build/clients/python/rfid.py
cp build/clients/python/rfid.py /usr/lib/python2.7/rfid.py

echo "Finished Installing"
