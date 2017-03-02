

import FreqHandler



class TagModel():

    # Must have __init__(self) function for a class, similar to a C++ class constructor.
    def __init__(self,tid,gridSize,resolution):
        self.gridsMap=dict()
        self.tid=tid
        self.gridSize=gridSize
        self.resolution=resolution

    def updateCell(self, x, y, rssi_db, freq_khz, phase_deg):

        if freq_khz not in self.gridsMap:
            fh=FreqHandler.FreqHandler(self.tid,freq_khz,self.gridSize,self.resolution)
            self.gridsMap[freq_khz]=fh
        else:
            fh=self.gridsMap[freq_khz]

        fh.addData(x, y, rssi_db, phase_deg)