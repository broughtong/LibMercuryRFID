#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

sudo apt-get install -y python make

echo "Building Library..."

mkdir -p build/lib &> /dev/null
mkdir build/clients &> /dev/null

make > /dev/null
cp lib/* build/lib/

echo "Installing RFID libraries"

ln -s libmercuryrfid.so.1.0 build/lib/libmercuryrfid.so.1 &> /dev/null

cp build/lib/libltkc.so.1 /usr/lib/
cp build/lib/libltkctm.so.1 /usr/lib/
cp build/lib/libmercuryapi.so.1 /usr/lib/
cp build/lib/libmercuryrfid.so.1.0 /usr/lib/
cp build/lib/libmercuryrfid.so.1 /usr/lib

echo "Installing Python Module"

mkdir build/clients/python &> /dev/null
cp src/clients/python/rfid.py build/clients/python/rfid.py
chmod +x build/clients/python/rfid.py
cp build/clients/python/rfid.py /usr/lib/python2.7/rfid.py

echo "Finished Installing"
