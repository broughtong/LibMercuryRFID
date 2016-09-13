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
import scipy.ndimage



def plotAProbDetectCart(m,ax,X,Y,showAxis,minX,maxX,minY,maxY,title,sig):
    width = m[2].info.width
    height = m[2].info.height

    detections = np.array(m[3]).reshape(width, height).astype(float)


    try:
        f2 = str(float(m[1]) / 1000)  # won't work with average
    except ValueError:
        f2 = m[1]

    reescaledDetect=detections

    reescaledDetect = scipy.ndimage.filters.gaussian_filter(detections, sigma=sig,mode='reflect')
    maxDetect = np.nanmax(np.nanmax(reescaledDetect))

    reescaledDetect =(reescaledDetect + np.flipud(reescaledDetect))/2
    reescaledDetect =np.rot90(np.flipud(reescaledDetect),3)

    maxDetect = np.nanmax(np.nanmax(reescaledDetect))+1
    reescaledDetect = reescaledDetect / maxDetect

    # contours are *point* based plots, so convert our bound into point centers
    # cf = ax[i].contourf(x ,  y , z, levels=levels, cmap=cmap)
    #cf = ax.imshow(reescaledAVR, interpolation='nearest',cmap=cmap, norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1), origin='lower')

    cf = ax.pcolormesh(X, Y, reescaledDetect,
                          #norm=colors.LogNorm(vmin=0, vmax=1),
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
    cmap = plt.get_cmap('rainbow')

    i = 0
    X, Y = np.mgrid[slice(-(gridSize ), (gridSize ), gridResolution),
                    slice(-(gridSize ), (gridSize ), gridResolution)]

    minX=-3.0
    maxX=3.0
    minY=-3.0
    maxY=3.0
    sig = 0.45

    #for m in modelList[:-1:]:
    m=modelList[-1]
    figt, axt = plt.subplots(nrows=1, ncols=1)
    #fig2t, ax2t = plt.subplots(nrows=1, ncols=1)
    (cf, f)    = plotAProbDetectCart (m, axt,  X, Y, True, minX, maxX, minY, maxY, 'Spatial Model', sig)
    #(cf2t, f) = plotAModelPolar(m, ax2t, R, T, True, maxR, maxT, '',sig)

    figt.subplots_adjust(right=0.8)
    cbar_ax = figt.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = figt.colorbar(cf, cax=cbar_ax, label='Detect. prob.')
    # ticks=[1, 15, 31])
    # cbar.ax.set_yticklabels(['-75', '-50', '-25'])  # vertically oriented colorbar

    #plt.show()

    pdf = PdfPages('./figures/AvDetect_cart_' + str(f) + '.pdf')
    pdf.savefig(figt)
    pdf.close()

    # pdf = PdfPages('./figures/AvRSSI_pol_' + str(f) + '.pdf')
    # pdf.savefig(fig2t)
    # pdf.close()