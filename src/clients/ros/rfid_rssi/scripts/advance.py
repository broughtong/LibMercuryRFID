#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from requests import post
import actionlib
from move_base_msgs.msg import MoveBaseAction
from move_base_msgs.msg import MoveBaseGoal

import json

import tf

import math
import random
import statistics
import numpy



rospy.init_node('move_ahead')
client = actionlib.SimpleActionClient('move_base',MoveBaseAction)

client.wait_for_server()

goal = MoveBaseGoal()
goal.target_pose.header.frame_id = "base_link"
goal.target_pose.header.stamp = rospy.Time.now()

goal = MoveBaseGoal()
goal.target_pose.header.frame_id = "base_link"
goal.target_pose.header.stamp = rospy.Time.now()
goal.target_pose.pose.position.x = 0.3
goal.target_pose.pose.position.y = 0
new_quaternion = tf.transformations.quaternion_from_euler(0,0,0.0)
goal.target_pose.pose.orientation.x = new_quaternion[0]
goal.target_pose.pose.orientation.y = new_quaternion[1]
goal.target_pose.pose.orientation.z = new_quaternion[2]
goal.target_pose.pose.orientation.w = new_quaternion[3]


client.wait_for_server()
client.send_goal(goal)
client.wait_for_result(rospy.Duration.from_sec(7.0))
rospy.spin()
