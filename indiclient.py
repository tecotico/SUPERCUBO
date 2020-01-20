
import argparse
import sys
import time
import logging
import PyIndi
import threading

#------------------------------
class IndiClient(PyIndi.BaseClient):
    
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        blobEvent.set()
        pass
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
        self.ccd='SBIG CCD'
        self.device_ccd=self.getDevice(self.ccd)
        while not(self.device_ccd):
            time.sleep(0.5)
            self.device_ccd=self.getDevice(self.ccd)

        self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")
        while not(self.ccd_connect):
            time.sleep(0.5)
            self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")
    
        if not(self.device_ccd.isConnected()):
            self.ccd_connect[0].s=PyIndi.ISS_ON
            self.ccd_connect[1].s=PyIndi.ISS_OFF
            self.sendNewSwitch(self.ccd_connect)
    
        self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")
        while not(self.ccd_connect):
            time.sleep(0.5)
            self.ccd_connect=self.device_ccd.getSwitch("CONNECTION")

        self.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")
        
        self.ccd_ccd1=self.device_ccd.getBLOB("CCD1")
        while not(self.ccd_ccd1):
            time.sleep(0.5)
            self.ccd_ccd1=self.device_ccd.getBLOB("CCD1")   
    
        self.ccd_exposure=self.device_ccd.getNumber("CCD_EXPOSURE")
        while not(self.ccd_exposure):
            time.sleep(0.5)
            self.ccd_exposure=self.device_ccd.getNumber("CCD_EXPOSURE")   
        
    def serverDisconnected(self, code):
        pass

