import pprint as pp
import os.path
import numpy
import rospy
import sys
import pickle
from std_msgs.msg import String
from nav_msgs.msg import *

from tf import TransformListener
from math import *

tagLocations = []
gridSize = 160 #8m forward, 8m back
transmissionPower = 3000
model = [] #format each freq is element, consisting of [freq, 2dmatrix] each matrix cell [mapped rssi, no of reads]
pub = ""
map = []

def normaliseVector(v):
	tol = 0.00001
	mag2 = sum(n * n for n in v)
	if abs(mag - 1.0) > tol:
		mag = sqrt(mag2)
		v = tuple(n / mag for n in v)
	return v

def quaternionMult(q1, q2):
	w1, x1, y1, z1 = q1
	w2, x2, y2, z2 = q2
	w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
	x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
	y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
	z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
	return w, x, y, z

def quaternionConjugate(q):
	w, x, y, z = q
	return (w, -x, -y, -z)

def quaternionVectorMult(q, v):
	q2 = (0.0,) + v
	return quaternionMult(quaternionMult(q, q2), quaternionConjugate(q))[1:]

def axisAngleToQuaternion(v, theta):
	v = normaliseVector(v)
	x, y, z = v
	theta /= 2
	w = cos(theta)
	x = x * sin(theta)
	y = y * sin(theta)
	z = z * sin(theta)
	return w, x, y, z

def quaternionToAxisAngle(q):
	w, v = q[0], q[1:]
	theta = acos(w) * 2.0
	return normaliseVector(v), theta

def tagCallback(data):

	global model

	if not tf.frameExists("/base_link"):

		print "Error finding tf frame for base link"
		return

	elif not tf.frameExists("/map"):

		print "Error finding tf frame for odometry"
		return

	now = rospy.Time.now()
	tf.waitForTransform("/map", "/base_link", now, rospy.Duration(1.0))
	position, quat = tf.lookupTransform("/map", "/base_link", now)

	#print position
	
	data = str(data)
	data = data.split(":")
	tagID = data[2]
	freq = data[5]
	rssi = data[3]
	tx = 3000
	
	for i in tagLocations:
		if i[0] == tagID:
			#print "found tag with known pos"
			tagx = i[1]
			tagy = i[2]

			freqFound = False

			for j in model:
				if j[0] == freq:
					#found known tag + freq
					freqFound = True

			if freqFound == False:
				#if freq is new to us
				oc = OccupancyGrid()
				oc.header.frame_id = '/base_link'
				oc.info.resolution = 0.1
				oc.info.width = gridSize
				oc.info.height = gridSize
				oc.data = []

				encounter = []

				for i in xrange(0, gridSize * gridSize):
					oc.data.append(-1)
					encounter.append(0)

				pub = rospy.Publisher("rfid/build_model_map_" + str(freq), OccupancyGrid)
				
				newFreq = [freq, oc, encounter, pub]
				model.append(newFreq)

			for j in model:
				if j[0] == freq:
					#convert pos to local coords,
					#update cell to reflect
					tagPos = (float(tagx), float(tagy), float(0))
					robotPos = position
					normPos = (tagPos[0] - float(robotPos[0]), tagPos[1] - float(robotPos[1]), tagPos[2] - float(robotPos[2]))
					#print "tagpos: "
					#print tagPos
					#print "robotPos"
					#print robotPos
					#normPos = tagPos - robotPos
					v = quaternionVectorMult(quat, normPos) 
					
					correctedx = int(floor(v[0])) + (gridSize / 2)
					correctedy = int(floor(v[1])) + (gridSize / 2)
					oneDimIndex = (correctedx * gridSize) + correctedy
					currentRssi = j[1].data[oneDimIndex]
					currentReliability = j[2][oneDimIndex]

					#currentRssi = j[1][correctedx][correctedy][0]
					#currentReliability = j[1][correctedx][correctedy][1]

					#print "CurrentRSSI" + str(currentRssi) + "Current rel" + str(currentReliability)

					rel = int(((currentRssi * currentReliability) + int(rssi)) / (currentReliability + 1))

					#print "before + after"
					#print correctedy
					#print j[1][correctedx][correctedy]
					#print j[1][correctedx][correctedy-1]
					#j[1][correctedx][correctedy][0] = rel
					#j[1][correctedx][correctedy][1] += 1
					###############################
					#j[1].data[oneDimIndex] = rel
					#j[2][oneDimIndex] += 1	
					model[0][1].data[25500] = 100
					#model[0][1].data[oneDimIndex] = 100
					model[0][2][oneDimIndex] += 1
					model[0][1].info.origin.position.x = 8
					model[0][1].info.origin.position.y = -8
					model[0][1].info.origin.position.z = 0
					model[0][1].info.origin.orientation.x = 0
					model[0][1].info.origin.orientation.y = 0
					model[0][1].info.origin.orientation.z = 1
					model[0][1].info.origin.orientation.w = 1

					##############################				
					#j[1].info.origin.position.x = 8
					#j[1].info.origin.position.y = -8
					#j[1].info.origin.position.z = 0
					#j[1].info.origin.position.x = robotPos[0]
					#j[1].info.origin.position.y = robotPos[1]
					#j[1].info.origin.position.z = robotPos[2]
					#j[1].info.origin.orientation.x = 0.0 
					#j[1].info.origin.orientation.y = 0.0 
					#j[1].info.origin.orientation.z = 1.0 
					#j[1].info.origin.orientation.w = 1.0 

					#print j
					#print j[3]
					
					j[3].publish(model[0][1])
					#ctr = 0
					#for u in xrange(0, len(j[1])):
					#	for v in xrange(0, len(j[1][u])):
					#		print ctr, u, v
					#		try:
					#			map.data[ctr] = j[1][u][v][0]
#
#							except:
#								pass
#							ctr += 1


					#pub.publish(j[1])	

						


if __name__ == '__main__':
	args = sys.argv
	del args[0]

	if len(args) == 0:
		print "Error: No tag to track"
	else:
		foundPower = False

		for i in args:
			if i.startswith("--power="):
				foundPower = True
				transmissionPower = i[8:]
			else:
				i = i.split(":")
				tagLocations.append(i)				

		if foundPower == False:
			print "Transmission power not set, using default"

		fname = "models/" + str(transmissionPower) + ".p"

		#if os.path.isfile(fname):
		#	model = pickle.load(open(fname, "rb"))

		rospy.init_node('buildModel')
		tf = TransformListener()
		sub = rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

		rospy.spin()

		pickle.dump(model, open(fname, "wb"))
		#print model[0][1]