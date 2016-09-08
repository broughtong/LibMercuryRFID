#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import math
import pickle

import matplotlib.colors as colors
import os
from nav_msgs.msg import  OccupancyGrid
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


# Main function.
if __name__ == '__main__':
    gridSize = 9
    gridResolution = 0.3
    transmissionPower = 3000

    realMin=-76.0
    realMax=-27.0

    #print os.getcwd()
    try:
        fname = "../models/" + str(transmissionPower) + ".p"
        file = (open(fname, "rb"))
    except IOError:
        fname = "scripts/models/" + str(transmissionPower) + ".p"
        file = (open(fname, "rb"))

    modelList = pickle.load(file)

    # pick the desired colormap, sensible levels, and define a normalization
    # instance which takes data values and translates those into levels.
    cmap = plt.get_cmap('OrRd')

    i = 0
    fig, ax = plt.subplots(nrows=6, ncols=10)
    ax = ax.reshape(60)

    fig2, ax2 = plt.subplots(nrows=6, ncols=10)
    ax2 = ax2.reshape(60)


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

    maxAVrssiList=[]
    minAVrssiList = []
    allData=[]

    X, Y = np.mgrid[slice(-(gridSize ), (gridSize ), gridResolution),
                    slice(-(gridSize ), (gridSize ), gridResolution)]

    R, T = np.mgrid[slice(-(gridSize), (gridSize), gridResolution),
                    slice(-(gridSize), (gridSize), gridResolution)]

    for k in xrange(0,60):
        for j in xrange(0,60):
            x = X[k][j]
            y = Y[k][j]
            R[k][j]=math.sqrt(x*x+y*y)
            T[k][j]=math.atan2(y,x)-math.pi/2
    T.flat[T.flat<=(-math.pi)]=T.flat[T.flat<=(-math.pi)]+math.pi


    for m in sorted(modelList, key=lambda m: m[1]):
                width=m[2].info.width
                height=m[2].info.height
                avRssi    = np.array(m[4]).reshape(width,height)
                detections= np.array(m[3]).reshape(width, height)

                allData.append(m[4])

                avRssi=avRssi.astype(float)

                avRssi[detections==0]=float('nan')


                try:
                    f2=str(float(m[1])/1000 )# first wont work...
                except ValueError:
                    f2=m[1]


                numDetections = sum(sum(detections))
                print "rssi (" + f2 + ") " + str(numDetections) + " readings"
                minRssi=np.nanmin(avRssi)
                maxRssi=np.nanmax(avRssi)

                maxAVrssiList.append(maxRssi)
                minAVrssiList.append(minRssi)
                print "range "+ str(minRssi) + ", " + str(maxRssi)

                # fig, axes = plt.subplots()
                # axes.imshow(data, interpolation='gaussian')
                # axes.set_title('gauzz')
                # plt.show()

                # contours are *point* based plots, so convert our bound into point centers
                # cf = ax[i].contourf(x ,  y , z, levels=levels, cmap=cmap)
                #cf = ax[i].imshow(avRssi, interpolation='gaussian', origin='lower')

                reescaledAVR=avRssi-(realMin)+1
                #reescaledAVR=(reescaledAVR+ np.flipud(reescaledAVR))/2
                reescaledAVR[detections == 0] = float('nan')

                cf = ax[i].pcolormesh(X, Y, reescaledAVR,
                                   norm=colors.LogNorm(vmin=1, vmax=realMax-realMin+1),
                                   cmap=cmap,shading='gouraud')
                ax[i].get_xaxis().set_visible(False)
                ax[i].get_yaxis().set_visible(False)

                # fig.colorbar(cf, ax=ax[i])
                ax[i].set_title( str(f2) + ' MHz')

                #..........................................................
                cf2 = ax2[i].pcolormesh(R, T, reescaledAVR,
                                      norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1),
                                      cmap=cmap, shading='gouraud')

                # fig.colorbar(cf, ax=ax[i])
                ax2[i].set_title(str(f2) + ' MHz')
                #..........................................................

                i = i + 1

    minAVrssiList.sort()
    maxAVrssiList.sort()
    print "/////////////////////////////////////////"
    print "Global range " + str(minAVrssiList[0]) + ", " + str(maxAVrssiList[-1])

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(cf, cax=cbar_ax)

    plt.axis('off')

    #fig.colorbar(cf, ax=ax[i - 1])
    #plt.show()
#/////////////////////////////////////////////
    fig2.subplots_adjust(right=0.8)
    cbar_ax2 = fig2.add_axes([0.85, 0.15, 0.05, 0.7])
    fig2.colorbar(cf2, cax=cbar_ax2)

    #plt.axis('off')

    # fig.colorbar(cf, ax=ax[i - 1])
    plt.show()


    #//////////////////////////////////////




    # allData=np.array(allData).flat
    # allData=allData[allData!=float('nan')]
    #
    # allData = allData[allData <-9]
    #
    # plt.hist(allData)
    # plt.title("rssi Histogram")
    # plt.xlabel("Value")
    # plt.ylabel("Frequency")
    #
    # fig = plt.gcf()
    # plt.show()
