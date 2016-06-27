import rospy
from std_msgs.msg import String

def callback(data):
	
	print "Rssi: " + str(data)

if __name__ == '__main__':
	
	rospy.init_node('rssi')
	rospy.Subscriber("rfid/rfid_detect", String, callback)
	rospy.spin()
