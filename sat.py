# -*- coding: utf-8 -*-

import os 
import configparser
import urllib.request
from libs.predict import Predict
import ephem
import shutil

class Sat():


    def __init__(self):
        self.currentPath = os.path.dirname(os.path.realpath(__file__))

    def readObserver(self):
        
        satPredictCfg = os.path.join(self.currentPath,'config','satpredict.ini')
        if os.path.isfile(satPredictCfg): 
            config = configparser.ConfigParser()
            config.read(satPredictCfg)
            self.groundstation = ephem.Observer()
            self.groundstation.lat = config['groundstation']['lat']
            self.groundstation.lon = config['groundstation']['long']
            self.groundstation.elevation = config['groundstation'].getint('alt')
            return True

        else:
            print ("No satPredict.ini")
            return False
    

    def readConfig(self):
        
        satPredictCfg = os.path.join(self.currentPath,'config','satpredict.ini')
        if os.path.isfile(satPredictCfg): 
            config = configparser.ConfigParser()
            config.read(satPredictCfg)
            return config

        else:
            print ("No satPredict.ini")
            return False

    def updateTleDb(self):
        
        tleFileName = 'tle.txt'
        tleFile = os.path.join(self.currentPath,'tle',tleFileName)
        satPredictCfg = os.path.join(self.currentPath,'config','satpredict.ini')
        if os.path.isfile(satPredictCfg): 
            config = configparser.ConfigParser()
            config.read(satPredictCfg)
            tleUrl = config['DEFAULT']['tleUrl']

            u = urllib.request.urlopen(tleUrl)
            f = open(tleFile, 'wb')
            
            meta = u.info()
            
            file_size = int(meta['Content-Length'])
    
            print ("Downloading TLE into: {0} ".format(tleFileName))

            file_size_dl = 0
            block_sz = 8192
            
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = "{0}  [{1}%]".format(file_size_dl,int(file_size_dl * 100. / file_size))
                status = status + chr(8)*(len(status)+1)
                print (status)

            f.close()
            print ("Downloaded : {0} Bytes".format(file_size))
        else:
            print ("No satPredict.ini")


    def getSatelliteList(self):
        
        satelliteConfigFile = os.path.join(self.currentPath,'config','satellites.cfg')
        if os.path.isfile(satelliteConfigFile):  
            with open(satelliteConfigFile) as f:
                sats = f.readlines()
            sats = [x.strip() for x in sats]
        else:
            print("error:" + satelliteConfigFile + "missing")

        return sats


    def getTle(self,satName):
        tleFileName = 'tle.txt'
        tleFile = os.path.join(self.currentPath,'tle',tleFileName)
        tle0 = ""
        tle1 = ""
        tle2 = ""
        found = False
        if os.path.isfile(tleFile):
            with open(tleFile) as f:
                tleLines = f.readlines()
            tleLines = [x.strip() for x in tleLines]

            tleLineIdx = 0
            
            for line in tleLines:
                lineArr = line.split(" ")

                if len(lineArr) == 1 and  lineArr[0] == satName :
                    found = True
                    tle0 = line
                if found:
                    tleLineIdx+=1
                if tleLineIdx == 2:
                    tle1=line    
                if tleLineIdx == 3:
                    tle2=line    

                if tleLineIdx == 3:                    
                    return found,tle0,tle1,tle2
            return found,tle0,tle1,tle2    


        else:
            print ("TLE file {0} not found").format(tleFile)
            return found,tle0,tle1,tle2


    def predictAll(self,output="none"):
        sats = self.getSatelliteList()
        
        for sat in sats:            
            found,tle0,tle1,tle2 = self.getTle(sat)
            if found:
                tle =[tle0,tle1,tle2]
                self.predict(tle,output)

    def predictSat(self,satname):
        print("predict sat not implemented")


    def predict(self,tle,output="none"):
        config = self.readConfig()
        self.readObserver()
        predict = Predict(config,self.groundstation)
        predict.predictToText(tle,output)
        

    def deleteOutput (self):
        outFolder = os.path.join(self.currentPath,'output')
        for root, dirs, files in os.walk(outFolder):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        print("Folder content {0} deleted".format(outFolder))
