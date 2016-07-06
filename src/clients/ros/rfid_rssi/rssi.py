import rospy
import Queue
import threading
from std_msgs.msg import String
from tf import TransformListener

class Frequency:
	frequency = ""
	rssi = []
	phase = []
	map = []

	def __init__(self):

		map = [[0] * 100] * 100

class Tag:
	id = ""
	frequencies = []

tagList = []
queue = Queue.Queue()

class controlThread(threading.Thread):
	def __init__(self, queue):

		threading.Thread.__init__(self)

		self.threadRunning = True
		self.queue = queue

	def run(self):
		while self.threadRunning == True:
			try:
				data = self.queue.get(False)
				if data == "EXIT":
					self.programRunning = False
				else:
					self.processInput(data)	
			except Queue.Empty:
				#self.degrade()
				pass

	def processInput(self, data):

		if not tf.frameExists("/base_link"):

			print "Error finding tf frame for base link"
			return

		elif not tf.frameExists("/odom_combined"):

			print "Error finding tf frame for odometry"
			return

		now = rospy.Time.now()
		tf.waitForTransform("/base_link", "/odom_combined", now, rospy.Duration(1.0))
		position, quat = tf.lookupTransform("/base_link", "/odom_combined", now)
		print position, quat

		data = str(data)
		data = data.split(":")

		tagExistsAlready = False
	
		for itemIndex in xrange(0, len(tagList)):
			if tagList[itemIndex].id == data[2]:
				tagExistsAlready = True
	
				frequencyExistsAlready = False
	
				for frequencyIndex in xrange(0, len(tagList[itemIndex].frequencies)):
					if tagList[itemIndex].frequencies[frequencyIndex].frequency == data[5]:
						frequencyExistsAlready = True
						
						tagList[itemIndex].frequencies[frequencyIndex].rssi.append(data[3])
						tagList[itemIndex].frequencies[frequencyIndex].phase.append(data[4])
	
						if len(tagList[itemIndex].frequencies[frequencyIndex].rssi) > 5:
							del tagList[itemIndex].frequencies[frequencyIndex].rssi[0]
							del tagList[itemIndex].frequencies[frequencyIndex].phase[0]
	
				if frequencyExistsAlready == False:
		
					f = Frequency()
					f.frequency == data[5]
					f.rssi.append(data[3])
					f.phase.append(data[4])
	
					tagList[itemIndex].frequencies.append(f)
	
		if tagExistsAlready == False:
			f = Frequency()
			f.frequency = data[5]
			f.rssi.append(data[3])
			f.phase.append(data[4])
		
			t = Tag()
			t.id = data[2]
			t.frequencies.append(f)

			tagList.append(t)

		for tag in xrange(0, len(tagList)):
			if tagList[tag].id == data[2]:
				for frequencyIndex in xrange(0, len(tagList[tag].frequencies)):
					if tagList[tag].frequencies[frequencyIndex].frequency == data[5]:
						pass

def tagCallback(data):

	queue.put("TAG:" + str(data))

if __name__ == '__main__':

	thread = controlThread(queue)
	thread.start()

	rospy.init_node('rssi')
	tf = TransformListener()
	rospy.Subscriber("rfid/rfid_detect", String, tagCallback)

	rospy.spin()

	queue.put("EXIT")
