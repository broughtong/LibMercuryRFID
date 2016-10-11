#!/usr/bin/env python

import rfid
import time
import sys

cupCounter=0
remoteCounter=0
glassesCounter=0
walletCounter=0

#  message is a string containing 
#           0:tagID:rssi:phase:frequency:timestampHigh:timestampLow
#     e.g.  0:300833B2DDD9014000000003:-75:104:911750:339:2908467775i

def rfidCallback(message):
	global tagID

	
	fields = str(message).split(':')
	tagID = fields[1]

	#get timestamp from fields
	timestampHigh =int(fields[5])

	# solve error with lower bit timestamp containing an i
	timestampLowStr = fields[6]
	if timestampLowStr.endswith("i"):
	    timestampLowStr=timestampLowStr[1:len(timestampLowStr)-1]

	timestampLow  =int(timestampLowStr)
	# timestamp in milisecs
	timest= ( timestampHigh<<32) | timestampLow
	
	secs =  timest/1000
	nsecs =  (timest%1000)*1000000
	rssi      = int(fields[2])
	phase     = int(fields[3])
	frequency = int(fields[4])



if __name__ == "__main__":


    rfid.init()

    reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)

    #newEpcData='\x30\x08\x33\xB2\xDD\xD9\x01\x41\x00\x00\x00\x0A' 
    if (len(sys.argv)==2 ):
	newEpcData = sys.argv[1] 
    else:
        newEpcData='300833B2DDD901410000000A' 

    #Stop from reading more tags
    rfid.stopReader(reader)

    error = True
    # just write first tag you get!   
    print "about to send %"
    print newEpcData
    print "\n\n "
    while error:
           error=(rfid.writeTag(reader, newEpcData,12)!=0)
	
    rfid.close()
	
