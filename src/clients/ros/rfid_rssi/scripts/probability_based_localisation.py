import rospy
import pickle

from math import *

gridSize = 9
gridResolution = 0.3

model = ""
map = []

def tagCallback(data):

	data = str(data).split(":")
	tagID = data[2]
	freq = data[5]
	rssi = int(data[3])
	tx = 3000

	tagFound = False

	for i in map:
		if i[0] == tagID:
			tagFound = True

	if tagFound == False:
		map.append([tagID, []])

	for i in map:
		if i[0] == tagID:
			temp = i[1]
			
			max = -100

			for i in xrange(0, len(temp)):
				i = abs(i - rssi)
				if i > max:
					
				
				

def createMap():

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

def main():

	global model

	model = pickle.load(open("models/3000.p", "rb"))

	rospy.init_node("rfid/localise")

	rfidSub = rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

	rospy.spin()

if __name__ == "__main__":

	main()
