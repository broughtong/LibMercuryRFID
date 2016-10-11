#!/usr/bin/env python
import rfid

def rfidCallback(message):
	pass

if __name__ == "__main__":

	rfid.init()
	reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)

	print "Current hop time is: " + str(rfid.getHopTime(reader))
	print "Setting hop time to 100ms"
	rfid.setHopTime(reader, 100)
	print "Current hop time is: " + str(rfid.getHopTime(reader))

	_ = raw_input()
	
	rfid.stopReader(reader)
	rfid.close()

