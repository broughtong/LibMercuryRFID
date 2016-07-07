#!/usr/bin/env python

import rospy
import std_msgs
import rfid

from rfid_node.msg import TagData
from rfid_node.msg import TagStats

pub = ""

def isValidData(data):
    if len(data)<7:
        rospy.logerr("LibMercury msg too short (%d)" ,len(data))
        return False
    if len(data[1])<14:
        rospy.logerr("Tag id is not 14 chars long (%d)" ,len(data[1]))
        return False
    
    value=data[2] 
    if value.startswith("-"):
        value=value[1:len(value)]
    if not value.isdigit():    # integer with sign
        rospy.logerr("RSSI is not signed integer (%s)" ,data[2])
        return False
    
    value=data[3] 
    if value.startswith("-"):
        value=value[1:len(value)]
    if not value.isdigit():    # integer with sign
        rospy.logerr("phase is not signed integer (%s)" ,data[3])
        return False
    
    if not data[4].isdigit():    # positive integer
        rospy.logerr("frequency is not a positive integer (%s)" ,data[4])
        return False
    if not data[5].isdigit():  # positive integer
        rospy.logerr("High byte timestamp is not a positive integer (%s)" ,data[5])
        return False
                    
    if not data[6].isdigit():  # positive integer
        rospy.logerr("low byte timestamp is not a positive integer '%s'" ,data[5])
        return False
                
    return True       




def rfidCallback(message):
    global tag_pub
    fields = str(message).split(':')
    tagID = fields[1]
    
    if isValidData(fields):
        try:
            #get timestamp from fields
            timestampHigh =int(fields[5])

            timestampLowStr = fields[6]            
            
            timestampLow  =int(timestampLowStr)
            # timestamp in milisecs
            timest= ( timestampHigh<<32) | timestampLow

            # a Tag Stats message contains instantaneous transmission data
            tagSt = TagStats()
            tagSt.timestamp.secs =  timest/1000
            tagSt.timestamp.nsecs =  (timest%1000)*1000000
            tagSt.rssi      = int(fields[2])
            
            tagSt.phase     = float(fields[3])
            tagSt.frequency = int(fields[4])
                            
            lastTag=TagData()
            lastTag.ID = tagID
            lastTag.stats.append(tagSt)
            
            tag_pub.publish(lastTag)
                
        # a failure in rfid library could produce wrong values
        except ValueError: pass
    
    # print tag data
    if False:
      rospy.loginfo('%s,%s,%s,%s,%d', tagID,fields[2], fields[3], fields[4], timest)
    if False:
      rospy.loginfo('Detected tag id: %s', tagID)
      rospy.loginfo('RSSi = %s', fields[2])
      rospy.loginfo('phase = %s', fields[3])
      rospy.loginfo('frequency = %s', fields[4])
      rospy.loginfo('Timestamp = %d', timest)



if __name__ == "__main__":
    global tag_pub
    rospy.init_node("rfid_detect")
    tag_pub = rospy.Publisher("lastTag", TagData,queue_size=10)
    txpower = int(rospy.get_param('~txpower', '3000'))
    
    rfid.init()
    reader = rfid.startReader("tmr:///dev/ttyACM0", rfidCallback)
        
    rfid.setHopTime(reader, 40) 
    rfid.setRegionEU(reader)
    rfid.setPower(reader, txpower)
    rfid.getPower(reader)
    rospy.spin()

    rfid.stopReader(reader)
    rfid.close()
