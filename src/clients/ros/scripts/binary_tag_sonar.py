#!/usr/bin/env python


import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Range
from geometry_msgs.msg import Pose
from rfid_node.msg import TagData
import math
import tf
import numpy as np
from sklearn import linear_model
from threading import Lock

from datetime import datetime
import sys


# Node  class.
class TagLocatorNode():

    def tagCallback(self,data):
        '''
        Stores received tag data into buffer.
        Handles new position flag
        :param data:
        :return:
        '''

        if (data.ID.upper() == self.tagNAME.upper()):
            self.singlePub(float("inf"))


    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        # "Constants" or variables you should not change
        self.C=299792458.0  #m/s
        self.FREQ_STEP= 500000.0  # Hz
        self.FREQ_MIN = 860000000.0 # Hz
        self.FREQ_MAX = 868000000.0 # Hz
        self.MAX_DIST = 15.0  # ... to honor the Hebrew God, whose Ark this is."

        # Get the ~private namespace parameters from command line or launch file.
        self.tsample = float(rospy.get_param('~tsample', '0.01'))
        self.tagTopicName = rospy.get_param('~tagTopicName', 'lastTag')
        self.rangeTopicName = rospy.get_param('~rangeTopicName', '/sonarRFID')
        try:
            self.tagNAME = rospy.get_param('~tagNAME')
        except KeyError:
            rospy.logerr("No tracking tag provided, using default!!!!")
            self.tagNAME ='390000010000000000000007'


        # Create subscribers
        rospy.Subscriber(self.tagTopicName, TagData, self.tagCallback)

        # Create publisher
        self.rangePub=rospy.Publisher(self.rangeTopicName, Range,queue_size=0)

        # Main while loop.
        r = rospy.Rate(1/self.tsample)

        self.rangeMsg = Range()
        self.rangeMsg.radiation_type=Range.INFRARED
        self.rangeMsg.min_range= self.C/(2.0*self.FREQ_MIN)
        self.rangeMsg.max_range = self.MAX_DIST
        self.rangeMsg.field_of_view = 2*math.pi
        self.rangeMsg.header.frame_id = "sonar_"+self.tagNAME

        while not rospy.is_shutdown():
            self.singlePub(float("-inf"))
            # Sleep for a while after publishing
            r.sleep()

    def singlePub(self,R):

        self.rangeMsg.header.stamp = rospy.Time.now()
        self.rangeMsg.range = R
        # publish as a sonar value
        self.rangePub.publish( self.rangeMsg)



# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('taglocator_node')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        tln = TagLocatorNode()
    except rospy.ROSInterruptException: pass
