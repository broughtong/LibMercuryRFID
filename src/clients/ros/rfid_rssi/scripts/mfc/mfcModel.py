#!/usr/bin/env python


#test tag was 300833B2DDD9014000000014

import rospy
import tf
import math
from std_msgs.msg import String
import TagModel

class la_clase():

    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        self.tf = tf.TransformListener()


        self.gridSize=8
        self.resolution=0.3
        self.robotTFName="/base_link"
        self.tagTFPrefix="rfid/tags/"
        rospy.Subscriber('/rfid/rfid_detect', String, self.tagCallback)
        self.do = True
        self.tagDict=dict()
        rospy.spin()

    def getTagTFName(self,tid):
        return self.tagTFPrefix+tid



    def tagCallback(self, data):

        rawD = data.data
        fields = rawD.split(':')
        tid = fields[1]
        rssi_db = fields[2]
        phase_deg = fields[3]
        freq_khz = fields[4]

        tagModel=[]

        if tid not in self.tagDict:
            print "new tag "+tid
            self.do = True
            tagModel=TagModel.TagModel(tid,self.gridSize,self.resolution)
            self.tagDict[tid]=tagModel
        else:
            tagModel=self.tagDict[tid]


        now = rospy.Time()
        try:
            self.tf.waitForTransform(self.robotTFName,self.getTagTFName(tid),  now, rospy.Duration(2.0))
            rel_pose, rel_quat = self.tf.lookupTransform(self.robotTFName,self.getTagTFName(tid),  now)
            rel_x = rel_pose[0]
            rel_y = rel_pose[1]
            (rel_rol, rel_pitch, rel_yaw) = tf.transformations.euler_from_quaternion(rel_quat)
            rel_r   = math.sqrt(math.pow(rel_x,2)+math.pow(rel_y,2))
            rel_phi = math.atan2(rel_y, rel_x)
            # relative position of the tag respect to the antenna
            if self.do:
                self.do = False
                print "Pose:   "+"{:2.2f}".format(rel_x)+" m. "+"{:2.2f}".format(rel_y)+" m. "+"{:2.2f}".format(rel_yaw*180/3.141592)+" deg."
                print " polar: "+"{:2.2f}".format(rel_r) + " " + "{:2.2f}".format(rel_phi * 180 / 3.141592)+" deg."

            tagModel.updateCell(rel_x,rel_y,rssi_db,freq_khz,phase_deg)
        except tf.Exception:
            rospy.logerr("Detected tag ("+tid+") with no know location. Skipping")

# Main function.
if __name__ == '__main__':


    rospy.init_node('lalala')

    #rospy.loginfo("")


    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        lalala=la_clase()
    except rospy.ROSInterruptException:
        pass



