#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Removing udev rules"

rm /etc/udev/rules.d/99-virtual-usb.rules

echo "Removing RFID Libraries"

rm /usr/lib/rfid.so
rm /usr/lib/libltkc.so.1
rm /usr/lib/libltkctm.so.1
rm /usr/lib/libmercuryapi.so.1
rm /usr/lib/libmercuryrfid.so.1

echo "Removing Python Modules"

rm /usr/lib/python2.7/rfid.py

echo "Finished Uninstalling"
