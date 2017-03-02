#!/usr/bin/env python
import ros, tf
import random, time
import threading, Queue

from SpatioModel import SpatioModel
from TagState import *
from ParticleFilter import ParticleFilter

PARTICLE_COUNT = 1000

model = SpatioModel("models/3000.p")
tagStates = []
threadQueue = Queue.Queue()

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

	threadQueue.put(newTagRead)

def main():

	random.seed(time.time())

	threadQueue = Queue.Queue()
	particleThread = ParticleFilter(threadQueue)

	rospy.init_node('particle_filter_f')
	rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

	rospy.spin()

	threadQueue.put("exit")

if __name__ == '__main__':
	main()
