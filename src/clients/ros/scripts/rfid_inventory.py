#!/usr/bin/env python

# See here 
#   http://wiki.ros.org/ROSNodeTutorialPython
#   for more info about dinamic reconfiguring.
#   Followed same structure


import roslib
import rospy
import rospy.rostime
import sys
import time
import math
import rfid as m6e

# Import custom message data 
from rfid_node.msg import Inventory
from rfid_node.msg import TagData
from rfid_node.msg import TagStats

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
    global inventory_msg
    global tag_dict
    global tag_pub
    inventory_msg.lastTagTime=rospy.get_rostime()

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
                
            if tagID not in tag_dict:
                newTag = TagData()
                newTag.ID = tagID
                tag_dict[tagID]=newTag

            tag_dict[tagID].stats.append(tagSt)
            
            lastTag=TagData()
            lastTag.ID = tagID
            lastTag.stats.append(tagSt)
            
            tag_pub.publish(lastTag)
                
        # a failure in rfid library could produce wrong values
        except ValueError: pass
    
    # print tag data
    if True:
      rospy.loginfo('Detected tag id: %s', tagID)
      rospy.loginfo('RSSi = %s', fields[2])
      rospy.loginfo('phase = %s', fields[3])
      rospy.loginfo('frequency = %s', fields[4])
      rospy.loginfo('Timestamp = %d', timest)

# Node example class.
class RFID_Inventory():

    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        global inventory_msg
        global tag_dict
        global reader
        global tag_pub
        # "Constants" or variables you should really not change
        # power is in 100 dBm
        POWER_STEP=100  # decreasing power after each inventory
        MIN_POWER=500   # minimum reading power
        MAX_POWER=3000  # maximum reading power

        # Init our global vars...
        inventory_msg = Inventory()
        tag_dict = {}

        # Get the ~private namespace parameters from command line or launch file.
        self.tinventory = float(rospy.get_param('~tinventory', '2.0'))
        self.trest = float(rospy.get_param('~trest', '1.0'))
        self.txpower = int(rospy.get_param('~txpower', '3000'))
        self.topic = rospy.get_param('~topic', 'Inventory')

        rospy.loginfo('tinventory = %d', self.tinventory)
        rospy.loginfo('txpower = %d', self.txpower)
        rospy.loginfo('trest = %d', self.trest)       
        rospy.loginfo('topic = %s', self.topic)

        # Create a publisher
        pub = rospy.Publisher(self.topic, Inventory,queue_size=10)
        tag_pub = rospy.Publisher("lastTag", TagData,queue_size=10)

        # Init reader
        m6e.init()
        reader = m6e.startReader("tmr:///dev/rfid", rfidCallback)
        m6e.setHopTime(reader, 40)
        m6e.getPower(reader)
        m6e.stopReader(reader)
        



        # Main while loop.
        while not rospy.is_shutdown():
            # Prepare custom mesage
            #inventory_msg = Inventory()
            inventory_msg.readingTime = rospy.Duration(self.tinventory)
            inventory_msg.TxPower = self.txpower
            inventory_msg.tagList = []
            tag_dict = {}

            m6e.setPower(reader, self.txpower)
            m6e.getPower(reader)

            # get inventory: read tags for specified time
            inventory_msg.startTime = rospy.get_rostime() # closest to the real starting moment
            #m6e.reStartReader(reader)
            self.getInventory()
            #m6e.stopReader(reader)

            # if inventory was successful, do a 'smaller' one
            if (len(tag_dict)> 0):
                inventory_msg.tagList = tag_dict.values()
                # publish them
                pub.publish(inventory_msg)
                self.txpower = self.txpower-POWER_STEP
                if (self.txpower<MIN_POWER):
                    self.txpower=MAX_POWER
            else:
                self.txpower=MAX_POWER

            # Sleep for a while after publishing new messages
            rospy.sleep(self.trest)



    def getInventory(self):
        global tag_dict
        global reader

        rospy.loginfo('Starting inventory.............................' )
        # reader will be detecting tags while this is sleeping...
        rospy.sleep(self.tinventory)
        rospy.loginfo('Detected %d different tags:', len(tag_dict))
        rospy.loginfo('%s', tag_dict.keys())
        rospy.loginfo('Inventory ended   .............................' )


# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('rfid_inventory')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        ne = RFID_Inventory()
    except rospy.ROSInterruptException: pass
