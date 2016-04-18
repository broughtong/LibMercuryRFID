#!/usr/bin/env python

import sys
import ctypes
import time
import threading
import Queue

lib = ""
callbackList = ""
callbackHandler = ""

def callbackHandlerFunction(char_ptr):
	callbackString = ""

	try:

		for i in char_ptr:
			if i == "\0":
				break
			else:
				callbackString += i

	except:
		print "Indexing Error: Pointer to string conversion in wrapper\n"

	callbackList[0](callbackString)

	return 0

callback = ctypes.CFUNCTYPE(ctypes.c_byte, ctypes.POINTER(ctypes.c_char))(callbackHandlerFunction)

def init():

	global lib, callbackHandler, callbackList

	lib = ctypes.CDLL("libmercuryrfid.so.1")
	lib.RFIDinit(callback)

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

	readerID = lib.startReader(deviceURI)

	#lib.RFIDclose()
	#lib.getHopTime(readerID)
	#lib.setHopTime(readerID, 100)

	callbackList[readerID] = callbackFunction
	return readerID

def stopReader(readerID):

	global lib

	lib.stopReader(readerID)

def setPower(readerID, value):

	global lib

	time = lib.setPower(readerID, value)


def close():

	global lib, callbackList

	#lib.closeRFID()
	lib.RFIDclose()
	callbackList = {}
