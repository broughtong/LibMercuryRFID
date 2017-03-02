#!/usr/bin/env python

from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import matplotlib.pyplot as plt
import math
import pickle

import matplotlib.colors as colors
import os
from nav_msgs.msg import  OccupancyGrid
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator




def plotAModelCart(m,ax,X,Y,showAxis,minX,maxX,minY,maxY,title,sig):
    width = m[2].info.width
    height = m[2].info.height
    realMin=-76.0
    realMax=-27.0

    avRssi = np.array(m[4]).reshape(width, height)
    detections = np.array(m[3]).reshape(width, height)

    avRssi = avRssi.astype(float)

    avRssi[detections == 0] = -76

    try:
        f2 = str(float(m[1]) / 1000)  # won't work with average
    except ValueError:
        f2 = m[1]


    import scipy.ndimage
    reescaledAVR = scipy.ndimage.filters.gaussian_filter(avRssi, sigma=sig,mode='reflect')

    reescaledAVR =(reescaledAVR + np.flipud(reescaledAVR))/2
    reescaledAVR = reescaledAVR- (realMin) + 1
    reescaledAVR =np.rot90(np.flipud(reescaledAVR),3)
    #reescaledAVR[detections == 0] = float('nan')


    # contours are *point* based plots, so convert our bound into point centers
    # cf = ax[i].contourf(x ,  y , z, levels=levels, cmap=cmap)
    #cf = ax.imshow(reescaledAVR, interpolation='nearest',cmap=cmap, norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1), origin='lower')

    cf = ax.pcolormesh(X, Y, reescaledAVR,
                          norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1),
                          cmap=cmap,shading='none')
    ax.plot(0,0,"g>",markersize=8)

    ax.get_xaxis().set_visible(showAxis)
    ax.get_yaxis().set_visible(showAxis)
    ax.set_xlim((minX, maxX))
    ax.set_ylim((minY, maxY))
    ax.set_aspect('equal')
    ax.set_xlabel('X (m.)')
    ax.set_ylabel('Y (m.)')


    if title =='':
        ax.set_title(str(f2) + ' MHz.',fontsize= 8)
    else:
        ax.set_title(title)

    return (cf,f2)

#/////////////////////////////
def plotAModelPolar(m,ax2,R,T,showAxis,maxR,maxT,title):
    width = m[2].info.width
    height = m[2].info.height
    avRssi = np.array(m[4]).reshape(width, height)
    detections = np.array(m[3]).reshape(width, height)

    avRssi = avRssi.astype(float)
    avRssi[detections == 0] = float('nan')

    try:
        f2 = str(float(m[1]) / 1000)  # won't work with average
    except ValueError:
        f2 = m[1]




    reescaledAVR = avRssi - (realMin) + 1

    reescaledAVR[detections == 0] = float('nan')

    #Zm = np.ma.masked_where(R>maxR, reescaledAVR)

    cf2 = ax2.pcolormesh(R, T, reescaledAVR,
                            norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1),
                            cmap=cmap,shading='gouraud')#, shading='none')


    # fig.colorbar(cf, ax=ax[i])
    ax2.get_xaxis().set_visible(showAxis)

    ax2.get_yaxis().set_visible(showAxis)
    ax2.set_xlabel('dist (m.)')
    ax2.set_ylabel('ang. (deg.)')

    ax2.set_xlim((0,maxR))
    ax2.set_ylim((-maxT, maxT))

    if title =='':
        ax2.set_title(str(f2) + ' MHz.',fontsize=8)
    else:
        ax2.set_title(title)
    # ..........................................................
    return (cf2,f2)

#/////////////////////////////


# Main function.
if __name__ == '__main__':
    gridSize = 9
    gridResolution = 0.3
    transmissionPower = 3000



    #print os.getcwd()
    try:
        fname = "../models/" + str(transmissionPower) + ".p"
        file = (open(fname, "rb"))
    except IOError:
        fname = "scripts/models/" + str(transmissionPower) + ".p"
        file = (open(fname, "rb"))

    modelList = pickle.load(file)
    modelList = sorted(modelList, key=lambda m: m[1])

    # pick the desired colormap, sensible levels, and define a normalization
    # instance which takes data values and translates those into levels.
    cmap = plt.get_cmap('OrRd')

    i = 0
    nc=1
    nr=1
    total = nc*nr
    fig, ax = plt.subplots(nrows=nr, ncols=nc)

    if total>1:
        ax = ax.reshape(total)

    X, Y = np.mgrid[slice(-(gridSize ), (gridSize ), gridResolution),
                    slice(-(gridSize ), (gridSize ), gridResolution)]

    minX=-3.0
    maxX=3.0
    minY=-3.0
    maxY=3.0
    sig = 0.45

    printSet=modelList[:-1:int(math.ceil(50/total))]
    printSet = modelList[10]

    if total>1:
        for g in xrange(0, total):
            (cf, f) = plotAModelCart(printSet[g], ax[g], X, Y, False, minX, maxX, minY, maxY, '',sig)
    else:
        (cf, f) = plotAModelCart(printSet, ax, X, Y, True, minX, maxX, minY, maxY, 'Spatial Model', sig)


    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar=fig.colorbar(cf, cax=cbar_ax, label='decibels',ticks = [1, 15, 31])
    cbar.ax.set_yticklabels(['-75','-50','-25'])  # vertically oriented colorbar

    plt.show()
