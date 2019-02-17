from math import fabs
from Base import Base

class ResultData(Base):

    # initialize the attributes
    def __init__(self):
        Base.__init__(self)
        self.nodePos = {}           # selected fiber nodes
        self.sumRFo  = [0.,0.,0.]   # sum of reaction forces
        self.nodeRFo = {}           # reaction force on nodes
        self.nodeDis = {}           # displacements along the fiber

    # calculate the maximum vertical displacent along the fiber
    def getMaxDisp(self):
        max = 0.
        for label in self.nodePos:
            disp = self.nodeDis[label]
            # y
            if (fabs(disp[1]) > fabs(max)): max = disp[1]
        return max