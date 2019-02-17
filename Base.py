# base class for the TWA
from datetime import datetime as time
import io

class Base:

    # instance counter
    __counter = 0          # class attribute
    __log     = "profiles.log"

    # constructor
    def __init__(self,log = ""):
        Base.__counter += 1
        if len(log) > 0: Base.__log = log  

        self.AppendLog(">> Instance %d created." % Base.__counter)

    # reset the log
    def Reset(self):
        io.remove(Base.__log)        

    # log function
    def AppendLog(self,text):

        t         = time.now()          # get the actual time
        timestamp = "%2.2d.%2.2d.%2.2d|" % (t.hour,t.minute,t.second)
        textout   = timestamp + text    # output text

        # create a file object
        f = file(Base.__log,"a")        # open for append
        f.write(textout + "\n")         # add linebreak
        f.close()    

        # print to the screen
        print textout