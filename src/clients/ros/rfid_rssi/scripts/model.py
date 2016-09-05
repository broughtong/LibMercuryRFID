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
        rospy.Subscriber('/rfid/rfid_detect', String, self.tagCallback)
        self.do = True
        self.tagDict=dict()
        rospy.spin()




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
            tagModel=TagModel.TagModel(tid,self.gridSize,self.resolution)
            self.tagDict[tid]=tagModel
        else:
            tagModel=self.tagDict[tid]


        now = rospy.Time()
        self.tf.waitForTransform("/base_link","/tag",  now, rospy.Duration(2.0))
        rel_pose, rel_quat = self.tf.lookupTransform("/base_link","/tag",  now)
        rel_x = rel_pose[0]
        rel_y = rel_pose[1]
        (rel_rol, rel_pitch, rel_yaw) = tf.transformations.euler_from_quaternion(rel_quat)
        rel_r   = math.sqrt(math.pow(rel_x,2)+math.pow(rel_y,2))
        rel_phi = math.atan2(rel_y, rel_x)
        # relative position of the tag respect to the antenna
        if self.do:
            self.do = False
            print "{:2.2f}".format(rel_x)+" "+"{:2.2f}".format(rel_y)+" "+"{:2.2f}".format(rel_yaw*180/3.141592)
            print "{:2.2f}".format(rel_r) + " " + "{:2.2f}".format(rel_phi * 180 / 3.141592)

        tagModel.updateCell(rel_x,rel_y,rssi_db,freq_khz,phase_deg)

# Main function.
if __name__ == '__main__':


    rospy.init_node('lalala')

    #rospy.loginfo("")


    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        lalala=la_clase()
    except rospy.ROSInterruptException:
        pass


