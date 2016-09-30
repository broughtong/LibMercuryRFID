#!/usr/bin/env python
import ros, tf
import random, time

from SpatioModel import SpatioModel
from TagState import *

PARTICLE_COUNT = 1000

model = SpatioModel("models/3000.p")
tagStates = []

def parseTagData(data):
	data = data.split(":")
	id = data[1]
	rssi = int(data[2])
	phase = data[3]
	freq = data[4]
	return (id, rssi, phase, freq)

def tagCallback(data):

	(id, rssi, phase, freq) = parseTagData(data)
	now = rospy.Time(0)
	tfListener.waitForTransform(robotTFName, tagTFName, now, rospy.Duration(2.0))
	pos, orientation = tfListener.lookupTransform(robotTFName, tagTFName, now)
	newTagRead = TagRead(id, rssi, phase, freq, pos, orientation, time.time())

	foundTag = False
	for i in tagStates:
		if i.id == id:
			foundTag = True
			i.append(newTagRead)
	if foundTag == False:
		tagState = TagState(id)
		tagState.append(newTagRead)
		tagStates.append(tagState)

def main():

	random.seed(time.time())
	rospy.init_node('particle_filter_f')

	rospy.Subscriber("rfid/rfid_detect", String, tagCallback)
	rospy.spin()


if __name__ == '__main__':
	main()
