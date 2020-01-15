#!/usr/bin/env python3

import sys, time, logging
import PyIndi

texp = 0.2 

class IndiClient(PyIndi.BaseClient):
    device = None
    def __init__(self, prueba1, prueba2):
        self.pr1 = prueba1
        self.pr2 = prueba2
        
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')

    def newDevice(self, d):
        if d.getDeviceName() == "SBIG CCD":
            # save reference to the device in member variable
            self.device = d
            
    def newProperty(self, p):
        if self.device is not None and p.getName() == "CONNECTION" and p.getDeviceName() == self.device.getDeviceName():
            self.connectDevice(self.device.getDeviceName())
            self.setBLOBMode(1, self.device.getDeviceName(), None)
        if p.getName() == "CCD_EXPOSURE":
            # take first exposure
            self.takeExposure()

    def newBLOB(self, bp):
        print('6')
        img = bp.getblobdata()
        with open(self.pr2, "wb") as f:
        #with open("frame.fits", "wb") as f:
            f.write(img)
        # start new exposure for timelapse images!
        #self.takeExposure()
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        #print("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
        pass
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")
    def takeExposure(self):
        self.logger.info("<<<<<<<< Exposure >>>>>>>>>")
        exp = self.device.getNumber("CCD_EXPOSURE")
        exp[0].value = texp
        self.sendNewNumber(exp)
        
        
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# instantiate the client
indiclient=IndiClient(1.5, 'prueba.fits')
# set indi server localhost and port 7624
indiclient.setServer("localhost",7624)
     
if (not(indiclient.connectServer())):
     print("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort())+" - Try to run")
     print("  indiserver indi_simulator_telescope indi_simulator_ccd")
     print("8")
     sys.stdout.flush()          

     sys.exit(1)
time.sleep(1)

# start endless loop, client works asynchron in background
#while True:
#    time.sleep(1)
time.sleep(texp + 2)
