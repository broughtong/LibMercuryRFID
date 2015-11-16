#!/usr/bin/env python

import rospy
import threading
import time

from std_msgs.msg import String
from ctypes import *
from Queue import *

lib = CDLL('libmerc/rfid.so')
qcom = Queue()
qcomExit = Queue()

values = {};
runningAvg = 0
avgList = []
avgNo = 100

class com(threading.Thread):
	def run(self):
		while True:
			try:
				i = qcomExit.get(False)
				break
			except:
				pass
			try:
				i = qcom.get(False)
				pub.publish(i)
			except:
				time.sleep(0.05)

class Test(object):
	def __init__(self):
		self.callback = CFUNCTYPE(c_byte, POINTER(POINTER(c_char)))(self.pyfoo)
	def pyfoo(self, char_ptr_ptr):
		buf = ""
		rssi = ""
		for i in char_ptr_ptr[0]:
			if i == "\0":
				break
			else:
				buf += i
		for i in char_ptr_ptr[1]:
			if i == "\0":
				break
			else:
				rssi += i

		if buf in values:
			if len(values[buf]) < avgNo:
				values[buf].append(int(rssi))
			else:
				for i in xrange(0, avgNo - 1):
					values[buf][i] = values[buf][i + 1]
				values[buf][avgNo - 1] = rssi
		else:
			values[buf] = []
			values[buf].append(rssi)

		print values

		total = 0
		for i in values[buf]:
			total += int(i)
		runningAvg = int(total / len(values[buf]))

		print avgList
		print runningAvg

		msg = "TAG: " + buf + " RSSI: " + rssi + "dB" + " Immediate Average RSSI (x" + str(avgNo) + "): " + str(runningAvg) + "dB"
		qcom.put(msg)
		return 0

t = Test()
_ = lib.run(t.callback)

a = com()
a.start()

rospy.init_node("rfid_detect")
pub = rospy.Publisher("rfid/rfid_detect", String, queue_size=100)
rospy.spin()
qcomExit.put("exit")
lib.close()
