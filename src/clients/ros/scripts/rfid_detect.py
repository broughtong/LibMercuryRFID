#!/usr/bin/env python

import rospy
import std_msgs
import rfid

pub = ""

def rfidCallback(message):
	msg = str(message[0]) + ":" + str(message[1]) + ":" + str(message[2]) + ":" + str(message[3])
	# + ":" + str(message[4]) + ":" + str(message[5])
	#print msg
	
	pub.publish(msg)

if __name__ == "__main__":

	rospy.init_node("rfid_detect")
	pub = rospy.Publisher("rfid/rfid_detect", std_msgs.msg.String, queue_size=100)

	rfid.init()
	reader = rfid.startReader("tmr:///dev/rfid", rfidCallback)
	
	rospy.spin()

	rfid.stopReader(reader)
	rfid.close()
