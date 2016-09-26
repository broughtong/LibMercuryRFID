import rospy
import pickle
import tf

from math import *
from std_msgs.msg import String
from nav_msgs.msg import *


gridSize = 9
gridResolution = 0.3

model = ""
worldMap = ""
lPub = ""
gPub = ""
tfListener = ""

def tagCallback(data):

	global tfListener

	if not tfListener.frameExists("/base_link"):
                print "Unable to find tf frame for base link"
                return
        if not tfListener.frameExists("/map"):
                print "Unable to find tf frame for map"
                return

	data = str(data).split(":")
	tagID = data[2]
	freq = data[5]
	rssi = int(data[3])
	tx = 3000

	if tagID != "300833B2DDD9014000000014":
		return 				

	index = -1

	modelW = model[0][2].info.width
	modelH = model[0][2].info.height

	for i in xrange(0, len(model)):
		if str(model[i][1]) == str(freq):
			index = i	

	total = 0 #ideally w*h, but may not be due to insufficient data

	dif = []
	max = 0

	for i in xrange(0, len(model[index][4])):
		if model[index][4][i] == 0:
			dif.append("---")
		else:
			total += 1
			dif.append(abs(float(model[index][4][i]) - rssi))
			if dif[i] > max:
				max = dif[i]
	if total == 0:
		print "Model is empty for freq"
		return

	newMax = 0
	for i in xrange(0, len(dif)):
		if dif[i] != "---":
			dif[i] = max - dif[i]
			if dif[i] > newMax:
				newMax = dif[i]
	runningTotal = 0
	for i in xrange(0, len(dif)):
		if dif[i] != "---":
			dif[i] = dif[i] / newMax
			runningTotal += dif[i]

	mean = runningTotal / total
	
	testTotal = 0
	for i in xrange(0, len(dif)):
		if dif[i] != "---":
			dif[i] = dif[i] - mean
			testTotal += dif[i]


	#dif now equals a probability change
	#print dif


	#mapProbability(dif, 9, 9)
	#adjustWorldMap()

	resolution = 0.3

	Map = OccupancyGrid()
        Map.header.frame_id = "/base_link"
        Map.info.resolution = 0.3
        Map.info.width = 60
        Map.info.height = 60
        Map.info.origin.position.x = -9
        Map.info.origin.position.y = -9
        Map.info.origin.position.z = 0
        Map.info.origin.orientation.w = 1
        Map.info.origin.orientation.x = 0
        Map.info.origin.orientation.y = 0
        Map.info.origin.orientation.z = 0
        Map.data = []
        for i in xrange(0, 3600):
		if dif[i] != "---":
			Map.data.append(int(dif[i] * 50))
		else:
			Map.data.append(-1)
	Map.data[0] = 0
	Map.data[1] = 100
	Map.data[2] = -20

	#print "###########################################################"
	#print Map.data

	pub.publish(Map)


	#pub.publish(worldMap)

"""def createMap():

	totalCells = (gridSize / gridResolution) * (gridSize / gridResolution) * 4

	

	map = []

def getModelIndex(x, y):

	gridTotal = gridSize * gridResolution

	if x > gridTotal or y > gridTotal or -x > gridTotal or -y > gridTotal:
		return -1

	yoffset = ((y - (y % gridResolution)) + gridSize) / gridResolution
	xoffset = ((x - (x % gridResolution)) + gridSize) / gridResolution

	index = int((gridTotal * 2 * yoffset) + xoffset)
	return index
"""

def mapProbability(dif, w, h):
######################################TODO###################
	global worldMap, tfListener

	now = rospy.Time(0)
	tfListener.waitForTransform("map", "base_link", now, rospy.Duration(4.0))
        r_pos, r_quat = tfListener.lookupTransform("/map", "/base_link", now)

	roll, pitch, yaw = tf.transformations.euler_from_quaternion([r_quat[0], r_quat[1], r_quat[2], r_quat[3]])

	for i in xrange(0, len(dif)):
		relx = (i % h) - (w / 2) + 0.05
		rely = floor(i / w) - (w / 2) + 0.05

		mapx = relx * cos(-yaw) - rely * sin(-yaw)
		mapy = relx * sin(-yaw) + rely * cos(-yaw)

		absx = round((-r_pos[0] - mapx) / worldMap.info.resolution) * worldMap.info.resolution
		absy = round((-r_pos[1] - mapy) / worldMap.info.resolution) * worldMap.info.resolution

		print absx, absy

		#absolute map-based coords, find corresponding cell, then update

		absx -= worldMap.info.origin.position.x
		absy -= worldMap.info.origin.position.y

		cell = int((absy * worldMap.info.width) + absx)

		if dif[i] != "---":
			#print "abc"
			#print worldMap.data[cell]
			#print cell
			newValue = float(dif[i]) * 100
			#worldMap.data[cell] += newValue
			#print worldMap.data[cell]

def adjustWorldMap():

	global worldMap

	min = 999

	for i in worldMap.data:
		if i < min:
			min = i
	
	sum = 0

	for i in xrange(0, len(worldMap.data)):
		worldMap.data[i] = worldMap.data[i] - min
		sum += worldMap.data[i]

	for i in xrange(0, len(worldMap.data)):
		worldMap.data[i] = worldMap.data[i] / sum

def createWorldMap(width, height, resolution):

	global worldMap

	totalCells = (width / resolution) * (height / resolution)

	val = 1. / totalCells

	worldMap = OccupancyGrid()
        worldMap.header.frame_id = "/map"
        worldMap.info.resolution = resolution
        worldMap.info.width = width / resolution
        worldMap.info.height = height / resolution
        worldMap.info.origin.position.x = -4
        worldMap.info.origin.position.y = -2
        worldMap.info.origin.position.z = 0
        worldMap.info.origin.orientation.w = 1
        worldMap.info.origin.orientation.x = 0
        worldMap.info.origin.orientation.y = 0
        worldMap.info.origin.orientation.z = 0
        worldMap.data = []
        for i in xrange(0, int(totalCells)):
                worldMap.data.append(val)

def main():

	global model, pub, worldMap, tfListener

	model = pickle.load(open("models/3000.p", "rb"))

	createWorldMap(10, 10, 0.5)

	rospy.init_node("localise")

	tfListener = tf.TransformListener()

	lPub = rospy.Publisher("rfid/localise-local", OccupancyGrid, queue_size=10)
	gPub = rospy.Publisher("rfid/localise-global", OccupancyGrid, queue_size=10)

	rfidSub = rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

	rospy.spin()

if __name__ == "__main__":

	main()
