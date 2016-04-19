#!/usr/bin/env python

# See here 
#   http://wiki.ros.org/ROSNodeTutorialPython
#   for more info about dinamic reconfiguring.
#   Followed same structure


import roslib
import rospy
import sys
import time
import rfid

# Give ourselves the ability to run a dynamic reconfigure server.
from dynamic_reconfigure.server import Server as DynamicReconfigureServer

# Import custom message data 
from rfid.msg import Inventory
from rfid.msg import TagData
from rfid.msg import TagStats

# Import also dynamic reconfigure variables .
from node_rfid_inventory.cfg import rfid_inventory_paramsConfig as ConfigType

# Node example class.
class RFID_Inventory():
	
    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        # Get the ~private namespace parameters from command line or launch file.
        tinventory = float(rospy.get_param('~tinventory', '1.0'))
        trest = float(rospy.get_param('~trest', '1.0'))
        txpower = rospy.get_param('~txpower', '1.0')
        topic = rospy.get_param('~topic', 'Inventory')

        rospy.loginfo('tinventory = %d', tinventory)
        rospy.loginfo('txpower = %d', txpower)
        rospy.loginfo('trest = %d', trest)       
        rospy.loginfo('topic = %s', topic)

        # Create a dynamic reconfigure server and add reconfigure callback
        self.server = DynamicReconfigureServer(ConfigType, self.reconfigure)

        # Create a publisher
        pub = rospy.Publisher(topic, Inventory)

        # Set the message to publish as our custom message.
        self.inventory_msg = Inventory()
        
        # Main while loop.
        while not rospy.is_shutdown():
            # Prepare custom mesage
            self.inventory_msg.startTime = rospy.get_rostime()
            self.inventory_msg.maxTimeMiliSecs = self.tinventory
            self.inventory_msg.TxPower = self.txpower
            self.inventory_msg.tagList = []
            self.tag_dict = {}

            # get inventory: read tags for specified time
            self.getInventory()
            self.inventory_msg.tagList = self.tag_dict.values()

            # publish them
            pub.publish(self.inventory_msg)

            # Sleep for a while after publishing new messages
            if trest:
                rospy.sleep(trest)
            else:
                rospy.sleep(1.0)


    def getInventory(self):
        rfid.init()
        reader = rfid.startReader("tmr:///dev/rfid", self.rfidCallback)
        rfid.setHopTime(reader, 40)
        rfid.setPower(reader,self.txpower)

        # reader will be detecting tags while sleeping... I hope
        rospy.sleep(self.tinventory)



    def rfidCallback(message,self):
        self.inventory_msg.endTime=rospy.get_rostime()

        fields = str(message).split(':')
        tagID = fields[1]

        #get timestamp from fields
        timest =fields[6]

        # solve error with lower bit timestamp containing an i
        if timest.endswith("i"):
            timest=timest[1:len(timest)-1]

        timest= (fields[5]<<32) | timest

        # a Tag Stats message contains instantaneous transmission data
        tagSt = TagStats()
        tagSt.timestamp =  timest
        tagSt.rssi      = fields[2]
        tagSt.phase     = fields[3]
        tagSt.frequency = fields[4]

        if tagID not in self.tag_dict:
            newTag = TagData()
            newTag.ID = tagID
            self.tag_dict[tagID]=newTag

        self.tag_dict[tagID].stats.append(tagSt)


    # Create a callback function for the dynamic reconfigure server.
    def reconfigure(self, config, level):
        # Fill in local variables with values received from dynamic reconfigure clients (typically the GUI).
        self.tinventory = config["tinventory"]
        self.trest = config["trest"]
        self.txpower = config["txpower"]
        # Return the new variables.
        return config


# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('rfid_inventory')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        ne = RFID_Inventory()
    except rospy.ROSInterruptException: pass
