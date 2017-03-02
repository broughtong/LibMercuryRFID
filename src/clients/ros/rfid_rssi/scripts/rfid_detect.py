#!/usr/bin/env python

import rospy
import std_msgs
import rfid
from std_msgs.msg import String
pub = ""

def rfidCallback(message):

	pub.publish(message)

if __name__ == "__main__":

	rospy.init_node("rfid_detect")
	pub = rospy.Publisher("/rfid/rfid_detect", String, queue_size=100)

	rfid.init()
	reader = rfid.startReader("tmr:///dev/ttyACM0", rfidCallback)
	rfid.setPower(reader,3000)

	rfid.setHopTime(reader, 40) 
	#rfid.setRegionEU(reader)

	rospy.spin()

	rfid.stopReader(reader)
	rfid.close()
