

#!/usr/bin/env python


# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
# Based on the code  Created by Martin J. Laubach on 2011-11-15
# https://github.com/mjl/particle_filter_demo/blob/master/particle_filter.py
# ------------------------------------------------------------------------

from __future__ import absolute_import

import time
import pickle
import random
import math
import bisect
import rospy
import tf
import os
import numpy as np
from math import *
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped, PoseArray, Pose, Point, Quaternion
#from rfid_node.msg import TagReading

PARTICLE_COUNT = 1000    # Total number of particles


positives = 0
negatives = 0
cumulative = 0
distances = []

# ------------------------------------------------------------------------
# Some utility functions

def add_noise(level, *coords):
	lst = list(coords)

	for x in xrange(0, len(lst)):
		lst[x] = lst[x] + random.uniform(-level, level)

	return tuple(lst)

#def add_noise(level, *coords):
#   return [x + random.uniform(-level, level) for x in coords]

def add_little_noise(*coords):
    return add_noise(0.02, *coords)

def add_some_noise(*coords):
    return add_noise(0.1, *coords)

def distance(px, py, mx, my):
    difx=px-mx
    dify = py - my
    dist=math.sqrt(difx*difx+dify*dify)
    return dist

# ------------------------------------------------------------------------
def compute_mean_point(particles):
    """
    Compute the mean for all particles that have a reasonably good weight.
    This is not part of the particle filter algorithm but rather an
    addition to show the "best belief" for current position.
    """

    m_x, m_y, m_count = 0, 0, 0
    for p in particles:
        m_count += p.w
        m_x += p.x * p.w
        m_y += p.y * p.w

    if m_count == 0:
        return -1, -1, False

    m_x /= m_count
    m_y /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if distance(p.x, p.y, m_x, m_y) < 1:
            m_count += 1

    return m_x, m_y, m_count > PARTICLE_COUNT * 0.999

# ------------------------------------------------------------------------
class WeightedDistribution(object):
    def __init__(self, state):
        accum = 0.0
        self.state = [p for p in state if p.w > 0]
        self.distribution = []
        for x in self.state:
            accum += x.w
            self.distribution.append(accum)

    def pick(self):
        try:
            return self.state[bisect.bisect_left(self.distribution, random.uniform(0, 1))]
        except IndexError:
            # Happens when all particles are improbable w=0
            return None

# ------------------------------------------------------------------------

#===================================================================================================

class SpatioFreqModel(object):

    def __init__(self):

        tid = '300833B2DDD9014000000014'
        self.gridResolution = 0.3
        self.gridSize = 9

	if self.gridSize % self.gridResolution > 0.0001:
		print "Error: grid size must be a multiple of the grid resolution"
		_ = raw_input()

	self.model = pickle.load(open("models/3000.p", "rb"))
        #numFreqs = len(self.model) - 1

    """def metric2cell(self,x):
        c=int((x+(self.gridSize/2))/self.gridResolution)
        if c>=math.ceil(self.gridSize / self.gridResolution):
            c = math.ceil(self.gridSize / self.gridResolution)-1
        if c< 0:
            c=0
        #print "distance " + str(x) + " corresponds to cell "+str(c)
        return c

    def freq2cell(self,f):
        try:
            findex = self.freqSet.index(f)###############################
        except ValueError:
            findex =0
            #rospy.loginfo("Frequency "+str(f)+" not in model")
        return findex
"""
    def getNearest(self,cx,cy,cf,m):
        maxCell=math.ceil(self.gridSize / self.resolution)-1
        for offset in range(1,maxCell):
            for ox in range(-maxCell,maxCell):
                for oy in range(-maxCell, maxCell):
                    if ((cx+ox)<=maxCell) and ((cy+oy)<=maxCell) and ((cx+ox)>=0) and ((cy+oy)>=0) :
                        if m[cx+ox,cy+oy,cf]!=float('nan'):
                            return (cx+ox,cy+oy)
        return 0,0


    def probability(self,rssi_db, x, y, freq_khz):

	if x > self.gridSize or y > self.gridSize or x < -self.gridSize or y < -self.gridSize:
		print "Warning: position outside of sensor model, consider creating a larger sensor model"
		return pow(10, -99)

	roundedx = x - (x % self.gridResolution)
	roundedy = y - (y % self.gridResolution)

	indexx = roundedx / self.gridResolution
	indexy = roundedy / self.gridResolution

	correctedx = indexx + (self.gridSize / self.gridResolution)
	correctedy = indexy + (self.gridSize / self.gridResolution)

	index = int(((self.gridSize / self.gridResolution) * 2 * correctedy) + correctedx)
	
	for i in self.model:
		if str(i[1]) == str(freq_khz):

			if i[4][index] == 0 or i[5][index] == 0:
				#sensor model blank for this location
				#the next if/else statement checks to see if the generic model contains data and uses that instead
				#this is sort of a hybrid technique, and the if else statement can be commented out to use purely the per-frequency probabilities
				if self.model[0][4][index] == 0:
					return pow(10, -99)
				else:
					av_rssi = self.model[0][4][index]
					std_rssi = self.model[0][5][index]

				#instead of defaulting to the generic model, this can be uncommented to ignore it
				#return pow(10, -99) 
			else:
				av_rssi = i[4][index]
				std_rssi = i[5][index]

	if std_rssi == 0:
		print "bad std"
		return pow(10, -99)

	rssi_dif = rssi_db - av_rssi
	prob = math.exp(-math.pow(rssi_dif, 2) / (2*std_rssi*std_rssi)) / (std_rssi * math.sqrt(2 * math.pi))

        return prob

# ==================================================================================================
class Particle(object):
    def __init__(self, x, y, heading=None, w=1, noisy=False):
        if heading is None:
            heading = random.uniform(0, 360)
        if noisy:
            x, y, heading = add_some_noise(x, y, heading)

        self.x = x
        self.y = y
        self.h = heading
        self.w = w

    def __repr__(self):
        return "(%f, %f, w=%f)" % (self.x, self.y, self.w)

    @property
    def xy(self):
        return self.x, self.y

    @property
    def xyh(self):
        return self.x, self.y, self.h

    @classmethod
    def create_random(cls, count, sizX,sizY):
        ans=[]
        for _ in range(0, count):
            rand_loc = random.uniform(-1, sizX-1), random.uniform(-.5, sizY-.5)
            ans.append(cls(*rand_loc))
        return ans

    def read_sensor(self, maze):
        """
        Find distance to nearest beacon.
        """
        return maze.distance_to_nearest_beacon(*self.xy)

    def advance_by(self, speed, checker=None, noisy=False):
        h = self.h
        if noisy:
            speed, h = add_little_noise(speed, h)
            h += random.uniform(-3, 3) # needs more noise to disperse better
        r = math.radians(h)
        dx = math.sin(r) * speed
        dy = math.cos(r) * speed
        if checker is None or checker(self, dx, dy):
            self.move_by(dx, dy)
            return True
        return False

    def move_by(self, x, y):
        self.x += x
        self.y += y


# ------------------------------------------------------------------------
class Object(Particle):
    speed = 0.0 # objects are *usually* static

    def __init__(self, sizeX,sizeY):
        rand_loc = random.uniform(0, sizeX), random.uniform(0, sizeY)
        super(Object, self).__init__(*rand_loc, heading=90)
        self.chose_random_direction()
        self.step_count = 0

    def chose_random_direction(self):
        heading = random.uniform(0, 360)
        self.h = heading


    def move(self):
        """
        Move the robot. Note that the movement is stochastic too.
        """
        while True:
            self.step_count += 1
            if self.advance_by(self.speed, noisy=True, checker=None):
                break
            # Bumped into something or too long in same direction,
            # chose random new direction
            self.chose_random_direction()

# ------------------------------------------------------------------------

class PartFilter():

    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self):
        # todo get map dimensions
        self.mapSizeX = 5
        self.mapSizeY = 3.5
        self.tagID='300833B2DDD9014000000014'
        self.tagTopicName='/rfid/rfid_detect'
        #self.tagTopicName = '/lastTag'
        self.robotTFName = '/base_link'
        self.globalTFName = '/map'
        self.tl = tf.TransformListener()
        self.tagModel=SpatioFreqModel()

        # initial distribution assigns each particle an equal probability
        self.particles = Particle.create_random(PARTICLE_COUNT, self.mapSizeX,self.mapSizeY)
        #self.mug = Object(self.mapSizeX,self.mapSizeY)

        self.pose_pub = rospy.Publisher('rfid/particles_f', PoseArray,queue_size=1000)

        #leave this for last line, otherwise it may start firing callbacks before we finish init
        rospy.Subscriber(self.tagTopicName, String, self.tagCallback)
        #rospy.Subscriber(self.tagTopicName, TagReading, self.tagCallback)
        rospy.spin()



    def getNewWeights(self, rssi_db, freq_khz, x, y):
        # particle pose is refered to global frame
        # let's ask transform listener its equivalent in robot coordinates.
        particlePose = PointStamped()
        particlePose.point.x = x
        particlePose.point.y = y
        particlePose.point.z = 0.0
        particlePose.header.frame_id = self.globalTFName

	#convert map coords to robot coords
        rel_pose = self.tl.transformPoint(self.robotTFName, particlePose)

        weights = self.tagModel.probability(rssi_db, rel_pose.point.x, rel_pose.point.y, freq_khz)
        return weights

    def parseTagData(self,data):
        rawD = data.data
        fields = rawD.split(':')
        tid = fields[1]
        rssi_db = float(fields[2])
        phase_deg = fields[3]
        freq_khz = fields[4]
        return (tid, rssi_db, freq_khz)


    def parseTagData2(self,data):
        # data is a TagReading message.
        # ID          tag EPC code
        # txP         transmitted power from reader
        # timestamp   reader timestamp
        # rssi        signal strength (dBm)
        # phase       wave phase  (degrees)
        # frequency   wave frequency (KHz)

        tid = data.ID
        rssi_db = data.rssi
        phase_deg = data.phase
        freq_khz = data.frequency
        return (tid, rssi_db, freq_khz)



    def publishPoses(self):
        poses = PoseArray()
        poses.header.frame_id = self.globalTFName
        poses.header.stamp = rospy.Time.now()

        for p in self.particles:
	        point = Point(p.x, p.y, 0)
       		direction = p.h
		quat = Quaternion(*tf.transformations.quaternion_from_euler(0, 0, direction))
		poses.poses.append(Pose(point, quat))

        self.pose_pub.publish(poses)

    def getRobotPose(self):
	now = rospy.Time(0)
	self.tl.waitForTransform("map", "base_link", now, rospy.Duration(4.0))
	r_pos, r_quat = self.tl.lookupTransform("/map", "/base_link", now)
	return r_pos

    def tagCallback(self,data):
	    global positives, negatives, cumulative, distances
            # Sensor data
            (id,rssi_db,freq_khz)= self.parseTagData(data)


            if id == self.tagID:

                # sensor reading
                for p in self.particles:
                    p.w=self.getNewWeights(rssi_db, freq_khz, p.x, p.y)


                # ---------- Try to find current best estimate for display ----------
                m_x, m_y, m_confident = compute_mean_point(self.particles)


		
                # ---------- Shuffle particles ----------
                new_particles = []

                # Normalise weights
                nu = sum(p.w for p in self.particles)
		#print "sum: " + str(nu)
		if nu:
                    for p in self.particles:
                        p.w = p.w / nu
		else:
			#pass
			print "no value"
			_ = raw_input()

                # create a weighted distribution, for fast picking
                dist = WeightedDistribution(self.particles)
                for _ in self.particles:
			p = dist.pick()
			if p is None:  # No pick b/c all totally improbable
				new_particle = Particle.create_random(1, self.mapSizeX,self.mapSizeY)[0]
				#for i in self.particles:
				#pass	
				#print "Improbable particles"
				_ = raw_input()				
                	else:
				deltax = p.x - -0.3
				deltay = p.y - 1.5
				tagToEst = sqrt((deltax * deltax) + (deltay * deltay))
				cumulative += tagToEst
				if p.y > 0.5 and p.y < 2.5 and p.x < 0.7 and p.x > -1.3:
					#print "S", p.x, p.y
					positives += 1
				else:
					#print "F", p.x, p.y
					negatives += 1                 
				#print "##S: " + str(positives) + " F: " + str(negatives) + " %: " + str((float(positives) / (positives + negatives)) * 100) + " C: " + str(cumulative)
                        	new_particle = Particle(p.x, p.y,
                                                #heading=self.mug.h,
                                                noisy=True)
		    	new_particles.append(new_particle)

        
		self.publishPoses()
  		
                self.particles = new_particles

                # ---------- Move things ----------
                #old_heading = self.mug.h
                #self.mug.move() # basically add noise...
                #d_h = self.mug.h - old_heading

                 # Move particles according to my belief of movement (this may
                # be different than the real movement, but it's all I got)
                for p in self.particles:
                    #p.h += d_h  # in case robot changed heading, swirl particle heading too
                    #p.advance_by(self.mug.speed)
                    p.advance_by(0)



# Main function.
if __name__ == '__main__':

    random.seed(time.time())

    rospy.init_node('particle_filter_f')

    #rospy.loginfo("")


    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        qad=PartFilter()
    except rospy.ROSInterruptException:
        pass

    print "##################################"
    print "Finished test"
    print "Cumulative distance to target: " + str(cumulative)
    print "Success: " + str(positives)
    print "Failure: " + str(negatives)
    print "%:       " + str((float(positives) / (positives + negatives)) * 100)

    with(open("distances", "w")) as f:
	for i in distances:
		f.write(str(i[0]) + "," + str(i[1]) + "\n")
