#==============================================================================
# a class to handle the input parameters
# for the Quadrilateral Triple-T profile
#
# dimensions:  mm, N
#==============================================================================

from Base import Base
from math import sin
from math import cos
from math import radians as rad

class InputData(Base):
    # constructor
    def __init__(self):
        # uncomment the required combined profile(CP) here.
        name, a_q, b_q, s_q, b_t, h_t, s_t, l = "CP1", 120, 60, 4, 50, 50, 6, 3700
        # name, a_q, b_q, s_q, b_t, h_t, s_t, l = "CP2", 140, 80, 4, 50, 50, 6, 3700
        # name, a_q, b_q, s_q, b_t, h_t, s_t, l = "CP3", 160, 90, 4, 50, 50, 6, 3700

        # call the Base constructor
        Base.__init__(self)

        # geometry parameters
        self.name = name   # name of the profile
        self.a_q = a_q     # width of quadrilateral profile
        self.b_q = b_q     # height of quadrilateral profile
        self.s_q = s_q     # thickness of quadrilateral profile
        self.b_t = b_t     # length of T flange
        self.h_t = h_t     # length of T web
        self.s_t = s_t     # thickness of T beam
        self.l = l         # length of the profile

        # material parameters
        self.EMod = 210000.    # young's modul
        self.nue  = 0.3        # poisson ratio
        self.rho  = 7.8e-6     # density [kg/mm^3]
        self.load =  -29.0     # load in [kN]

        # model parameters
        # set mesh seed
        self.maxElement  = int(200)
        self.quadHeightSeed = int(5)
        self.quadWidthSeed = int(10)
        self.tFlangeSeed = int(5)
        self.tWebSeed = int(5)
        self.lengthSeed  = int(10)

        # step parameters
        self.LINEAR      = 0    # linear static calculation
        self.BUCKLING    = 1    # stability analysis
        self.stepnames   = ("Linear", "Buckling")
        self.jobnames    = (self.name + "-Linear", self.name + "-Buckling")
        self.steptype    = self.LINEAR
        self.stepname    = self.stepnames[self.steptype]
        self.jobname     = self.jobnames[self.steptype]

        self.Check()        # check for possible geometrical errors
        self.calcHelpers()  # calculate helper variables

    # load the inputdata from a file
    def Load(self,filename):
        # calculate helper variables
        self.calcHelpers()

    # check the input data
    def Check(self):
        dmin = 0.1      # minimum length
        if self.b_t < dmin:
            raise Exception("error: Invalid flange length for T section", self.b_t)
        elif self.h_t < dmin:
            raise Exception("error: Invalid web length for T section", self.h_t)
        elif (self.s_t < dmin):
            raise Exception("error: Geometric parameters must be non-negative - invalid T section thickness : %8.4f", self.s_t)
        elif (self.s_t > self.b_t):
            raise Exception("error: Flange length must be greater than T section thickness", self.s_t, self.b_t)
        elif (self.s_t > self.h_t):
            raise Exception("error: Web length must be greater than T section thickness", self.s_t, self.h_t)
        else:
            print"--------------ERROR CHECK ON T-SECTION SUCCESSFUL:::::NO ERRORS FOUND-----------------"
        if self.a_q < dmin:
            raise Exception("error: Invalid width for quadrilateral section", self.a_q)
        elif self.b_q < dmin:
            raise Exception("error: Invalid height for quadrilateral section", self.b_q)
        elif (self.s_q > self.a_q) or (self.s_q > self.b_q):
            raise Exception("error: Both length and width of the quadrilateral section must be greater than it's thickness", self.s_q)
        else:
            print"--------------ERROR CHECK SUCCESSFUL:::::NO ERRORS FOUND---------------"
        if not self.a_q >= (2 * self.b_t):
            raise Exception("error: The T-beams collide each other")
        else:
            print "--------------COLLISION CHECK SUCCESSFUL:::::NO ERRORS FOUND---------------"

    # calculate helper variables
    def calcHelpers(self):
        self.qs = (self.a_q - self.s_q) / 2.
        self.lower_y = (self.b_q / 2.) + self.h_t - (self.s_t / 2.)
        self.quad_y = (self.b_q / 2.) - (self.s_q / 2.)
        self.p1  = self.load * 1.e3 / (self.l * (self.b_t + self.a_q)) # pressure