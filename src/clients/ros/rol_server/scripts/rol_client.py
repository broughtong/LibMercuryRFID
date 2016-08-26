#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from rol_server.srv import findObject, findObjectRequest, findObjectResponse



# Node class.
class rol_client():

    def __init__(self):
        rospy.loginfo('Waiting for Server to be active')
        rospy.wait_for_service('rol_server')
        self.callService = rospy.ServiceProxy('findObject', findObject)

        action  ='list' #'list','find','accurate_find'
        payload ='objects'
        resp1 =  self.callService(action,payload)



        rospy.spin()


# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('rol_client_node')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        rc = rol_client()
    except rospy.ROSInterruptException: pass
