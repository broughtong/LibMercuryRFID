#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import os
import math


from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator


# Main function.
if __name__ == '__main__':
    tid = '300833B2DDD9014000000014'
    # resolution and grid size in meters
    dx, dy = 0.3, 0.3
    gridSize = 8

    # generate 2 2d grids for the x & y bounds
    y, x = np.mgrid[slice(-(gridSize / 2), (gridSize / 2), dy),
                    slice(-(gridSize / 2), (gridSize / 2), dx)]

    # pick the desired colormap, sensible levels, and define a normalization
    # instance which takes data values and translates those into levels.
    cmap = plt.get_cmap('OrRd')

    i=0
    fig, ax = plt.subplots(nrows=2,ncols=2)
    ax=ax.reshape(4)

    # should be something like ./300833B2DDD9014000000004/866900
    fileDIR = './' + tid
    files = os.listdir(fileDIR)

    for fileName in files:
        if 'av_rssi' in fileName:
            # fileName=files[4]
            f = float(fileName[0:6])/1000
            fileURIprefix = fileDIR + '/'
            fileURI = fileURIprefix + fileName

            z = np.loadtxt(fileURI, delimiter=',')

            nc, nr = z.shape
            for r in xrange(nr):
                for c in xrange(nc):
                    if z[r, c] == 0.0:
                        z[r, c]=float('NaN')
                    else:
                        z[r, c] = 10*math.log10(z[r, c])

            #z= (z[10:17,10:17])
            levels = MaxNLocator(nbins=15).tick_values(-80, 0)



            # contours are *point* based plots, so convert our bound into point centers
            #cf = ax[i].contourf(x ,  y , z, levels=levels, cmap=cmap)
            cf=   ax[i].imshow(z, interpolation='gaussian', origin='lower')
            #fig.colorbar(cf, ax=ax[i])
            ax[i].set_title('Freq. '+str(f)+' MHz')
            i=i+1
            # adjust spacing between subplots so `ax1` title and `ax0` tick labels
            # don't overlap
            # fig.tight_layout()

    fig.colorbar(cf, ax=ax[i-1])
    plt.show()

if False:
        tidList = ['300833B2DDD901410000000F', '300833B2DDD9014000000004', '300833B2DDD9014000000009',
               '300833B2DDD9014000000010', '300833B2DDD9014000000014', '390000010000000000000006',
               '390000010000000000000007', '390000010000000000000009', '390000010000000000000012',
               '390000010000000000000015', '390000010000000000000020']

    #for tid in tidList:
        tid='300833B2DDD9014000000014'
        # should be something like ./300833B2DDD9014000000004/866900
        fileDIR = './' + tid
        files=os.listdir(fileDIR)
        print tid

        for fileName in files:
            if 'av_rssi' in fileName:
                #fileName=files[4]
                f=fileName[0:6]
                fileURIprefix = fileDIR + '/'
                fileURI = fileURIprefix + fileName


                data= np.loadtxt(fileURI, delimiter=',')

                print f + ': ' + str(sum(sum(data)))

                fig, axes = plt.subplots()

                axes.imshow(data, interpolation='gaussian')
                axes.set_title('gauzz')

                plt.show()