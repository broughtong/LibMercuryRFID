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

    width=60
    height=60
    numFreq=len(modelList)-1

    X, Y = np.mgrid[slice(-(gridSize), (gridSize), gridResolution),
                    slice(-(gridSize), (gridSize), gridResolution)]

    freqList=np.zeros(numFreq)
    allData=np.zeros((width, height,numFreq))
    i=0
    for m in modelList[:-1:]:
        freqList[i]=(float(m[1])/1000)
        avRssi = np.array(m[4]).reshape(width, height)
        allData[:,:,i]=avRssi
        i=i+1

    jmax=kmax=60
    tol=gridResolution
    rTarg=1
    Tetol = 0.1*math.pi
    teDeg=30
    teTarg = teDeg*math.pi/180
    propAtR = np.zeros(numFreq)
    n= np.zeros(numFreq)
    for k in xrange(0, jmax):
        for j in xrange(0, kmax):
            x = X[k][j]
            y = Y[k][j]
            r = math.sqrt(x * x + y * y)
            te=math.atan2(y,x)

            if math.fabs(te-teTarg)<Tetol:
                if math.fabs(r - rTarg) < tol:
                    newData=allData[k,j,:]
                    for it in xrange(0,len(newData)):
                        if not math.isnan(newData[it]):
                            propAtR[it] = propAtR[it] + (( newData[it] - propAtR[it]) / (n[it] + 1))
                            n[it] = n[it] + 1

    fig = plt.figure(figsize=(6, 5))
    plt.plot(freqList,propAtR)
    plt.xlabel('frequency (MHz.)')
    plt.ylabel('Average RSSI (dB)')
    plt.grid(True)
    font = {'family': 'serif',
            'color': 'black',
            'weight': 'normal',
            'size': 16,
            }

    angleS=str(teDeg)
    distS=str(rTarg)
    plt.text(902, -62, 'Tag at '+distS+' m.,'+ angleS+ ' deg.', fontdict=font)


    pdf = PdfPages("figures/freq_dep_"+distS+"m_"+angleS+"deg.pdf")
    pdf.savefig(fig)
    pdf.close()

    plt.show()