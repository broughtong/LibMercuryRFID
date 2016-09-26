#!/usr/bin/env python
# #import ros



import rospy
import tf

#for loading models
import pickle
import os

#getting command line arguments
import sys

#for reading rfid messages
from std_msgs.msg import String

#for writing navigation og messages
from nav_msgs.msg import *

#for trig for map calculations
from math import *

#Configurables - distances in meters
#gridSize = distance from robot to edge of map in all directions
#gridResolution = the cell size of the map
gridSize = 9
gridResolution = 0.3
transmissionPower = 3000

#globals
tagIDs = []
tfListener = ""
gridTotal = int(gridSize/gridResolution)
#model, each element is a frequency model
#each frequency model has the following format
#[ROS publisher, frequency(kHz), 2D ROS occupancy grid,
#detections, mean, standard deviation]
model = []


<<<<<<< HEAD
	data = str(data)
	data = data.split(":")
	tagID = data[2]
	freq = data[5]
	rssi = int(data[3])
	tx = 3000

	if not tagID in tagIDs:
		return
 	if not tfListener.frameExists("/base_link"):
		print "Unable to find tf frame for base link"
		return
	if not tfListener.frameExists("/map"):
		print "Unable to find tf frame for map"
		return
	if not tfListener.frameExists("/rfid/tags/" + tagID):
		print "Unable to find tf frame for rfid tag: " + tagIDs[0]
		return

	now = rospy.Time(0)
	tfListener.waitForTransform("map", "base_link", now, rospy.Duration(4.0))
	r_pos, r_quat = tfListener.lookupTransform("/map", "/base_link", now)
	tfListener.waitForTransform("map", "rfid/tags/" + tagID, now, rospy.Duration(4.0))
	t_pos, t_quat = tfListener.lookupTransform("/map", "/rfid/tags/" + tagID, now)

	foundFrequency = False

	for i in model:
		if i[1] == freq:
			foundFrequency = True

	if foundFrequency == False:
		createModel(freq)

	for i in model:
		if i[1] == freq:
			roll, pitch, yaw = tf.transformations.euler_from_quaternion([r_quat[0], r_quat[1], r_quat[2], r_quat[3]])

			xt = t_pos[0] - r_pos[0]
			yt = t_pos[1] - r_pos[1]
			x = xt * cos(-yaw) - yt * sin(-yaw)
			y = xt * sin(-yaw) + yt * cos(-yaw)
			z = 0

			if x > gridTotal or y > gridTotal or -x > gridTotal or -y > gridTotal:
				print "Warning: Tag detected beyond the range of the model being created"
				return

			yoffset = ((y - (y % gridResolution)) + gridSize) / gridResolution
			xoffset = ((x - (x % gridResolution)) + gridSize) / gridResolution
			cellIndex = int((gridTotal * 2 * yoffset) + xoffset)

			#update freq-specific model

			n = i[3][cellIndex]
			mean = i[4][cellIndex]
			sd = i[5][cellIndex]

			n, mean, m2 = recursiveVar(rssi, n, mean, sd * sd)

			i[3][cellIndex] = n
			i[4][cellIndex] = mean
			i[5][cellIndex] = sqrt(m2)

			#update combined model

			n = model[0][3][cellIndex]
			mean = model[0][4][cellIndex]
			sd = model[0][5][cellIndex]

			n, mean, m2 = recursiveVar(rssi, n, mean, sd * sd)

			model[0][3][cellIndex] = n
			model[0][4][cellIndex] = mean
			model[0][5][cellIndex] = sqrt(m2)

			#update mean
			#oldMean = i[4][cellIndex]
			#i[4][cellIndex] = ((i[4][cellIndex] * i[3][cellIndex]) + rssi) / (i[3][cellIndex] + 1)
			#model[0][4][cellIndex] = ((model[0][4][cellIndex] * model[0][3][cellIndex]) + rssi) / (model[0][3][cellIndex] + 1)

			#Increment no of detections
			#i[3][cellIndex] = i[3][cellIndex] + 1
			#model[0][3][cellIndex] = model[0][3][cellIndex] + 1

			#todo: add standard dev
			#i[5][cellIndex] = sqrt(recursiveVar(i[4][cellIndex], oldMean, rssi, i[5][cellIndex], i[3][cellIndex] - 1))
			#model[0][5][cellIndex] = sqrt(recursiveVar(model[0][4][cellIndex], oldMean, rssi, model[0][5][cellIndex], model[0][3][cellIndex] - 1))

			#good approximation for mapping rssi to 0-100 scale
			display_mean = (i[4][cellIndex] * -2) - 60
			display_combinedMean = (model[0][4][cellIndex] * -2) - 60

			i[2].data[cellIndex] = display_mean
			model[0][2].data[cellIndex] = display_combinedMean
			
			i[0].publish(i[2])
			model[0][0].publish(model[0][2])

#def recursiveVar(xnp,xn,x,vn,n):
#	xnp = int(xnp)
#	xn = int(xn)
#	x = int(x)
#	vn = int(vn)
#	n = int(n)
#	print xnp, xn, x, vn, n
#       vnp= vn + pow(xn, 2) - pow(xnp, 2) + ((pow(x, 2) - vn - pow(xn, 2)) / (n + 1))
#	#print vnp
#       return vnp

def recursiveVar(val, n, mean, m2):
	n += 1
	delta = val - mean
	mean += delta/n
	m2 += delta * (val - mean)

	return n, mean, m2
=======
def updateMean(m,cellIndex,rssi,n):
    oldMean = m[4][cellIndex]
    newMean = ((oldMean * n) + rssi) / (n + 1)
    m[4][cellIndex] = newMean
    return (oldMean,newMean)

>>>>>>> bcebe065b9d9cf1a7bd84309e2da16d7ae07ac92

def updateStd(m, cellIndex, newMean, oldMean, rssi, n):
    vn = pow(m[5][cellIndex], 2)

    try:
        vnp = recursiveVar(newMean, oldMean, rssi, vn, n)
        stdNew = sqrt(vnp)
    except ValueError:
        print str(vnp)+ ": "+ str(newMean) + " " + str(oldMean) + " " + str(rssi) + " " + str(vn) + " " + str(n)
        stdNew = 0
    m[5][cellIndex] = stdNew

<<<<<<< HEAD
	for i in xrange((gridTotal * 2) * (gridTotal * 2)):
		detections.append(0)
		mean.append(0.0)
		std.append(0.0)
=======
>>>>>>> bcebe065b9d9cf1a7bd84309e2da16d7ae07ac92

def tagCallback(data):
    global tfListener
    data = str(data)
    data = data.split(":")
    tagID = data[2]
    freq = data[5]
    rssi = int(data[3])
    tx = 3000
    robotTFName="/base_link"
    tagTFName="/rfid/tags/" + tagID
    globalTFName="/map"

    if not tagID in tagIDs:
        return
    # if not tfListener.frameExists(robotTFName):
    #     print "Unable to find tf frame for base link"
    #     return
    # if not tfListener.frameExists(globalTFName):
    #     print "Unable to find tf frame for map"
    #     return
    # if not tfListener.frameExists(tagTFName):
    #     print "Unable to find tf frame for rfid tag: " + tagIDs[0]
    #     return

    now = rospy.Time(0)
    tfListener.waitForTransform(robotTFName, tagTFName, now, rospy.Duration(5.0))
    rel_pose, rel_quat = tfListener.lookupTransform(robotTFName, tagTFName, now)
    rel_x = rel_pose[0]
    rel_y = rel_pose[1]
    (rel_rol, rel_pitch, rel_yaw) = tf.transformations.euler_from_quaternion(rel_quat)

    foundFrequency = False

    for i in model:
        if i[1] == freq:
            foundFrequency = True

    if foundFrequency == False:
        createModel(freq)

    for i in model:
        if i[1] == freq:
            #roll, pitch, yaw = tf.transformations.euler_from_quaternion([r_quat[0], r_quat[1], r_quat[2], r_quat[3]])

            #xt = t_pos[0] - r_pos[0]
            #yt = t_pos[1] - r_pos[1]
            #x = xt * cos(-yaw) - yt * sin(-yaw)
            #y = xt * sin(-yaw) + yt * cos(-yaw)
            #z = 0
            x=rel_x
            y=rel_y


            if x > gridTotal or y > gridTotal or -x > gridTotal or -y > gridTotal:
                print "Warning: Tag detected beyond the range of the model being created"
                return

            yoffset = ((y - (y % gridResolution)) + gridSize) / gridResolution
            xoffset = ((x - (x % gridResolution)) + gridSize) / gridResolution
            cellIndex = int((gridTotal * 2 * yoffset) + xoffset)

            if cellIndex>len(i[3])-1:
                print "Warning: Tag detected beyond the range of the model being created"
                return

            #update mean
            n = i[3][cellIndex]
            (oldMean, newMean)     = updateMean(i, cellIndex, rssi, n)
            #idem accumulated
            nAc = model[0][3][cellIndex]
            (oldMeanAc, newMeanAc) = updateMean(model[0], cellIndex, rssi, nAc)


            #update std dev
            updateStd(i,cellIndex,newMean,oldMean,rssi,n)
            updateStd(model[0], cellIndex,newMeanAc,oldMeanAc,rssi,nAc)

            # Increment no of detections
            i[3][cellIndex] = i[3][cellIndex] + 1
            model[0][3][cellIndex] = model[0][3][cellIndex] + 1

            #good approximation for mapping rssi to 0-100 scale
            mean = (i[4][cellIndex] * -2) - 60
            combinedMean = (model[0][4][cellIndex] * -2) - 60

            i[2].data[cellIndex] = mean
            model[0][2].data[cellIndex] = combinedMean

            i[0].publish(i[2])
            model[0][0].publish(model[0][2])


def recursiveVar(xnp,xn,x,vn,n):
    #http://johnthemathguy.blogspot.co.uk/2012/08/deviant-ways-to-compute-deviation.html
    if n>0:
        vnp = ((n-1)*vn/n) + (pow(xn-x, 2) / (n + 1))
    else:
        vnp=0
    #vnp= vn + pow(xn, 2) - pow(xnp, 2) + ((pow(x, 2) - vn - pow(xn, 2)) / (n + 1))
    if vnp<0:
        print "warning!"

    return vnp

def createModel(freq):
    global model,tfListener
    map = createMap()
    detections = []
    mean = []
    std = []
    tfListener=tf.TransformListener()
    for i in xrange((gridTotal * 2) * (gridTotal * 2)):
        detections.append(0)
        mean.append(0)
        std.append(0)

    pub = rospy.Publisher("rfid/sensor_model/" + str(freq), OccupancyGrid, queue_size=10)

    newFreq = [pub, freq, map, detections, mean, std]
    model.append(newFreq)

def createMap():
    map = OccupancyGrid()
    map.header.frame_id = "/base_link"
    map.info.resolution = gridResolution
    map.info.width = gridTotal * 2
    map.info.height = gridTotal * 2
    map.info.origin.position.x = -gridSize
    map.info.origin.position.y = -gridSize
    map.info.origin.position.z = 0
    map.info.origin.orientation.w = 1
    map.info.origin.orientation.x = 0
    map.info.origin.orientation.y = 0
    map.info.origin.orientation.z = 0
    map.data = []
    for i in xrange(0, (gridTotal * 2) * (gridTotal * 2)):
        map.data.append(-1)
    return map

def recoverModel():

    fname = "models/" + str(transmissionPower) + ".p"

    if os.path.isfile(fname):
        model = pickle.load(open(fname, "rb"))

    for i in model:

        i[0] = rospy.Publisher("rfid/sensor_model/" + str(freq), OccupancyGrid, queue_size=10)

def dumpModel():

    fname = "" + str(transmissionPower) + ".p"

    for i in model:
        i[0] = ""

    pickle.dump(model, open(fname, "wb"))

def main():

    global tfListener, model

    args = sys.argv
    del args[0]

    if len(args) == 0:
        print "Error: No tags to build model from"
        return

    rospy.init_node("buildModel")

    if "-a" in args:
        recoverModel()
        args = args.remove("-a")
    else:
        createModel("combined")

    for i in args:
        tagIDs.append(i)

    tfListener = tf.TransformListener()
    rfidSub = rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

    rospy.spin()

    dumpModel()

if __name__ == "__main__":
    main()
