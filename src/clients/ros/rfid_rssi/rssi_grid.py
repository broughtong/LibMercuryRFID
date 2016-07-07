import Queue
import threading
from std_msgs.msg import String
from tf import TransformListener

class Frequency:
	frequency = ""
	rssi = []
	phase = []

class Tag:
	id = ""
	frequencies = []

tagList = []
queue = Queue()

class controlThread(threading.Thread):
	def __init__(self, queue):
		self.queue = queue
		self.threadRunning = True
	def run(self):
		while self.threadRunning == True:
			
def callback(data):
	
	data = str(data)
	data = data.split(":")

	tagExistsAlready = False

	for itemIndex in xrange(0, len(tagList)):
		if tagList[itemIndex].id == data[2]:
			tagExistsAlready = True

			frequencyExistsAlready = False

			for frequencyIndex in xrange(0, len(tagList[itemIndex].frequencies)):
				if tagList[itemIndex].frequencies[frequencyIndex].frequency == data[2]:
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

	if tf.frameExists("/base_link") and tf.frameExists("/map"):
		t = tf.getLatestCommonTime("/base_link", "/map")
		position, quat = tf.lookupTransform("/base_link", "/map")
		print position, quat

