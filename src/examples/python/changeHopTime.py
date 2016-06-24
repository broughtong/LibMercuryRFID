#!/usr/bin/env python
import rfid

def rfidCallback(message):
	
	msg = str(message)
	fields = msg.split(':')

	tagID = fields[1]
	rssi = fields[2]
	phase = fields[3]

	print "Detected " + tagID +  " tag with RSSI "  + rssi  +  " and phase " + phase

if __name__ == "__main__":

	rfid.init()
	reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)

	print rfid.getHopTime(reader) #defaults to 375
	rfid.setHopTime(reader, 40)
	print rfid.getHopTime(reader)

	_ = raw_input()

	rfid.stopReader(reader)
	rfid.close()
	
