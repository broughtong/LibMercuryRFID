#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from rol_server.srv import findObject, findObjectRequest, findObjectResponse



# Node class.
class rol_client():

    def __init__(self):
        rospy.loginfo('Waiting for Server to be active')
        rospy.wait_for_service('rol_server')
        self.callService = rospy.ServiceProxy('rol_server', findObject)


        sleepTime = rospy.Duration(1, 0)

        self.op('list','objects')
        rospy.loginfo('................................................................................................')

        self.op('list', 'locations')

        rospy.loginfo('................................................................................................')


        self.op('list', 'sublocations')

        rospy.loginfo('................................................................................................')


        self.op('find', 'tape holder')

        rospy.loginfo('................................................................................................')


        self.op('accurate_find', 'tape holder')

        rospy.loginfo('................................................................................................')

        self.op('find', 'remote')

        rospy.loginfo('................................................................................................')

        self.op('accurate_find', 'tape holder')

        rospy.loginfo('................................................................................................')

    def op(self,action,payload):
        resp1 = self.callService(action, payload)
        if resp1.wasOk:
            rospy.loginfo('Request was correct.')
            rospy.loginfo(action+'('+payload+'): is (' + resp1.response + ')')
        else:
            rospy.loginfo('Request was incorrect')
            rospy.loginfo('error is (' + resp1.feedback + ')')


# Main function.
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('rol_client_node')

    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        rc = rol_client()
    except rospy.ROSInterruptException: pass
