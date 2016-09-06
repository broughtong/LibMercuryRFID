import rospy
import pickle
import sys
import tf

from std_msgs.msg import String
from nav_msgs.msg import *
from math import *

#Configurables - distances in meters
#gridSize = distance from robot to edge of map in all directions
#gridResolution = the cell size of the map
gridSize = 8
gridResolution = 0.5

#Globals
tagIDs = []
tfListener = ""
gridTotal = int(gridSize/gridResolution)
pub = rospy.Publisher("/rfid/ocmap", OccupancyGrid, queue_size=10)

def tagCallback(data):

	data = str(data)
	data = data.split(":")
	tagID = data[2]
	freq = data[5]
	rssi = data[3]
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
	tfListener.waitForTransform("map", "tag", now, rospy.Duration(4.0))
	t_pos, t_quat = tfListener.lookupTransform("/map", "/rfid/tags/" + tagID, now)

	roll, pitch, yaw = tf.transformations.euler_from_quaternion([r_quat[0], r_quat[1], r_quat[2], r_quat[3]])

	xt = t_pos[0] - r_pos[0]
	yt = t_pos[1] - r_pos[1]
	x = xt * cos(-yaw) - yt * sin(-yaw)
	y = xt * sin(-yaw) + yt * cos(-yaw)
	z = 0

	rssi = int(rssi)
	rssi = rssi * -2
	rssi = rssi - 60
	setMapValue(x, y, rssi)

	pub.publish(map)

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

def setMapValue(x, y, val):
	if x > gridTotal or y > gridTotal or -x > gridTotal or -y > gridTotal:
		return
	else:
		yoffset = ((y - (y % gridResolution)) + gridSize) / gridResolution
		xoffset = ((x - (x % gridResolution)) + gridSize) / gridResolution
		index = int((gridTotal * 2 * yoffset) + xoffset)

		if map.data[index] == -1:
			map.data[index] = val
		else:
			map.data[index] = (map.data[index] + val) / 2

def main():

	global tfListener
	
	args = sys.argv
	del args[0]

	if len(args) == 0:
		print "Error: No tags to build model from"
		return

	for i in args:
		tagIDs.append(i)

	rospy.init_node("buildModel")
	tfListener = tf.TransformListener()
	rfidSub = rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

	rospy.spin()
	
if __name__ == "__main__":
	main()