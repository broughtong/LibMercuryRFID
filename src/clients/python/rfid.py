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

# configures READING transmision power to value, given in 100*dBm (should be between 500 and 3000)
# TODO find out minimum step of power values
def setPower(readerID, value):

    global lib

    lib.setPower(readerID, value)


def close():

    global lib, callbackList

    #lib.closeRFID()
    lib.RFIDclose()
    callbackList = {}

# prints on screen current power configuration in 100*dBm
# TODO return power value
def getPower(readerID):

    global lib

    power = lib.getPower(readerID)

    return power


# newEPCdata is a string with hex char values of epc data
# epcMemoryBytes is size in bytes of EPCData memory bank (at leas 12 bytes). 
#                  It's half of the length of the string with values!!
def writeTag(readerId, newEpcData,epcMemoryBytes):

    global lib

    error=lib.writeTag(readerId, newEpcData,epcMemoryBytes)
    return error

# reenables reader reading
def reStartReader(readerID):

    global lib

    error=lib.reStartReader(readerID)
    return error

