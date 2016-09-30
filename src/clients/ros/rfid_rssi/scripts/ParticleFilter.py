import threading
import Queue

from TagState import *

class ParticleFilter(threading.Thread):
	
	def __init__(self, exitQueue):

		threading.Thread.__init__(self)

		self.exitQueue = exitQueue

		self.tagStates = []

	def run(self):

		try:
			msg = self.exitQueue.get(False)

			if msg == "exit":
				return

			else:

				foundTag = False

				for i in self.tagStates:
					if i.id == msg.id:
						foundTag = True
						i.append(msg)
				if foundTag == False:
					tagState = TagState(msg.id)
					tagState.append(msg)
					self.tagStates(tagState)

		except Queue.Empty:
			pass

		
