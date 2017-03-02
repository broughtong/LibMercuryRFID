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




def plotAModelCart(m,ax,X,Y,showAxis,minX,maxX,minY,maxY,title):
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

    numDetections = sum(sum(detections))
    print "rssi (" + f2 + ") " + str(numDetections) + " readings"
    minRssi = np.nanmin(avRssi)
    maxRssi = np.nanmax(avRssi)

    maxAVrssiList.append(maxRssi)
    minAVrssiList.append(minRssi)
    print "range " + str(minRssi) + ", " + str(maxRssi)



    reescaledAVR = avRssi - (realMin) + 1
    reescaledAVR =np.rot90(np.flipud(reescaledAVR),3)
    reescaledAVR[detections == 0] = float('nan')


    # contours are *point* based plots, so convert our bound into point centers
    # cf = ax[i].contourf(x ,  y , z, levels=levels, cmap=cmap)
    #cf = ax.imshow(reescaledAVR, interpolation='nearest',cmap=cmap, norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1), origin='lower')

    cf = ax.pcolormesh(X, Y, reescaledAVR,
                          norm=colors.LogNorm(vmin=1, vmax=realMax - realMin + 1),
                          cmap=cmap,shading='gouraud')
    ax.get_xaxis().set_visible(showAxis)
    ax.get_yaxis().set_visible(showAxis)
    ax.set_xlabel('X (m.)')
    ax.set_ylabel('Y (m.)')

    ax.set_xlim((minX, maxX))
    ax.set_ylim((minY, maxY))

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

    numDetections = sum(sum(detections))
    print "rssi (" + f2 + ") " + str(numDetections) + " readings"
    minRssi = np.nanmin(avRssi)
    maxRssi = np.nanmax(avRssi)

    maxAVrssiList.append(maxRssi)
    minAVrssiList.append(minRssi)
    print "range " + str(minRssi) + ", " + str(maxRssi)



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
    modelList = sorted(modelList, key=lambda m: m[1])

    # pick the desired colormap, sensible levels, and define a normalization
    # instance which takes data values and translates those into levels.
    cmap = plt.get_cmap('OrRd')

    i = 0
    fig, ax = plt.subplots(nrows=3, ncols=6)
    ax = ax.reshape(18)

    fig2, ax2 = plt.subplots(nrows=3, ncols=6)
    ax2 = ax2.reshape(18)

    figa, axa   = plt.subplots(nrows=1, ncols=1)
    fig2a, ax2a = plt.subplots(nrows=1, ncols=1)

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

    kmax,jmax=X.shape
    for k in xrange(0,jmax):
        for j in xrange(0,kmax):
            x = X[k][j]
            y = Y[k][j]
            R[k][j]=math.sqrt(x*x+y*y)
            T[k][j]=math.atan2(y,x)
            T[k][j] = math.degrees(T[k][j])
    T.flat[T.flat<=(-180)]=T.flat[T.flat<=(-180)]+180

    minX=-4.5
    maxX=5
    minY=-4.5
    maxY=4.5

    maxR=5.5
    maxT = 150
    save=False

    printSet= modelList[:-1:3]
    printSet.append(modelList[-2])

    for m in printSet:
        if i==18:
            break
        (cf,f) = plotAModelCart(m, ax[i], X, Y, False, minX,maxX,minY,maxY, '')
        (cf2,f)= plotAModelPolar(m, ax2[i], R, T, False,  maxR,maxT, '')
        allData.append(m[4])
        i = i + 1

    if 0:
        for m in modelList[:-1:]:
            figt, axt = plt.subplots(nrows=1, ncols=1)
            fig2t, ax2t = plt.subplots(nrows=1, ncols=1)
            (cft,f)  = plotAModelCart( m, axt,  X, Y, True, minX, maxX, minY, maxY, '')
            (cf2t,f) = plotAModelPolar(m, ax2t, R, T, True, maxR, maxT, '')

            if save:
                pdf = PdfPages('./figures/AvRSSI_cart_'+str(f)+'.pdf')
                pdf.savefig(figt)
                pdf.close()

                pdf = PdfPages('./figures/AvRSSI_pol_'+str(f)+'.pdf')
                pdf.savefig(fig2t)
                pdf.close()


    #
    minAVrssiList.sort()
    maxAVrssiList.sort()
    print "/////////////////////////////////////////"
    print "Global range " + str(minAVrssiList[0]) + ", " + str(maxAVrssiList[-1])

    #
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(cf, cax=cbar_ax,label='decibels')

    #plt.axis('off')
    #
    # #/////////////////////////////////////////////
    fig2.subplots_adjust(right=0.8)
    cbar_ax2 = fig2.add_axes([0.85, 0.15, 0.05, 0.7])
    fig2.colorbar(cf2, cax=cbar_ax2,label='decibels')

    #/////////////////////////////////////////////
    (cfa,f2) = plotAModelCart(modelList[-1], axa, X, Y, True,  minX,maxX,minY,maxY,  'Overlapped frequencies')
    (cf2a,f2) = plotAModelPolar(modelList[-1], ax2a, R, T, True,  maxR,maxT, 'Overlapped frequencies')


    figa.subplots_adjust(right=0.8)
    cbar_axa = figa.add_axes([0.85, 0.15, 0.05, 0.7])
    figa.colorbar(cfa, cax=cbar_axa,label='decibels')


    fig2a.subplots_adjust(right=0.8)
    cbar_ax2a = fig2a.add_axes([0.85, 0.15, 0.05, 0.7])
    fig2a.colorbar(cf2a, cax=cbar_ax2a,label='decibels')

    # /////////////////////////////////////////////

    if not save:
        plt.show()

    #/////////////////////////////////////////////
    if save:
        pdf=PdfPages('./figures/AvRSSI_cart_map.pdf')
        pdf.savefig(fig)
        pdf.close()

        pdf=PdfPages('./figures/AvRSSI_pol_map.pdf')
        pdf.savefig(fig2)
        pdf.close()

        pdf = PdfPages('./figures/AvRSSI_cart_AllF.pdf')
        pdf.savefig(figa)
        pdf.close()

        pdf = PdfPages('./figures/AvRSSI_pol_AllF.pdf')
        pdf.savefig(fig2a)
        pdf.close()




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
