#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:45:27 2020

Python wrapper class for communication with Tektronix oscilloscopes.
Allows for easy retrieval of scope traces over USB connection.
Tested with Tektronix MDO4104B-3 on Linux Kernel 5.3.18
"""

import os
import struct
import time
import numpy as np

transferMode = '16bit'
scopeDev = '/dev/usbtmc0'

class ScopeWrapper:
    def __init__(self):
        self.scope = os.open(scopeDev, os.O_RDWR)
        
        self.lastChannelSync = None
        
        self.ymult = None
        self.yoffset = None
        self.yunit = None
        self.xinc = None
        self.x0   = None
        self.numSamples = None
        
        self.write('*IDN?')
        scopeID = self.read(100).decode()
        print("Scope Returned *IDN? request:")
        print(scopeID)
        
        
        #Some intialization things that apparently allow the scope to return more than 100,000 points
        self.write("DESE 1")
        self.write("*ESE 1")
        self.write("*SRE 32")
        
        self.write("dat INIT")  #Set transfer mode to binary, which is faster than ASCII
        
        if(transferMode == '16bit'):
            self.write("WFMO:BYT_N 2")
            print("Setting transfer mode to 16 bit")
        else:
            self.write("WFMO:BYT_N 1")
            print("Setting transfer mode to 8 bit")
            
        #Set transfer mode to most significant bit first. Keeps things consistent when using struct.decode()
        self.write("WFMO:BYT_O MSB")
        
    def write(self, string):
        os.write(self.scope,string.encode())
    
    def read(self, numBytes):
        return os.read(self.scope,numBytes)
    
    def syncParams(self,channelStr):
        
        #Set channel number
        self.write("DATA:SOURCE " + channelStr)
        self.lastChannelSync = channelStr
        
        #Voltage Scale
        self.write("WFMO:YMU?") #WFMOutpre:YMUlt?
        self.ymult = float(self.read(20))
        
        #Waveform Display Offset
        self.write("WFMO:YOFF?")
        self.yoffset = float(self.read(20))     
        
        #Y units
        self.write("WFMO:YUN?")
        self.yUnit = self.read(20).decode()
        
        #X increment
        self.write("WFMO:XIN?")
        self.xinc = float(self.read(20))
        
        #X offset
        self.write("WFMO:XZE?")
        self.x0 = float(self.read(20))
        
        #Number of samples in recorded waveform
        self.numSamples = self.getRecordLength()
        
        
    
    def getTrace(self, channelStr):
        '''
        channelStr should be one of CH1, CH2, CH3, CH4, REFA, REFB
        '''
        
        #Assuming scope settings havent changed, we do not have to read paramters again for same channel
        if(self.lastChannelSync != channelStr):  
            self.syncParams(channelStr)
        self.write("CURV?")
        datLen = int(self.read(20)[2::])
        recvBuff = b''
        yOut = None
        while len(recvBuff) < datLen:
            recvBuff = recvBuff + self.read(datLen)
        if(transferMode == '16bit'):
            yOut = struct.unpack(">%ih" % (len(recvBuff)/2), recvBuff)
        elif(transferMode == '8bit'):
            yOut = struct.unpack("%ib" % (len(recvBuff)), recvBuff)
        else:
            print("Invalid Transfer Mode")
        yOut = np.array(yOut)
        return ((yOut - self.yoffset) * self.ymult)
    
    def getTimeAxis(self):
        return self.x0 + np.arange(self.numSamples)*self.xinc
    
    def setSingleAcq(self):
        self.write("ACQ:STOPA SEQ") #ACQuire:STOPAfter SEQuence
    
    def acqFinised(self):
        self.write("ACQ:STATE?") #ACQuire:STATE?
        return int(self.read(20))
    
    def getRecordLength(self):
        self.write("HOR:DIG:RECO:MAI?") #HORizontal:DIGital:RECOrdlength:MAIn?
        return int(self.read(20))
    
    def getScopeAcqNum(self):
        self.write("ACQ:NUMAC?")
        return int(self.read(20))
    
    def waitForAcq(self):
        while self.acqFinised() != 0:
            time.sleep(0.01)
        