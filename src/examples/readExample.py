#!/usr/bin/env python

import rfid
import time

#  message is a string containing 
#           0:tagID:rssi:phase:frequency:timestampHigh:timestampLow
#     e.g.  0:300833B2DDD9014000000003:-75:104:911750:339:2908467775i
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

	try:
	    while True:
	        time.sleep(1)
	except KeyboardInterrupt:
    	    pass
	
	print "bye"
	rfid.stopReader(reader)
	rfid.close()
	
