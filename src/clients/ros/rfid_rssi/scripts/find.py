#!/usr/bin/env python
import ros, tf
import random, time

from SpatioModel import SpatioModel

PARTICLE_COUNT = 1000

model = SpatioModel("models/3000.p")
tagState = []

def parseTagData(data):
	data = data.split(":")
	id = data[1]
	rssi = int(data[2])
	phase = data[3]
	freq = data[4]
	return (id, rssi, freq)

def tagCallback(data):

	(id, rssi, freq) = parseTagData(data)

	for tag in tagState:

		if tag

def main():

	random.seed(time.time())
	rospy.init_node('particle_filter_f')

	rospy.Subscriber("rfid/rfid_detect", String, tagCallback)
	rospy.spin()


if __name__ == '__main__':
	main()
