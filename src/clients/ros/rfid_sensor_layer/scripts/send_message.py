import rospy

from rfid_node.msg import TagData
from rfid_node.msg import TagStats

rospy.init_node('sender')


tagSt = TagStats()

timestampHigh =340
timestampLow  =30409264
timest= ( timestampHigh<<32) | timestampLow
tagSt.timestamp.secs =  timest/1000
tagSt.timestamp.nsecs =  (timest%1000)*1000000

tagSt.rssi      = -57
tagSt.phase     = 146
tagSt.frequency = 923750
            
lastTag=TagData()
lastTag.ID = '300833B2DDD9014000000006'
lastTag.stats.append(tagSt)

tag_pub.publish(lastTag)

tag_pub = rospy.Publisher("lastTag", TagData,queue_size=10)

while not rospy.is_shutdown():
    lastTag.header.stamp = rospy.Time.now()
    lastTag.stats[0].timestamp = rospy.Time.now()

    tag_pub.publish(lastTag)

    rospy.sleep(5)
