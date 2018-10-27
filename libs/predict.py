# -*- coding: utf-8 -*-


import time
import datetime
import sys
import math
import ephem
import os


class Predict():

    
    def __init__(self,config,observer):
        self.config = config
        self.observer = observer
        
        

    def predictToText(self,tle,output='txt'):
        """
        Single sat predict
        """         
        sat = ephem.readtle(tle[0],tle[1],tle[2])

        startTime = self.config['predict'].get('minUtc')
        endTime = self.config['predict'].get('maxUtc')

        ephemStart = ephem.Date("{0} {1}".format(datetime.datetime.now().strftime('%Y/%m/%d'),startTime))
        ephemStop = ephem.Date("{0} {1}".format(datetime.datetime.now().strftime('%Y/%m/%d'),endTime))

        if 'txt' in output:
            fileName = "ALL_{0}.txt".format(datetime.datetime.now().strftime('%Y%m%d'))
            summaryfileName = "SUMMARY_{0}.txt".format(datetime.datetime.now().strftime('%Y%m%d'))
            outFilePath = os.path.join('output',fileName)
            sumOutFilePath = os.path.join('output',summaryfileName)
            if os.path.exists(outFilePath):
                outFile = open(outFilePath,'a+')
            else:
                outFile = open(outFilePath,'w+')
            if os.path.exists(sumOutFilePath):
                sumOutFile = open(sumOutFilePath,'a+')
            else:
                sumOutFile = open(sumOutFilePath,'w+')


        while True:
            tr, azr, tt, altt, ts, azs = self.observer.next_pass(sat)

            #Exit if date/time is passed over the limit
            if tr > ephemStop:
                break

            posArray = []

            while tr < ts:
                self.observer.date = tr
                sat.compute(self.observer)

                position = {
                    'time':ephem.localtime(tr).strftime("%d/%m/%y  %H:%M"),
                    'alt':math.degrees(sat.alt),
                    'az':math.degrees(sat.az),
                    'sublat':math.degrees(sat.sublat),
                    'sublong':math.degrees(sat.sublong)                    
                }    
                posArray.append(position)
               
                tr = ephem.Date(tr + 60.0 * ephem.second)

            self.observer.date = tr + ephem.minute

            #First check if the passage is valid
            visible = False
            for satPosition in posArray:
                if satPosition['alt'] > self.config['predict'].getint('minimumElevation'):
                    visible = True
                

            #If the pass is usable
            if visible:

                if 'console' in output:
                    print ()
                    print (tle[0])
                    print ("""Date/Time (LT)       Alt/Azim	  Lat/Long	""")
                    print ("""=====================================================""")
            
                if 'txt' in output:
                    outFile.write("\n{0}\n".format(tle[0]))
                    outFile.write("Date/Time (LT)       Alt/Azim	  Lat/Long	\n")
                    outFile.write("=====================================================\n")

                    sumOutFile.write("\n{0}\n".format(tle[0]))
                    sumOutFile.write("Date/Time (LT)       Alt/Azim	  Lat/Long	\n")
                    sumOutFile.write("=====================================================\n")


                isFirst = True
                isMaxAlt = False
                i=0 #lines index
                maxAlt = 0
                for satPosition in posArray:

                    passString = "{0} | {1:5.1f} {2:5.1f} | {3:8.4f} {4:8.4f}".format( \
                            satPosition['time'], 
                            satPosition['alt'], 
                            satPosition['az'], 
                            satPosition['sublat'], 
                            satPosition['sublong'])    

                    if 'console' in output:
                        print (passString)

                    if 'txt' in output:

                            passString = "{0} | {1:5.1f} {2:5.1f} | {3:8.4f} {4:8.4f}\n".format( \
                                satPosition['time'], 
                                satPosition['alt'], 
                                satPosition['az'], 
                                satPosition['sublat'], 
                                satPosition['sublong'])

                            outFile.write(passString)

                            #Write first line    
                            if isFirst:
                                sumOutFile.write(passString)
                                isFirst = False
                            #write last line
                            if i == len(posArray)-1:
                                sumOutFile.write(passString)
                                isFirst = False
                            #get center of passage
                            if  satPosition['alt'] < maxAlt and not isMaxAlt:
                                lastMaxAltLine = posArray[i-1]
                                passString = "{0} | {1:5.1f} {2:5.1f} | {3:8.4f} {4:8.4f}\n".format( \
                                lastMaxAltLine['time'], 
                                lastMaxAltLine['alt'], 
                                lastMaxAltLine['az'], 
                                lastMaxAltLine['sublat'], 
                                lastMaxAltLine['sublong'])
                                sumOutFile.write(passString)
                                isMaxAlt = True
                                   
                    i+=1
                    maxAlt = satPosition['alt']
        #end for p                   

        if 'txt' in output:
            outFile.close()
            sumOutFile.close()


