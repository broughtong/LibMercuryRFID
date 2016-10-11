#!/usr/bin/env python
import rfid

def rfidCallback(message):
	print message

if __name__ == "__main__":

	rfid.init()
	reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)

	_ = raw_input()

	rfid.stopReader(reader)
	rfid.close()
