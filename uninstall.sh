#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Removing udev rules"

rm /etc/udev/rules.d/99-virtual-usb.rules

echo "Removing RFID Libraries"

rm /usr/local/lib/rfid.so

echo "Removing Python Modules"

rm /usr/lib/python2.7/rfid.py

echo "Finished Uninstalling"
