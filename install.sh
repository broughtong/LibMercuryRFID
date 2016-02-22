#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "Building Library..."
make > /dev/null
make clean > /dev/null

echo "Adding User to correct groups"
sudo usermod -a -G dialout $USER

read -p "Make sure the RFID reader is unplugged and then press enter" dummy
unplugged="$(ls /dev | grep "ttyUSB")"
read -p "Now plug the RFID reader in and then press enter" dummy
plugged="$(ls /dev | grep "ttyUSB")"

fileList="$(diff <(echo "$unplugged") <(echo "$plugged"))"
file="$(echo $fileList | cut -d " " -f 5)"
echo RFID detected at: $file
echo "Persistant symlink created at /dev/rfid for this device"

prod="$(udevadm info -a -n /dev/$file | grep '{idProduct}' | head -n1 | tr -d '[[:space:]]')"
vend="$(udevadm info -a -n /dev/$file | grep '{idVendor}' | head -n1 | tr -d '[[:space:]]')"
seri="$(udevadm info -a -n /dev/$file | grep '{serial}' | head -n1 | tr -d '[[:space:]]')"

echo "SUBSYSTEM==\"tty\", $vend, $prod, $seri, SYMLINK+=\"rfid\"" > /etc/udev/rules.d/99-virtual-usb.rules

sudo udevadm control --reload-rules

echo "Settings updated, unplug and replug rfid device for /dev/rfid to appear"

echo "Installing RFID libraries"

cp lib/libltkc.so.1 /usr/lib/libltkc.so.1
cp lib/libltkctm.so.1 /usr/lib/libltkctm.so.1
cp lib/libmercuryapi.so.1 /usr/lib/libmercuryapi.so.1

echo "Installing Python Module"

cp lib/rfid.py /usr/lib/python2.7/rfid.py

echo "Finished Installing"
