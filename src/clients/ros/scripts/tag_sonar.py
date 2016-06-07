#!/usr/bin/env python


import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Range
from geometry_msgs.msg import Pose
from rfid_node.msg import TagData
import math
import tf
import numpy as np
import sklearn 
from sklearn import linear_model
from threading import Lock
from distutils.version import StrictVersion

from datetime import datetime
import sys


def distance(poseA,poseB):
    '''
    :param poseA:
    :param poseB:
    :return: euclidean distance between poses
    '''
    dist = math.sqrt(pow(poseA.position.x -
                        poseB.position.x, 2) +
                    pow(poseA.position.y -
                        poseB.position.y, 2) +
                    pow(poseA.position.z -
                        poseB.position.z, 2))
    return dist

def getYawFromPose(aPose):
    '''
    :param aPose:
    :return: yaw angle of pose's orientation
    '''
    quatA = (
        aPose.orientation.x,
        aPose.orientation.y,
        aPose.orientation.z,
        aPose.orientation.w)
    euler = tf.transformations.euler_from_quaternion(quatA)
    # roll = euler[0]     pitch = euler[1]
    yawA = euler[2]
    return yawA

def yawBetweenPoses(poseA, poseB):
    '''
    :param poseA:
    :param poseB:
    :return: yaw angle difference yawB-yawA
    '''
    yawA=getYawFromPose(poseA)
    yawB = getYawFromPose(poseB)
    return yawB-yawA

def buildDiffVector(vector,diffSize):
    '''
    Calculates up to diffSize possible differences between elements of a vector
    :param vector: vector to be opperated
    :param diffSize: maximum size of differences vector (may be up to ( (vector.size-1) /2.0)*vector.size )
    :return:
    '''
    diffSize=min(diffSize,  ( (vector.size-1) /2.0)*vector.size )
    diffV = []
    for i in range(0, vector.size - 1):
        diffV = np.concatenate((diffV, vector[i + 1:] - vector[i]), axis=1)
        if diffV.size>diffSize:
            break
    return diffV[:diffSize]

def solvePhaseAmbiguity(X,y):
    X = X.reshape(-1, 1)
    y = y.reshape(-1, 1)

    # 1.- calculate average y at each X value
    xUnique = np.unique(X)
    yUnique = np.zeros(xUnique.size)
    for i in range(0, xUnique.size):
        yUnique[i] = np.mean(y[X == xUnique[i]])

    # 2.-roughly filter before looking for sign changes
    yUnique2 = np.zeros(xUnique.size)
    yUnique2[0] = yUnique[0]
    for i in range(1, yUnique.size):
        yUnique2[i] = 0.5 * yUnique[i - 1] + 0.5 * yUnique[i]
    yUnique = yUnique2

    #3.-find first derivate: negative values are descending trend
    yd = np.array([1])
    yd = np.append(yd, np.sign(yUnique[1:] - yUnique[:-1]))
    indexes = (yd == -1)

    #4.-select relevant points to infer new phase addition
    xSel = xUnique[indexes]
    ySel = yUnique[indexes]

    #5.-usinge these points, calculate extra phase vector
    prevY = ySel[0]
    extraPhase = 0
    phaseVector = np.zeros(ySel.size)
    for i in range(0, ySel.size):
        if ySel[i] > prevY:
            extraPhase -= math.pi
        prevY = ySel[i]
        phaseVector[i] = extraPhase


    #6.-apply these changes to the hole vector
    found = False
    finalY = np.zeros(y.size)
    for i in range(0, X.size):
        for j in range(0, xSel.size):
            if X[i] == xSel[j]:
                finalY[i] = y[i] + phaseVector[j]
                found = True
                break
        if not found:
            finalY[i] = y[i]
        found = False

    return finalY


# Node  class.
class TagLocatorNode():

    def ransacEstimation(self):
        '''
        Using tag stored readings, calls ransac to estimate radius
        :return: estimated radius
        '''
        R=-1
    
        numHip = min(self.numHipot, self.rssiVector.size)
        #sort both of them usind df as reference

        orderIndexs=np.argsort(self.freqVector)
        self.freqVector = self.freqVector[orderIndexs]
        self.phaseVector = self.phaseVector[orderIndexs]

        # create a  set of frequency and phase differences
        df = buildDiffVector(self.freqVector, numHip)
        dp = buildDiffVector(self.phaseVector, numHip)
        dpUnwrapped=solvePhaseAmbiguity(df,dp)

        df = df.reshape(-1, 1)
        dpUnwrapped = dpUnwrapped.reshape(-1, 1)

        # feed into RANSAC Regressor...
        mr = sklearn.linear_model.RANSACRegressor(sklearn.linear_model.LinearRegression())
        mr.fit(df, dpUnwrapped)
        R = -mr.estimator_.coef_ * self.C / (4.0 * math.pi)
        
        
        if 0:
            rospy.logerr("Using %d points",self.rssiVector.size)
            rospy.logerr("self.freqVector: %s",np.array_str(self.freqVector))
            rospy.logerr("self.phaseVector: %s",np.array_str(self.phaseVector))
            rospy.logerr("df: %s",np.array_str(df))
            rospy.logerr("dpUnwrapped: %s",np.array_str(dpUnwrapped))
            rospy.logerr("mr.estimator_.coef_ : %s",mr.estimator_.coef_ )
            rospy.logerr("R: %s",R )
            rospy.logerr("Deleting after ransac")

        return R

    def odomCallback(self,data):
        '''
        Each time robot moves, we need to clean tag data.
        Raises internal flag to request it
        :param data:
        :return:
        '''
        newPose=data.pose.pose
        if (distance(newPose,self.prevPose)>self.distThresh) or (yawBetweenPoses(newPose,self.prevPose)>self.angThresh) :
            self.dataLock.acquire()
            try:
                self.isNewPose = True
            finally:
                self.dataLock.release()

           # print(">>>>>>>>>>>>>>>>>>>>>>>>>  New pose")

        self.prevPose=newPose

    def tagCallback(self,data):
        '''
        Stores received tag data into buffer.
        Handles new position flag
        :param data:
        :return:
        '''

        if (data.ID.upper() == self.tagNAME.upper()):
            # some versions of RFID library return values in degs and KHz
            if 0:
                if data.stats[0].frequency<10e8:             
                    print("...newTag:", data.ID, data.stats[0].rssi, data.stats[0].phase*math.pi/180.0, data.stats[0].frequency*1000.0)
                else:
                    print("...newTag:", data.ID, data.stats[0].rssi, data.stats[0].phase, data.stats[0].frequency)
				
            if (not self.isNewPose):
                id = data.ID
                rssi = float(data.stats[0].rssi)
                
                # some versions of RFID library return values in degs and KHz
                phase = float(data.stats[0].phase)*math.pi/180.0
                freq = float(data.stats[0].frequency)*1000.0
                
                #add new entry to vectors
                self.dataLock.acquire()
                try:
                    self.rssiVector = np.append(self.rssiVector, rssi)
                    self.phaseVector = np.append(self.phaseVector, phase)
                    self.freqVector = np.append(self.freqVector, freq)
                    
                finally:
                    self.dataLock.release()

            else:
                # clear tag info and reset flag
                self.dataLock.acquire()
                try:                    
                    self.rssiVector = np.array([])
                    self.phaseVector = np.array([])
                    self.freqVector = np.array([])
                    self.isNewPose = False
                finally:
                    self.dataLock.release()

    def singlePub(self):
        self.dataLock.acquire()
        try:
            if self.rssiVector.size > self.minNumReadings:                   
                R = self.ransacEstimation()  
                #delete used values
                self.rssiVector = np.array([])
                self.phaseVector = np.array([])
                self.freqVector = np.array([])                
                self.rangeMsg.header.stamp = rospy.Time.now()
                self.rangeMsg.range = R
                # publish as a sonar value
                self.rangePub.publish( self.rangeMsg)

        finally:
            self.dataLock.release()

    
    def multiplePub(self):
         self.dataLock.acquire()
         try:            
            rssi=self.rssiVector
            phase=self.phaseVector
            freq=self.freqVector    
                # delete used data
            if freq.size > self.minNumReadings:
                rospy.logerr("Deleting after simple est")
                self.rssiVector = np.array([])
                self.phaseVector = np.array([])
                self.freqVector = np.array([])
                  
         finally:
            self.dataLock.release()
         
         if freq.size > self.minNumReadings:
             #sort by freq
             orderIndexs=np.argsort(freq)
             phase = phase[orderIndexs]
             freq = freq[orderIndexs]
             
             #get average phase for each frequency... 
             freqUnique = np.unique(freq)   
             phaseAV = np.zeros(freqUnique.size)   
                
             for i in range(0, freqUnique.size):
                phaseAV[i] = np.mean(phase[freq == freqUnique[i]])
                
             R0=self.C*phaseAV/(4*math.pi*freqUnique)
             Rinc=self.C/(2*freqUnique) 

             R=[]
             for r0i,rinc in np.nditer([R0,Rinc]):
                Ri = np.arange(r0i,self.MAX_DIST,step=rinc)
                R  = np.concatenate((R, Ri), axis=1)
             #rospy.logerr("About to average %d readings", R.size)
             self.rangeMsg.header.stamp = rospy.Time.now()
             self.rangeMsg.range = np.mean(R)
             # publish as a sonar value
             self.rangePub.publish(self.rangeMsg)

    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        # "Constants" or variables you should not change
        self.C=299792458.0  #m/s
        self.FREQ_STEP= 500000.0  # Hz
        self.FREQ_MIN = 860000000.0 # Hz
        self.FREQ_MAX = 868000000.0 # Hz
        self.MAX_DIST = 15.0  # ... to honor the Hebrew God, whose Ark this is."
        self.numCicles= math.ceil(15 / (self.C / (2 * self.FREQ_MAX)))

        self.minNumReadings = 50 # minimun number of readings before publishing
        self.mode='diff' # 'diff' == use ransac and phase differences, 'mult' == multiple solutions based on phases

        if StrictVersion(sklearn.__version__)<=StrictVersion('0.16'):
            rospy.logerr("RANSAC is not on your python scikit package. You need version >=0.17. See http://scikit-learn.org/stable/install.html")


        # Get the ~private namespace parameters from command line or launch file.
        self.tsample = float(rospy.get_param('~tsample', '0.01'))
        self.tagTopicName = rospy.get_param('~tagTopicName', 'lastTag')
        self.odomTopicName = rospy.get_param('~odomTopicName', '/odom')
        self.rangeTopicName = rospy.get_param('~rangeTopicName', '/sonarRFID')
        self.distThresh = float(rospy.get_param('~distThresh', '0.1'))
        self.angThresh = float(rospy.get_param('~angThresh', '0.1'))
        self.numHipot = int(rospy.get_param('~numHipot', '1000'))
        try:
            self.tagNAME = rospy.get_param('~tagNAME')
        except KeyError:
            rospy.logerr("No tracking tag provided, using default!!!!")
            self.tagNAME ='390100010000000000000014'

        #init previous pose to a 0 value
        self.prevPose=Pose()
        self.prevPose.position.x=self.prevPose.position.y=self.prevPose.position.z=0
        quaternion = tf.transformations.quaternion_from_euler(0,0,0)
        self.prevPose.orientation.x = quaternion[0]
        self.prevPose.orientation.y = quaternion[1]
        self.prevPose.orientation.z = quaternion[2]
        self.prevPose.orientation.w = quaternion[3]

        # init read/write locks
        self.dataLock = Lock()

        #be ready to add new poses
        self.dataLock.acquire()
        try:
            self.rssiVector = np.array([])
            self.phaseVector = np.array([])
            self.freqVector = np.array([])
            self.isNewPose = False
        finally:
            self.dataLock.release()

        # Create subscribers
        rospy.Subscriber(self.tagTopicName, TagData, self.tagCallback)
        rospy.Subscriber(self.odomTopicName, Odometry, self.odomCallback)

        # Create publisher
        self.rangePub=rospy.Publisher(self.rangeTopicName, Range,queue_size=0)

        # Main while loop.
        r = rospy.Rate(1/self.tsample)

        self.rangeMsg = Range()
        self.rangeMsg.radiation_type=Range.INFRARED
        self.rangeMsg.min_range= 0#self.C/(2.0*self.FREQ_MIN)
        self.rangeMsg.max_range = self.MAX_DIST
        self.rangeMsg.field_of_view = math.pi
        self.rangeMsg.header.frame_id = "sonar_"+self.tagNAME

        while not rospy.is_shutdown():
            if not self.isNewPose:  
                if self.mode=='diff':
                    self.singlePub()
                elif self.mode=='mult':
                    self.multiplePub()
                    
                # Sleep for a while after publishing new messages
            r.sleep()




# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('taglocator_node')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        tln = TagLocatorNode()
    except rospy.ROSInterruptException: pass
