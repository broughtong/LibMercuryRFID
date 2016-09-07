
import math
import numpy as np
from geometry_msgs.msg import Pose, Point, Quaternion
from nav_msgs.msg import OccupancyGrid, MapMetaData
import numpy as np
import rospy
import os

class FreqHandler():

    def __init__(self,tid,freq,gridSize,resolution):
        self.f=freq
        self.points=0

        self.tid=tid
        self.resolution=resolution
        self.gridSize=gridSize
        self.width = int(gridSize/resolution)+1
        self.height = int(gridSize/resolution)+1

        self.av_rssi=  np.zeros((self.width,self.height))
        self.std_rssi= np.zeros((self.width,self.height))
        self.av_phi =  np.zeros((self.width,self.height))
        self.std_phi = np.zeros((self.width,self.height))

        self.detect = np.zeros((self.width, self.height))

        rospy.Timer(rospy.Duration(60), self.save_callback)

    def save_callback(self,data):
        # In the end it should be something like ./300833B2DDD9014000000004/866900/av_rssi.csv

        fileDIR='./'+self.tid+ '/' + self.f

        if not os.path.exists(fileDIR):
            os.makedirs(fileDIR)

        fileURIprefix = fileDIR + '/'

        fileURI=fileURIprefix+'av_rssi'+'.csv'
        x=self.av_rssi
        x[self.detect == 0.0] = float('nan')
        np.savetxt(fileURI, x, delimiter=',',fmt='%.4e')

        fileURI = fileURIprefix + 'va_rssi' + '.csv'
        x = self.std_rssi
        x[self.detect == 0.0] = float('nan')
        np.savetxt(fileURI, x, delimiter=',')

        fileURI = fileURIprefix + 'av_phi' + '.csv'
        x = self.av_phi
        x[self.detect == 0.0] = float('nan')
        np.savetxt(fileURI, x, delimiter=',')

        fileURI = fileURIprefix + 'va_phi' + '.csv'
        x = self.std_phi
        x[self.detect == 0.0] = float('nan')
        np.savetxt(fileURI, x, delimiter=',')

        fileURI = fileURIprefix + 'det' + '.csv'
        x = self.detect
        x[self.detect == 0.0] = float('nan')
        np.savetxt(fileURI, x, delimiter=',')



    def metric2cell(self,x):
        c=int((x+(self.gridSize/2))/self.resolution)
        #print "distance " + str(x) + " corresponds to cell "+str(c)
        return c

    def metric2cell(self,x):
        c=int((x+(self.gridSize/2))/self.resolution)
        if c>=math.ceil(self.gridSize / self.resolution):
            rospy.logerr("Distance " + str(x) + " corresponds to inexisting cell " + str(c))
            c = math.ceil(self.gridSize / self.resolution)-1
        if c< 0:
            rospy.logerr("Distance " + str(x) + " corresponds to inexisting cell " + str(c))
            c=0

        return c

    def recursiveMean(self,xn,x,n):
        xnp=xn + ( (x- xn) / (n + 1) )
        #print "Mean value with " + str(n) + " points is " + str(xn)
        #print "Including value " + str(x) + " mean is " + str(xnp)

        return xnp

    def recursiveVar(self,xnp,xn,x,vn,n):
        vnp= vn + math.pow(xn, 2) - math.pow(xnp, 2) \
                   + ((math.pow(x, 2) - vn - math.pow(xn, 2)) / (n + 1))
        return vnp

    def addData(self,x, y, rssi_db, phase_deg):


        rssi_db = float(rssi_db)
        phase_deg = float(phase_deg)

        cx = self.metric2cell(x)
        cy = self.metric2cell(y)
        #rssi_pot=pow(10,rssi_db/10)
        n=self.detect[cx,cy]


        prev_av_rssi=self.av_rssi[cx,cy]
        prev_av_phi = self.av_phi[cx, cy]

        prev_std_rssi = self.std_rssi[cx, cy]
        prev_std_phi = self.std_phi[cx, cy]

        new_av_rssi = self.recursiveMean(prev_av_rssi,rssi_db,n)
        new_av_phi  = self.recursiveMean(prev_av_phi,phase_deg,n)

        new_std_rssi=self.recursiveVar(new_av_rssi,prev_av_rssi,rssi_db,prev_std_rssi,n)
        new_std_phi = self.recursiveVar(new_av_phi,prev_av_phi,phase_deg,prev_std_phi,n)

        self.std_rssi[cx, cy] = new_std_rssi
        self.std_phi[cx, cy] = new_std_phi

        self.av_rssi[cx, cy] = new_av_rssi
        self.av_phi[cx, cy] = new_av_phi

        self.detect[cx, cy] = n + 1

        #print 'Data ('+str(cx)+', '+str(cy)+', '+self.f+'): '+str(rssi_db)+' dB, '+str(rssi_pot)+' W, '+str(prev_av_rssi)+' W('+str(n)+'), '+str(new_av_rssi)+' W('+str(n+1)+'), '

    def to_message(self,mat):
        """ Return a nav_msgs/OccupancyGrid representation of this map. """

        grid_msg = OccupancyGrid()

        # Set up the header.
        grid_msg.header.stamp = rospy.Time.now()
        grid_msg.header.frame_id = '/base_link'

        grid_msg.info.resolution = self.resolution
        grid_msg.info.width = self.width
        grid_msg.info.height = self.height

        grid_msg.info.origin = Pose(Point(self.origin_x, self.origin_y, 0),
                                    Quaternion(0, 0, 0, 1))

        flat_grid = mat.reshape((mat.size,)) * 100
        grid_msg.data = list(np.round(flat_grid))
        return grid_msg
