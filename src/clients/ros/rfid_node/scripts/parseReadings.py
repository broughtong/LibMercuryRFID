#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from rfid_node.msg import TagReading


def tagCallback(lastTag):
    global tag_pub

    timest = lastTag.timestamp.secs * 1000 + lastTag.timestamp.nsecs / 1000000
    higher = (timest) >> 32
    lower = timest - ((higher >> 32) << 32)
    fields = ['0', lastTag.ID, str(lastTag.rssi), str(lastTag.phase), str(lastTag.frequency), str(higher), str(lower)]
    separator=':'
    tag_pub.publish(separator.join(fields))


if __name__ == "__main__":
    global tag_pub

    rospy.init_node("readingParser")

    # Get the ~private namespace parameters from command line or launch file.
    tagTopicName = rospy.get_param('~tagTopicName', 'lastTag')
    stringTopicName = rospy.get_param('~stringTopicName', 'rfid/rfid_detect')
    # Create publisher/subuscriber
    tag_pub=rospy.Publisher(stringTopicName, String,queue_size=0)
    rospy.Subscriber(tagTopicName, TagReading, tagCallback)

    #and wait
    rospy.spin()
