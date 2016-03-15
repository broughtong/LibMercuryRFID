#!/usr/bin/env python
import rfid

def myCallback(message):
	print message

if __name__ == "__main__":

	rfid.init()
	reader = rfid.startReader("tmr:///dev/rfid", myCallback)

	_ = raw_input()

	rfid.stopReader(reader)
	rfid.close()
