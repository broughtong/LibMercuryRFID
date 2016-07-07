#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

#sudo apt-get install -y python make

echo "Building Library..."

mkdir -p build/lib &> /dev/null
mkdir -p build/clients/ros &> /dev/null
mkdir build/clients/python &> /dev/null
mkdir build/clients/c++ &> /dev/null
mkdir build/examples &> /dev/null

make > /dev/null
cp lib/* build/lib/

ln -sf libmercuryrfid.so.1.0 build/lib/libmercuryrfid.so.1
ln -sf libmercuryrfid.so.1 build/lib/libmercuryrfid.so

echo "Installing RFID libraries"

ln -s libmercuryrfid.so.1.0 build/lib/libmercuryrfid.so.1 &> /dev/null

cp build/lib/libltkc.so.1 /usr/lib/
cp build/lib/libltkctm.so.1 /usr/lib/
cp build/lib/libmercuryapi.so.1 /usr/lib/
cp build/lib/libmercuryrfid.so.1.0 /usr/lib/
ln -sf libmercuryrfid.so.1.0 /usr/lib/libmercuryrfid.so.1
ln -sf libmercuryrfid.so.1 /usr/lib/libmercuryrfid.so

echo "Installing Client Modules"

#Python
mkdir build/clients/python &> /dev/null
cp src/clients/python/rfid.py build/clients/python/rfid.py
chmod +x build/clients/python/rfid.py
cp build/clients/python/rfid.py /usr/lib/python2.7/rfid.py

#ROS
mkdir build/clients/ros &> /dev/null
cp -r src/clients/ros/ build/clients/ros

#C++
ln -sf libmercuryrfid-c.so.1.0 build/clients/c++/libmercuryrfid-c.so.1
cp build/clients/c++/libmercuryrfid-c.so.1.0 /usr/lib
ln -sf libmercuryrfid-c.so.1.0 /usr/lib/libmercuryrfid-c.so.1

echo "Finishing Installation"

ldconfig

echo "Finished Installing"
