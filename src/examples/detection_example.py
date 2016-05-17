#!/usr/bin/env python

import rfid
import time
import  math
  

#  message is a string containing
#           0:tagID:rssi:phase:frequency:timestampHigh:timestampLow
#     e.g.  0:300833B2DDD9014000000003:-75:104:911750:339:2908467775i
def rfidCallback(message):
    global counters
    global tagDesc

    msg = str(message)
    fields = msg.split(':')

    tagID = fields[1]
    rssi = float(fields[2])
    phase = float(fields[3])
    frequency= float(fields[4])
    friendlyName="other"

    if tagDesc.has_key(tagID):
        friendlyName=tagDesc[tagID]
        avPhase[tagID]=	(avPhase[tagID]*counters[tagID]+phase)/(counters[tagID]+1)
        #average power...
        pot=pow(10,rssi/10)
        avpot=pow(10,avPot[tagID]/10)
        avpot=(avpot*counters[tagID]+pot)/(counters[tagID]+1)
        avPot[tagID]= 10* math.log10(avpot)
        counters[tagID]=counters[tagID]+1

        if counters[tagID] > 50:
            #print "Detected " + friendlyName + " tag with RSSI " + str(avPot[tagID]) + " and phase " + str(avPhase[tagID])
            print "Detected %s tag (RSSI %3.1f, phase %3.1f)" % (friendlyName,avPot[tagID],avPhase[tagID])
            counters[tagID] = 0
    else:
        #site=tagID[2:4]
        #if ((site=="01")|(site=="00")):
         #   tagDesc[tagID]="Site "+site+", Object "+tagID[-2:]
        #else:
        tagDesc[tagID]=tagID
        counters[tagID] = 1
        avPhase[tagID] = phase
        avPot[tagID] = rssi





if __name__ == "__main__":

    tagDesc = {"390000010000000000000000": "Manuel's Chair", 
               "390000010000000000000001": "Serhan's Chair",
               "390000010000000000000002": "Feng's Chair", 
               "390000010000000000000003": "Printer's table",
               "390000010000000000000004": "Alfie's table",
               "390000010000000000000005": "Baxter's Table",
               "390000010000000000000006": "Lounge's table",
               "390000010000000000000007": "Kitchens's table",
               "390000010000000000000008": "Sofa (bottom)",
               "390000010000000000000009": "Red stappler", 
               "390000010000000000000010": "Black xbox gamepad",
               "390000010000000000000011": "Linda's keyboard", 
               "390000010000000000000012": "Logitech gamepad A",
               "390000010000000000000013": "Projector's remote",
               "390000010000000000000014": "Manuel's mug",
               "390000010000000000000015": "Scotch tape",
               "390000010000000000000020": "Workshop's Chair"}

    counters = dict()
    avPhase = dict()
    avPot = dict()
    for i in tagDesc.keys():
        counters[i] = 0
        avPhase[i] = 0
        avPot[i] = 0

                
    rfid.init()
    reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)

    print rfid.getHopTime(reader) #defaults to 375
    rfid.setHopTime(reader, 40)
    print rfid.getHopTime(reader)
    rfid.setPower(reader, 2700)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    print "bye"
    rfid.stopReader(reader)
    rfid.close()
	

