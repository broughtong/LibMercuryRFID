#!/usr/bin/env python

import sys
import ctypes
import time
import threading
import Queue

lib = ""
callbackList = ""
callbackHandler = ""

class CallbackHandler(object):

	def __init__(self):
		super(CallbackHandler, self).__init__()
		self.callback = ctypes.CFUNCTYPE(ctypes.c_byte, ctypes.POINTER(ctypes.c_char))(self.callbackHandler)

	def callbackHandler(self, char_ptr):

		tagString = ""

		try:
			for i in char_ptr:
				if i == "\0":
					break
				else:
					tagString += i
		except:
			print "Indexing Error: Pointer To String Conversion In Wrapper\n"

		callbackList[0](tagString)

		return 0

def init():

	global lib, callbackHandler, callbackList

	lib = ctypes.CDLL("libmercuryrfid.so.1")

	callbackHandler = CallbackHandler()

	callbackList = {}

def getHopTime(readerID):

	global lib

	time = lib.getHopTime(readerID)

	return time

def setHopTime(readerID, newHopTime):

	global lib

	lib.setHopTime(readerID, newHopTime)

def startReader(deviceURI, callbackFunction):

	global lib, callbackList, callbackHandler

	readerID = lib.startReader(deviceURI, callbackHandler.callback)

	lib.RFIDinit()
	#lib.RFIDclose()
	#lib.getHopTime(readerID)
	#lib.setHopTime(readerID, 100)

	callbackList[readerID] = callbackFunction
	return readerID

def stopReader(readerID):

	global lib

	lib.stopReader(readerID)

def close():

	global lib, callbackList

	#lib.closeRFID()
	lib.RFIDclose()
	callbackList = {}
