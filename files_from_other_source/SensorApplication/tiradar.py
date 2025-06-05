# -*- coding: utf-8 -*-

import serial
import serial.tools.list_ports
import numpy as np
import time
import seaborn as sns
import pandas as pd

#3D graph
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

# Url for obtaining config file
# https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/2.1.0/
"""
Other important links:
    http://www.ti.com/lit/ug/swru529b/swru529b.pdf
    http://dev.ti.com/tirex/explore/node?devtools=AWR1642BOOST&node=AMZZpBECR3W8VADs4TntfA__FUz-xrs__LATEST
    from installed sdk: .../ti/mmwave_sdk_03_02_00_04
"""

class TI_AWR1642BOOST():
    """
    Object for communication and control of the TI radar
    """
    def __init__(self, data_band = 921600, config_band = 115200, config_file = '.\\config.cfg', RxAnt = 4, TxAnt = 2):
        
        # Initialization of configuration port
        self.config_port = self.ports()[0]
        self.config_band = config_band
        self.config_serial = serial.Serial(self.config_port, self.config_band, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE, timeout=3.00, xonxoff=False, rtscts=False,
                              write_timeout=5, dsrdtr=False, inter_byte_timeout=0.02 )
        self.test_connection('config')
        
        # Initialization of data port
        self.data_port = self.ports()[1]
        self.data_band = data_band
        self.data_serial = serial.Serial(self.data_port, self.data_band, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE, timeout=3.00, xonxoff=False, rtscts=False,
                         write_timeout=5, dsrdtr=False, inter_byte_timeout=0.02 )
        self.test_connection('data')
        
        # Initializarion for data processing
        self.byteBuffer = np.zeros(2**15,dtype = 'uint8')
        self.byteBufferLength = 0
        # Data word array to convert 4 bytes to 32bit number
        self.word = [1, 2**8, 2**16, 2**24]
        self.sword = [1, 2**8]
        
        # Parsing config file into dict
        self.numRxAnt = RxAnt
        self.numTxAnt = TxAnt
        self.configFileName = config_file
        self.configParameters = self.parseConfigFile()      
      
    def ports(self):
        """
        Gets available serial ports, assumes only radar connected as a serial device
        """
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)
        #print("Available COM ports are: " + str(connected))
        if len(connected) < 2:
            print('There are not available serial ports to initiate communication')
            print('Please check if the radar is connected and powered up')
            raise IOError
        return connected
    
    def test_connection(self,type):
        """
        Tests connection with radar
        """
        try:
            if type == 'config':
                if self.config_serial.isOpen():
                    print(self.config_serial.name,'is open as configuration port \n')
                    self.config_serial.flushInput()
                else:
                    print('Failed to open configuration port',self.config_serial.name)
                    raise IOError
                self.config_serial.close()
            if type == 'data':
                if self.data_serial.isOpen():
                    print(self.data_serial.name, 'is open as data port \n')
                    self.data_serial.flushInput()
                else:
                    print('Failed to open data port',self.data_serial.name)
                    raise IOError
                self.data_serial.close()
        except:
            self.config_serial.close()
            self.data_serial.close()
        
    def serialConfig(self):
        """
        Sends .cfg file created from mmWave demo Visualizer into the radar
        """
        try:
            self.config_serial.open()
            with open(self.configFileName, 'r') as file:
                config = file.read()
            recieved_line = []
            for line in config.splitlines():
                print(line)
                self.config_serial.write(line.encode())
                self.config_serial.write(b'\r\n')
                while self.config_serial.out_waiting > 0:
                    pass
                time.sleep(0.01)
                
                while self.config_serial.in_waiting == 0:
                    print("No response form mmWave")
                    time.sleep(1)
                    
                recieved_line = self.config_serial.readline()
                print(recieved_line.decode())
            self.config_serial.close()
        except:
            self.config_serial.close()
            print('Error while opening configuration port', self.config_serial.name)
    
    def parseConfigFile(self):
        """
        Parsing config file to obtain some settings those will be required for bit decoding and corrections
         - rangeIdx, numDoppler, dopplerRes,...
        """
        configParameters = {}
        config = [line.rstrip('\r\n') for line in open(self.configFileName)]
        for param in config:
            splitWords = param.split(" ")
            
            # Informations about profile configuration
            if "profileCfg" in splitWords[0]:
                startFreq = int(splitWords[2])
                idleTime = int(splitWords[3])
                rampEndTime = float(splitWords[5])
                freqSlopeConst = float(splitWords[8])
                numAdcSamples = int(splitWords[10])
                numAdcSamplesRoundTo2 = 1
                while numAdcSamples > numAdcSamplesRoundTo2:
                    numAdcSamplesRoundTo2 = numAdcSamplesRoundTo2 * 2
                digOutSampleRate = int(splitWords[11])
                
            # Information about frame configuration
            elif "frameCfg" in splitWords[0]:
                chirpStartIdx = int(splitWords[1])
                chirpEndIdx = int(splitWords[2])
                numLoops = int(splitWords[3])
#                numFrames = int(splitWords[4])
#                framePeriodicity = int(splitWords[5])
                
        # Creating dict with settings
        numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1)*numLoops
        configParameters["numDopplerBins"] = numChirpsPerFrame / self.numTxAnt
        configParameters["numRangeBins"] = numAdcSamplesRoundTo2
        configParameters["rangeResolutionMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numAdcSamples)
        configParameters["rangeIdxToMeters"] = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * configParameters["numRangeBins"])
        configParameters["dopplerResolutionMps"] = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * configParameters["numDopplerBins"])
        configParameters["maxRange"] = (300 * 0.9 * digOutSampleRate) / (2 * freqSlopeConst * 1e3)
        configParameters["maxVelocity"] = 3e8 / (4 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * self.numTxAnt)
        configParameters["numVirtualAntennas"] = self.numRxAnt*self.numTxAnt
        
        return configParameters
                  
    def read_parse_data(self):
        """
        """
        #inicialization of byte format
        configParams = self.configParameters
        MMWDEMO_OUTPUT_MSG_NULL = 0
        MMWDEMO_UART_MSG_DETECTED_POINTS = 1
        MMWDEMO_UART_MSG_RANGE_PROFILE = 2
        MMWDEMO_OUTPUT_MSG_NOISE_PROFILE = 3
        MMWDEMO_OUTPUT_MSG_AZIMUTH_STATIC_HEAT_MAP = 4
        MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP = 5
        MMWDEMO_OUTPUT_MSG_STATS = 6        
        maxBufferSize = 2**15
        magicWord = [2,1,4,3,6,5,8,7]
        magicOK = 0
        dataOK = 0
        trigger = 0
        totalPacketLen = 0
        data = {}        
        
        # Serial port check, it should always be closed before reading data and starting the mmWave sensor
        if not self.data_serial.isOpen():
            self.data_serial.open()
            self.data_serial.flushInput()
            self.data_serial.flushOutput()
        self.startSensor()
        time.sleep(0.1)
#        print(self.data_serial.in_waiting)
        readBuffer = self.data_serial.read(self.data_serial.in_waiting)       
        byteVec = np.frombuffer(readBuffer, dtype =  'uint8')
        byteCount = len(byteVec)
#        print(byteVec, byteCount)
        self.stopSensor()
        
        # Check that buffer is not full and then add the data to the buffer
        if (self.byteBufferLength + byteCount) < maxBufferSize:
            self.byteBuffer[self.byteBufferLength:self.byteBufferLength + byteCount] = byteVec[:byteCount]
            self.byteBufferLength = self.byteBufferLength + byteCount
        
        # Check that the buffer has some data    
        if self.byteBufferLength >= 16:
            #Looking for magic word
            locations = np.where(self.byteBuffer == magicWord[0])[0]
            # Confirm location and store the index
            startIdx = []
            for loc in locations:
                check = self.byteBuffer[loc:loc+8]
                if np.all(check == magicWord):
                    startIdx.append(loc)
            
            if startIdx:
                # Check if there are any data in front of 1st startIdx and remove them
                if startIdx[0] > 0:
                    self.byteBuffer[:self.byteBufferLength - startIdx[0]] = self.byteBuffer[startIdx[0]:self.byteBufferLength]
                    self.byteBufferLength = self.byteBufferLength - startIdx[0]  
                if self.byteBufferLength < 0:
                    self.byteBufferLength = 0
                
                # Read the full packet length
                totalPacketLen = np.matmul(self.byteBuffer[12:12+4],self.word)
                # Check that all the packet has been read
                if (self.byteBufferLength >= totalPacketLen) and (self.byteBufferLength != 0):
                    magicOK = 1
#                    print(totalPacketLen)
                    
        # If the data is actually OK, processing can begin
        if magicOK == 1:
            # Init pointer index
            idX = 0
            # Read the header
            magicNumber = self.byteBuffer[idX:idX+8]
            idX += 8
            version = format(np.matmul(self.byteBuffer[idX:idX+4],self.word),'x')
            idX += 4
            totalPacketLen = np.matmul(self.byteBuffer[idX:idX+4],self.word)
            idX += 4
            platform = format(np.matmul(self.byteBuffer[idX:idX+4],self.word),'x')
            idX += 4
            frameNumber = np.matmul(self.byteBuffer[idX:idX+4],self.word)
            idX += 4
            timeCpuCycles = np.matmul(self.byteBuffer[idX:idX+4],self.word)
            idX += 4
            numDetectedObj = np.matmul(self.byteBuffer[idX:idX+4],self.word)
            idX += 4 
            numTLVs = np.matmul(self.byteBuffer[idX:idX+4],self.word)
            idX += 4
            subFrameNumber = np.matmul(self.byteBuffer[idX:idX+4],self.word)
            idX += 4
            print("Magic numbers: ",magicNumber,"\nVersion: ",version,"\nPlatform: ",platform,"\nFrame number: ",frameNumber,
                  "\nTime (CPU Cycles)",timeCpuCycles,"\nNumber detected objects: ",numDetectedObj,"\nNumber TVLs: ",numTLVs,
                  "\nSubframe number: ",subFrameNumber, "\nTotal packet length: ",totalPacketLen)
            #Read the TLV messages
            for tvlIdx in range(numTLVs):
                # Structure Tag
                tvl_type = np.matmul(self.byteBuffer[idX:idX+4],self.word)
                idX += 4
                tvl_length = np.matmul(self.byteBuffer[idX:idX+4],self.word)
                idX += 4
                print("TVL type: ",tvl_type,'; Bits:', tvl_length,'; Start bit:', idX)
                
                if tvl_type == MMWDEMO_OUTPUT_MSG_NULL:
                    print('Null settings have been initiated, no idea what i should do :), sorry.')
                    dataOK = 1
                
                if tvl_type == MMWDEMO_UART_MSG_DETECTED_POINTS:
                    # Descriptor
                    tlv_numObj = np.matmul(self.byteBuffer[idX:idX+2], self.sword)
                    idX += 2
                    tlv_xyzQFormat = 2**np.matmul(self.byteBuffer[idX:idX+2], self.sword)
                    idX += 2
                    
                    # Init arrays
                    rangeIdx = np.zeros(tlv_numObj, dtype = 'int16')
                    dopplerIdx = np.zeros(tlv_numObj, dtype = 'int16')
                    peakVal = np.zeros(tlv_numObj)
                    X = np.zeros(tlv_numObj, dtype = 'int16')
                    Y = np.zeros(tlv_numObj, dtype = 'int16')
                    Z = np.zeros(tlv_numObj, dtype = 'int16')
                    
                    for objectNum in range(tlv_numObj):
                        rangeIdx[objectNum] = np.matmul(self.byteBuffer[idX:idX+2], self.sword)
                        idX += 2
                        dopplerIdx[objectNum] = np.matmul(self.byteBuffer[idX:idX+2],self.sword)
                        idX += 2
                        peakVal[objectNum] = np.matmul(self.byteBuffer[idX:idX+2],self.sword)
                        idX += 2
                        X[objectNum] = np.matmul(self.byteBuffer[idX:idX+2],self.sword)
                        idX += 2
                        Y[objectNum] = np.matmul(self.byteBuffer[idX:idX+2],self.sword)
                        idX += 2
                        Z[objectNum] = np.matmul(self.byteBuffer[idX:idX+2],self.sword)
                        idX += 2
                    
                    # Corrections
                    rangeVal = rangeIdx * configParams["rangeIdxToMeters"]
                    dopplerIdx [dopplerIdx > (configParams["numDopplerBins"]/2-1)] = dopplerIdx [dopplerIdx > (configParams["numDopplerBins"]/2 -1)]- 65535
                    dopplerVal = dopplerIdx * configParams["dopplerResolutionMps"]
                    X = X/tlv_xyzQFormat
                    Y = Y/tlv_xyzQFormat
                    Z = Z/tlv_xyzQFormat
                    
                    # Store it to dict
                    objdata = {"numObj":tlv_numObj, "rangeIdx":rangeIdx, "range": rangeVal, "dopplerIdx":dopplerIdx,
                              "doppler":dopplerVal, "peakVal":peakVal, "X":X, "Y":Y, "Z":Z}
                    data['TVL type: '+str(tvl_type)] = objdata
                    dataOK = 1
                    
                elif tvl_type == MMWDEMO_UART_MSG_RANGE_PROFILE:
                    size = int(configParams["numRangeBins"]/2)
                    rangedata = []
                    for byte in range(size):
                        rangedata.append(np.matmul(self.byteBuffer[idX:idX+4], self.word))
                        idX += 4
                    data['TVL type: '+str(tvl_type)] = rangedata
                    dataOK = 1
                    
                elif tvl_type == MMWDEMO_OUTPUT_MSG_NOISE_PROFILE:
                    size = int(configParams["numRangeBins"]/2)
                    noisedata = []
                    for byte in range(size):
                        noisedata.append(np.matmul(self.byteBuffer[idX:idX+4], self.word))
                        idX += 4
                    data['TVL type: '+str(tvl_type)] = noisedata
                    dataOK = 1
                    
                elif tvl_type == MMWDEMO_OUTPUT_MSG_AZIMUTH_STATIC_HEAT_MAP:
                    size = int((configParams["numRangeBins"]*configParams["numVirtualAntennas"]))
                    bins = {}
                    # More work at decoding is required, info about full decoding process is listed in sdk pdf from TI
                    for rangebin in range(configParams['numRangeBins']):
                        for antenna in range(configParams['numVirtualAntennas']):
                            bindata = np.matmul(self.byteBuffer[idX:idX+4], self.word)
                            idX += 4
                            try:
                                bins['R'+str(antenna)].append(bindata)
                            except KeyError:
                                bins['R'+str(antenna)] = [bindata]        
                    data["TVL type: "+str(tvl_type)] = bins
                    dataOK = 1
                        
                
                elif tvl_type == MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP:
                    size = int((configParams["numRangeBins"]*configParams["numDopplerBins"])/2)
                    dopplerdata = []
                    # More work at decoding is required, info about full decoding process is listed in sdk pdf from TI
                    for byte in range(size):
                        dopplerdata.append(np.matmul(self.byteBuffer[idX:idX+4],self.word))
                        idX += 4
                    data["TVL type: "+str(tvl_type)] = dopplerdata
                    dataOK = 1
                
                # Stat info of mmWave device performace statistical data
                elif tvl_type == MMWDEMO_OUTPUT_MSG_STATS:
                    inframeProcessingTime = np.matmul(self.byteBuffer[idX:idX+4],self.word)
                    idX += 4
                    transmitOutputTime = np.matmul(self.byteBuffer[idX:idX+4],self.word)
                    idX += 4
                    interframeProcessingMargin = np.matmul(self.byteBuffer[idX:idX+4], self.word)
                    idX += 4
                    interchirpProcessingMargin = np.matmul(self.byteBuffer[idX:idX+4], self.word)
                    idX += 4
                    activeFrameCPUload = np.matmul(self.byteBuffer[idX:idX+4], self.word)
                    idX += 4
                    interframeCPUload = np.matmul(self.byteBuffer[idX:idX+4],self.word)
                    idX += 4
                    
                    statinfo = {"Inter-frame Processing Time":inframeProcessingTime, "Transmit output time":transmitOutputTime,
                                "Inter-frame Processing Margin":interframeProcessingMargin, "Inter-chirp Processing Margin":interchirpProcessingMargin,
                                "Active Frame CPU Load":activeFrameCPUload, "Interframe CPU Load":interframeCPUload}
                    data['TVL type: '+str(tvl_type)] = statinfo
                    
                    dataOK = 1
                    
                else:
                    # Usually happens when sent data is corrupted in some way or SDK of the board features more tvl messages
                    print('Unknown TVL type:',tvl_type,'\nPlease check your configuration.')
                    trigger = 1
                    

            if idX > 0:
                shiftsize = idX
                self.byteBuffer[:self.byteBufferLength - shiftsize] = self.byteBuffer[shiftsize:self.byteBufferLength]
                self.byteBufferLength = self.byteBufferLength-shiftsize
                if self.byteBufferLength < 0:
                    self.byteBufferLength = 0
                          
        if dataOK == 1 and trigger == 0:
            print("Data read correctly, returning values")
            return data
        elif dataOK == 1 and trigger == 1:
            print('An error with one or more TVL types has occured, returning known TVL types')
            return data
        else:
            print("Data could not be read correctly, please check config file and size of the frame")
            print("Magic:",magicOK,"Byte count:",byteCount)
            fail_data = {'TVL type: 0':0, 'TVL type: 1':{'X':0,'Y':0,'Z':0},'TVL type: 2':[0],'TVL type: 3':[0],
                         'TVL type: 4':[0],'TVL type: 5':[0],'TVL type: 6':[0],}
            return fail_data   
    
    def stopSensor(self):
        """
        """
        if not self.config_serial.isOpen():
            self.config_serial.open()
        self.config_serial.write(b'sensorStop\r\n')     
        #wait for all characters to be send
        while self.config_serial.out_waiting > 0 :
            pass
        time.sleep(0.01)
        ct = 0
        while self.config_serial.in_waiting == 0:
            time.sleep(0.01)
            if ct == 10:
                print('No resposne from mmWave on stopSensor')
                time.sleep(1)
            if ct > 50:
                self.masterStop()
                ct = 0
            ct += 1
        recieved_line = self.config_serial.readline()
        print('R:',recieved_line.decode())
        time.sleep(0.01)
        recieved_line = self.config_serial.readline()
        print('R:',recieved_line.decode())
        self.config_serial.close()

        
    def startSensor(self):
        """
        """
        if not self.config_serial.isOpen():
            self.config_serial.open()
        self.config_serial.write(b'sensorStart\r\n')
        while self.config_serial.out_waiting > 0 :
            pass
        time.sleep(0.01)
        ct = 0
        while self.config_serial.in_waiting == 0:
            time.sleep(0.01)
            if ct == 10:
                print('No resposne from mmWave on startSensor')
                time.sleep(1)
            if ct > 50:
                self.masterStop()
                ct = 0                
            ct += 1
        recieved_line = self.config_serial.readline()
        print('R:',recieved_line.decode())
        time.sleep(0.01)
        recieved_line = self.config_serial.readline()
        print('R:',recieved_line.decode())
        self.config_serial.close()
#        print('Sensor started')
    
    def masterStop(self):
        """
        """
        if not self.config_serial.isOpen():
            self.config_serial.open()
        self.config_serial.write(b'sensorStop\r\n')
        while self.config_serial.out_waiting > 0 :
            pass
        self.config_serial.close()
        self.data_serial.close()
        print('Sensor stopped, ports closed')
    
            
    
    
    
    
    
radar = TI_AWR1642BOOST()
a = radar.configParameters
radar.serialConfig()
#radar.startSensor()
data = radar.read_parse_data()
#datf = pd.DataFrame.from_dict(dat['TVL type: 4'])
#ax = sns.heatmap(datf)
#plt.show()
#ct = 1

#try:
#    while True:
#        ax = sns.heatmap(datf)
#        plt.pause(0.25)
#        plt.show()
#        dat = radar.read_parse_data()
#        datf = pd.DataFrame.from_dict(dat['TVL type: 4'])
#        plt.clf()
##        if ct % 100 == 0:
##            radar.serialConfig()
##            radar.data_serial.close()
##            radar.config_serial.close()
##            ct = 0
##        ct += 1
#except:
#    pass

##fig = plt.figure()
#try:
#    while True:
#        ax = plt.axes(projection="3d")
#        ax.scatter3D(dat['Frame 0']['X'],dat['Frame 0']['Y'],dat['Frame 0']['Z'])
#        ax.set_xlabel('X')
#        ax.set_xlim([-2,2])
#        ax.set_ylabel('Y')
#        ax.set_ylim([-2,2])
#        ax.set_zlabel('Z')
#        ax.set_zlim([-2,2])
#        plt.pause(0.033)
#        plt.show()
#        dat = radar.read_parse_data()
#except KeyboardInterrupt:
#    pass

class TIRadarVisualisation():
    def __init__(self):
        pass

    def init_plot(self):
        ax = plt.axes()
        ax.set_xlabel('X')
        ax.set_xlim([-10,10])
        ax.set_ylabel('Y')
        ax.set_ylim([0,10])
    
    def plot_data(self,data):
        ax = plt.axes()
        ax.scatter(data['TVL type: 1']['X'],data['TVL type: 1']['Y'])
        plt.pause(0.33)
        plt.show()
        data = radar.read_parse_data()
        plt.clf()
try:
    while True:
        ax = plt.axes()
        ax.scatter(data['TVL type: 1']['X'],data['TVL type: 1']['Y'])
        ax.set_xlabel('X')
        ax.set_xlim([-10,10])
        ax.set_ylabel('Y')
        ax.set_ylim([0,10])
        plt.pause(0.33)
        plt.show()
        dat = radar.read_parse_data()
        plt.clf()
except KeyboardInterrupt:
    pass

#try:
#    while True:
#        ax = plt.axes()
#        radar.stopSensor()
##        time.sleep(5)
#        ax.plot(dat['TVL type: 2'])
#        ax.set_xlabel('X')
#        ax.set_ylabel('Y')
#        plt.pause(0.33)
#        plt.show()
#        dat = radar.read_parse_data()
#        plt.clf()
#except KeyboardInterrupt:
#    pass

radar.masterStop()
