#!/usr/bin/env python


# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
# Based on the code  Created by Martin J. Laubach on 2011-11-15
# https://github.com/mjl/particle_filter_demo/blob/master/particle_filter.py
# ------------------------------------------------------------------------

from __future__ import absolute_import

import random
import math
import bisect
import rospy
import tf
import os
import numpy as np
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped, PoseArray, Pose, Point, Quaternion

PARTICLE_COUNT = 2000    # Total number of particles


# ------------------------------------------------------------------------
# Some utility functions

def add_noise(level, *coords):
    return [x + random.uniform(-level, level) for x in coords]

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

    return m_x, m_y, m_count > PARTICLE_COUNT * 0.95

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
        self.resolution = 0.3
        self.gridSize = 8



        # should be something like ./300833B2DDD9014000000004/866900
        fileDIR = './' + tid
        files = os.listdir(fileDIR)
        self.buildFreqIndex(fileDIR,files)

        numCols = math.ceil(self.gridSize / self.resolution)
        numRows = math.ceil(self.gridSize / self.resolution)
        numFreqs = len(self.freqSet)

        self.av_rssi_model = np.zeros((numCols, numRows, numFreqs))
        self.va_rssi_model = np.zeros((numCols, numRows, numFreqs))

        for fileName in files:
            if 'av_rssi' in fileName:
                fileURIprefix = fileDIR + '/'
                fileURI = fileURIprefix + fileName
                data = np.loadtxt(fileURI, delimiter=',')

                f = fileName[0:6]
                findex = self.freq2cell(f)

                self.av_rssi_model[:, :, findex] = data
                doPrint = True

            if 'va_rssi' in fileName:
                fileURIprefix = fileDIR + '/'
                fileURI = fileURIprefix + fileName
                data = np.loadtxt(fileURI, delimiter=',')

                f = fileName[0:6]
                findex = self.freq2cell(f)

                self.va_rssi_model[:, :, findex] = data



    def buildFreqIndex(self,fileDIR,files):
        self.freqSet = list()
        for fileName in files:
            f = (fileName[0:6])
            if f not in self.freqSet:
                self.freqSet.append(f)
        self.freqSet.sort()

    def metric2cell(self,x):
        c=int((x+(self.gridSize/2))/self.resolution)
        #print "distance " + str(x) + " corresponds to cell "+str(c)
        return c

    def freq2cell(self,f):
        findex = self.freqSet.index(f)
        return findex

    def probability(self,rssi_db, x, y, freq_khz):
        cx= self.metric2cell(x)
        cy = self.metric2cell(y)
        cf = self.freq2cell(freq_khz)
        av_rssi = self.av_rssi_model[cx,cy,cf]
        va_rssi = self.va_rssi_model[cx, cy, cf]
        std_rssi = math.sqrt(va_rssi)

        rssi_dif=10*pow(float(rssi_db)/10) - av_rssi

        prob= math.exp( - math.pow(rssi_dif,2) / (2*va_rssi)  ) / (va_rssi * math.sqrt(2*math.pi) )



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
        rand_loc = random.uniform(0, sizX), random.uniform(0, sizY)
        return [cls(*rand_loc) for _ in range(0, count)]

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
    speed = 0.0 # objects are *usually* statice

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
        self.mapSizeX=8
        self.mapSizeY = 8
        self.tagID='300833B2DDD9014000000014'
        self.tagTopicName='/rfid/rfid_detect'
        self.robotTFName = '/base_link'
        self.globalTFName = '/map'
        self.tl = tf.TransformListener()
        self.tagModel=SpatioFreqModel()

        # initial distribution assigns each particle an equal probability
        self.particles = Particle.create_random(PARTICLE_COUNT, self.mapSizeX,self.mapSizeY)
        self.mug = Object(self.mapSizeX,self.mapSizeY)

        self.pose_pub = rospy.Publisher('particles', PoseArray)

        #leave this for last line, otherwise it may start firing callbacks before we finish init
        rospy.Subscriber(self.tagTopicName, String, self.tagCallback)




    def getNewWeights(self, rssi_db, freq_khz, x, y):
        # particle pose is refered to global frame
        # let's ask transform listener its equivalent in robot coordinates.
        particlePose = PointStamped()
        particlePose.point.x = x
        particlePose.point.y = y
        particlePose.point.z = 0.0
        particlePose.header.frame_id = self.globalTFName

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


        return (tid,rssi_db,freq_khz)

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


    def tagCallback(self,data):
            # Sensor data
            (id,rssi_db,freq_khz)= self.parseTagData(data)


            if id == self.tagID:
                # get robot position
                #(rob_x, rob_y, rob_yaw)=self.getLatestRobotPose()

                # sensor reading
                for p in self.particles:
                    p.w=self.getNewWeights(rssi_db, freq_khz, p.x, p.y)

                # ---------- Try to find current best estimate for display ----------
                m_x, m_y, m_confident = compute_mean_point(self.particles)


                # ---------- Shuffle particles ----------
                new_particles = []

                # Normalise weights
                nu = sum(p.w for p in self.particles)
                if nu:
                    for p in self.particles:
                        p.w = p.w / nu

                # create a weighted distribution, for fast picking
                dist = WeightedDistribution(self.particles)

                for _ in self.particles:
                    p = dist.pick()
                    if p is None:  # No pick b/c all totally improbable
                        new_particle = Particle.create_random(1, self.mapSizeX,self.mapSizeY)[0]
                    else:
                        new_particle = Particle(p.x, p.y,
                                                heading=self.mug.h,
                                                noisy=True)
                    new_particles.append(new_particle)

                particles = new_particles
                self.publishPoses()

                # ---------- Move things ----------
                old_heading = self.mug.h
                self.mug.move() # basically add noise...
                d_h = self.mug.h - old_heading

                # Move particles according to my belief of movement (this may
                # be different than the real movement, but it's all I got)
                for p in self.particles:
                    p.h += d_h  # in case robot changed heading, swirl particle heading too
                    p.advance_by(self.mug.speed)



# Main function.
if __name__ == '__main__':


    rospy.init_node('particle_filter')

    #rospy.loginfo("")


    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        qad=PartFilter()
    except rospy.ROSInterruptException:
        pass


