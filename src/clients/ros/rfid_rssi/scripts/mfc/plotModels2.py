#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import os
import math
import pickle
from nav_msgs.msg import  OccupancyGrid
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


# Main function.
if __name__ == '__main__':
    gridSize = 9
    gridResolution = 0.3
    transmissionPower = 3000
    fname = "models/" + str(transmissionPower) + ".p"
    fname = "scripts/models/" + str(transmissionPower) + ".p"
    file=(open(fname, "rb"))
    modelList = pickle.load(file)
    '''
    pickle contains a list of models (one per frequency plus a combined one)
    Each element m contains:
    m[0] gridpublisher: not used in the stored mode
    m[1] string: frequency in khz
    m[2] OccupancyGrid: data structure.
        m[2].data: grid
        m[2].info.resolution
        m[2].info.width
        m[2].info.height
    m[3] detections - 1d array containing number of detections per cell (same size as occ grid)
    m[4] mean       - 1d array containing mean rssi            per cell (same size as occ grid)
    m[5] std        - 1d array containing std rssi             per cell (same size as occ grid)
    '''

    for m in modelList:
                width=m[2].info.width
                height=m[2].info.height
                avRssi=np.array(m[3]).reshape(width,height)
                f2=float(m[1])/1000 # first wont work...

                numDetections = float(m[2]) / 1000
                print "rssi (" + str(f2) + ") " + str(numDetections) + " readings"
                # fig, axes = plt.subplots()
                # axes.imshow(data, interpolation='gaussian')
                # axes.set_title('gauzz')
                # plt.show()

                # contours are *point* based plots, so convert our bound into point centers
                # cf = ax[i].contourf(x ,  y , z, levels=levels, cmap=cmap)
                cf = ax[i].imshow(data, interpolation='gaussian', origin='lower')
                # fig.colorbar(cf, ax=ax[i])
                ax[i].set_title('Freq. ' + str(f2) + ' MHz')
                i = i + 1

    fig.colorbar(cf, ax=ax[i - 1])
    plt.show()