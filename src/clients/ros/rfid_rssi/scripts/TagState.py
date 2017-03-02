import time

class TagRead():

	def __init__(self, id, rssi, phase, freq, position, orientation):

		self.id = id
		self.rssi = rssi
		self.phase = phase
		self.freq = freq
		self.position = position
		self.orientation = orientation
		self.timestamp = time.time()
		self.fade = 1.0

class TagState():

	def __init__(self, id):

		self.id = id

		self.tagReadObjects = []

	def append(self, tagRead):

		self.tagReadObjects.append(tagRead)

	def fade(seconds):

		for i in self.tagReadObjects:
			deltaTime = time.time() - i.timestamp
			if deltaTime >= seconds:
				i.fade = 0
			else:
				i.fade = deltaTime / seconds

		newList = []
		for i in self.tagReadObjects:
			if i.fade != 0:
				newList.append(i)
		self.tagReadObjects = newList
