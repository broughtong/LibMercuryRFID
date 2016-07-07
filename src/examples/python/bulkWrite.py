#!/usr/bin/env python

import rfid
import time
import sys
import tty, termios


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

def getChar():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch


# writes several correlative tags
if __name__ == "__main__":

    if (len(sys.argv)==3):
        newEpcDataCommon = sys.argv[1]
        newEpcDataFirstVal = int(sys.argv[2],16) 
    else:
		print "Not enough parameters"
		sys.exit(2) 

	#init rfid reader
    rfid.init()
    reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)
    rfid.stopReader(reader)
    
    haveFinished = False
    newEpcDataVal=newEpcDataFirstVal
    newEpcData=newEpcDataCommon+(hex(newEpcDataVal)[2:]).zfill(len(sys.argv[2]))   
    newEpcData=newEpcData.upper()
    
    if (len(newEpcData)!=24):
		print "Tag id lenght is not 12 bytes, is "+str(len(newEpcDataCommon)/2.0)+"+"+str(len((hex(newEpcDataVal)[2:]).zfill(len(sys.argv[2])))/2.0)
		sys.exit(2)
    
    while (haveFinished==False):    
		error = True
		print "about to write "+ newEpcData
		print "\n\n "
		while error:
			error=(rfid.writeTag(reader, newEpcData,12)!=0)
		newEpcDataVal=newEpcDataVal+1
		newEpcData=newEpcDataCommon+(hex(newEpcDataVal)[2:]).zfill(len(sys.argv[2]))   
		newEpcData=newEpcData.upper()
		print "proceed with next one ("+newEpcData+")? [Y/n] "
		answer=getChar()
		haveFinished=answer=='n'
    print "bye!"
    rfid.close()
    sys.exit(0)
