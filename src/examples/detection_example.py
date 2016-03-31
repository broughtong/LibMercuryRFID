#!/usr/bin/env python

import rfid
import time

cupCounter=0
remoteCounter=0
glassesCounter=0
walletCounter=0

#  message is a string containing 
#           0:tagID:rssi:phase:frequency:timestampHigh:timestampLow
#     e.g.  0:300833B2DDD9014000000003:-75:104:911750:339:2908467775i
def rfidCallback(message):
	global cupCounter
	global remoteCounter
	global glassesCounter
	global walletCounter
	
	msg = str(message)
	fields = msg.split(':')

	tagID = fields[1]
	rssi = fields[2]
	phase = fields[3]
	friendlyName="other"

	#print fields[0] + ":" + fields[1] +":" +fields[2]+":" +fields[3]
	
	if tagID.endswith("05"):
		friendlyName="Cup"
		cupCounter=cupCounter+1
		if cupCounter>50:			
			print "Detected " + friendlyName +  " tag with RSSI "  + rssi  +  " and phase " + phase
			cupCounter=0
	elif tagID.endswith("06"):
		friendlyName="Remote"
		remoteCounter=remoteCounter+1
		if remoteCounter>50:			
			print "Detected " + friendlyName +  " tag with RSSI "  + rssi  +  " and phase " + phase
			remoteCounter=0
	elif tagID.endswith("07"):
		friendlyName="Glasses"
		glassesCounter=glassesCounter+1
		if glassesCounter>50:			
			print "Detected " + friendlyName +  " tag with RSSI "  + rssi  +  " and phase " + phase
			glassesCounter=0
	elif tagID.endswith("08"):
		friendlyName="Wallet"
		walletCounter=walletCounter+1
		if walletCounter>50:			
			print "Detected " + friendlyName +  " tag with RSSI "  + rssi  +  " and phase " + phase
			walletCounter=0


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
	
