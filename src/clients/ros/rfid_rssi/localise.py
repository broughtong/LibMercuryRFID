import numpy
import rospy
import sys
import pickle
from std_msgs.msg import String
from tf import TransformListener
from math import *

sensorModel = []
worldModel = []

#x = 160x160x2
#model = [[freq1, x], [freq2, x2]]

def genModels():
	for i in sensorModel:
		freq = i[0]
		lmap = [[0.00004] * 160] * 160
		worldModel.append([freq, lmap])

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
	q2 = (0.0,) + v1
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

	if not tf.frameExists("/base_link"):

		print "Error finding tf frame for base link"
		return

	elif not tf.frameExists("/odom_combined"):

		print "Error finding tf frame for odometry"
		return

	now = rospy.Time.now()
	tf.waitForTransform("/base_link", "/odom_combined", now, rospy.Duration(1.0))
	position, quat = tf.lookupTransform("/base_link", "/odom_combined", now)

	data = str(data)
	data = data.split(":")	
	tagID = data[2]
	freq = data[5]
	rssi = int(data[3])
	tx = 3000

	for i in sensorModel:
		if i[0] == freq:
			tmp = i[1]

			max = -99
			for x in tmp:
				for y in x:
					y[0] = abs(y[0] - rssi)
					if y[0] > max:
						max = y[0]

			max2 = -99
			for x in tmp:
				for y in x:
					y[0] = max - y[0]
					if y[0] > max2:
						max2 = y[0]

			total = 0
			for x in tmp:
				for y in x:
					y[0] = y[0] / max			
					total += y[0]

			avg = total / 25600

			for x in tmp:
				for y in x:
					y[0] = y[0] - avg

			#change matrix complete			

			for q in worldModel:
				if q[0] == freq:
					#using existing map

					min = 99
					for x in xrange(0, len(q[1])):
						for y in xrange(0, len(q[1][x])):
							q[1][x][y][0] += tmp[x][y][0]
							if q[1][x][y][0] < min:
								min = q[1][x][y][0]
								
					sum = 0
					for x in xrange(0, len(q1)):
						for y in xrange(0, len(q[1][x])):
							q[1][x][y][0] = q[1][x][y][0] - min
							sum += q[1][x][y][0]

					for x in xrange(0, len(q1)):
						for y in xrange(0, len(q[1][x])):
							q[1][x][y][0] = q[1][x][y][0] / sum

	#display / print results
	#calc'd						

if __name__ == '__main__':

	sensorModel = pickle.load(open("models/3000.p", "rb"))
	genModels()

	rospy.init_node('localise')
	tf = TransformListener()
	sub = rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

	rospy.spin()

	#sub.shutdown()

