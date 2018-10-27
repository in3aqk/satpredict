#! /usr/bin/python3
import serial
import binascii

#------------------------------------------------------------------------------
#This class imports the serial class, and uses the serial connection to send 
#data to a Yaesu 857d radio. This radio uses what is calls CAT communication, 
#which is serial data. Commands are issued by sending blocks of 5 character 
#hexidecimal commands, as outlined in the Yaesu 857d CAT control section of the
#users manual.
#------------------------------------------------------------------------------
class YaesuControl:
    def __init__(self):
        #initializes seting for serial communcations and makes some basic
        #declarations.

        self.radioConnection = serial.Serial()
        self.radioConnection.port = '/dev/ttyAMA0'
        self.radioConnection.baudrate = 4800
        self.radioConnection.stopbits = 2
        self.radioConnection.timeout = 3
        self.radioModes = {'LSB' : b'\x00', 'USB' : b'\x01', 'CW' : b'\x02',
                           'CWR' : b'\x03', 'AM' : b'\x04', 'FM' : b'\x08',
                           'NFM' : b'\x88', 'DIG' : b'\x0a', 'PKT' : b'\x0c'}
                            #LSB=Lower Side Band : USB=Upper Side Band :
                            #CW=Morse Code : CWR=Morse code, reverse band
                            #AM=Amplitude Modulation : FM=Frequency Modulation
                            #NFM=Narrow FM : DIG=Digital : PKT=Packet
        
        self.CTCSSTones = {67.0:b'\x06\x70', 69.3:b'\x06\x93', 71.9:b'\x07\x19',
                           74.4:b'\x07\x44', 77.0:b'\x07\x70', 79.7:b'\x07\x97',
                           82.5:b'\x08\x25', 85.4:b'\x08\x54', 88.5:b'\x08\x85',
                           91.5:b'\x09\x15', 94.8:b'\x09\x48', 97.4:b'\x09\x48',
                           100.0:b'\x10\x00', 103.5:b'\x10\x35',
                           107.2:b'\x10\x72', 110.9:b'\x11\x09',
                           114.8:b'\x11\x48', 118.8:b'\x11\x88',
                           123.0:b'\x12\x30', 127.3:b'\x12\x73',
                           131.8:b'\x13\x18', 136.5:b'\x13\x65',
                           141.3:b'\x14\x13', 146.2:b'\x14\x62',
                           151.4:b'\x15\x14', 156.7:b'\x15\x67',
                           159.8:b'\x15\x98', 162.2:b'\x16\x22',
                           165.5:b'\x16\x55', 167.9:b'\x16\x79',
                           171.3:b'\x17\x13', 173.8:b'\x17\x38',
                           177.3:b'\x17\x73', 179.9:b'\x17\x99',
                           183.5:b'\x18\x35', 186.2:b'\x18\x62',
                           189.9:b'\x18\x99', 192.8:b'\x19\x28',
                           196.6:b'\x19\x66', 199.5:b'\x19\x95',
                           203.5:b'\x20\x35', 206.5:b'\x20\x65',
                           210.7:b'\x21\x07', 218.1:b'\x21\x81',
                           225.7:b'\x22\x57', 229.1:b'\x22\x91',
                           233.6:b'\x23\x36', 241.8:b'\x24\x18',
                           250.3:b'\x25\x03', 254.1:b'\x25\x41'}
                            # the 50 standard CTCSS tones and thir hex
                            #equivelents (as the radio interperts them

        self.DCSCodes = {6:b'\x00\x06', 7:b'\x00\x07', 15:b'\x00\x15',
                         17:b'\x00\x17', 21:b'\x00\x21', 23:b'\x00\x23',
                         25:b'\x00\x25', 26:b'\x00\x26', 31:b'\x00\x31',
                         32:b'\x00\x32', 36:b'\x00\x36', 43:b'\x00\x43',
                         47:b'\x00\x47', 50:b'\x00\x50', 51:b'\x00\x51',
                         53:b'\x00\x53', 54:b'\x00\x54', 65:b'\x00\x65',
                         71:b'\x00\x71', 72:b'\x00\x72', 73:b'\x00\x73',
                         74:b'\x00\x74', 114:b'\x01\x14', 115:b'\x01\x15',
                         116:b'\x01\x16', 122:b'\x01\x22', 125:b'\x01\x25',
                         131:b'\x01\x31', 132:b'\x01\x32', 134:b'\x01\x34',
                         141:b'\x01\x41', 143:b'\x01\x43', 145:b'\x01\x45',
                         152:b'\x01\x52', 155:b'\x01\x55', 156:b'\x01\x56',
                         162:b'\x01\x62', 165:b'\x01\x65', 172:b'\x01\x72',
                         174:b'\x01\x74', 205:b'\x02\x05', 212:b'\x02\x12',
                         214:b'\x02\x14', 223:b'\x02\x23', 225:b'\x02\x25',
                         226:b'\x02\x26', 243:b'\x02\x43', 244:b'\x02\x44',
                         245:b'\x02\x45', 246:b'\x02\x46', 251:b'\x02\x51',
                         252:b'\x02\x52', 255:b'\x02\x55', 261:b'\x02\x61',
                         263:b'\x02\x63', 265:b'\x02\x65', 266:b'\x02\x66',
                         271:b'\x02\x71', 274:b'\x02\x74', 306:b'\x03\x06',
                         311:b'\x03\x11', 315:b'\x03\x15', 325:b'\x03\x25',
                         331:b'\x03\x31', 332:b'\x03\x32', 343:b'\x03\x43',
                         346:b'\x03\x46', 351:b'\x03\x51', 356:b'\x03\x56',
                         364:b'\x03\x64', 365:b'\x03\x65', 371:b'\x03\x71',
                         411:b'\x04\x11', 412:b'\x04\x12', 413:b'\x04\x13',
                         423:b'\x04\x23', 431:b'\x04\x31', 432:b'\x04\x32',
                         445:b'\x04\x45', 446:b'\x04\x46', 452:b'\x04\x52',
                         454:b'\x04\x54', 455:b'\x04\x55', 462:b'\x04\x62',
                         464:b'\x04\x64', 465:b'\x04\x65', 466:b'\x04\x66',
                         503:b'\x05\x03', 506:b'\x05\x06', 516:b'\x05\x16',
                         523:b'\x05\x23', 526:b'\x05\x26', 532:b'\x05\x32',
                         546:b'\x05\x46', 565:b'\x05\x65', 606:b'\x06\x06',
                         612:b'\x06\x12', 624:b'\x06\x24', 627:b'\x06\x27',
                         631:b'\x06\x31', 632:b'\x06\x32', 654:b'\x06\x54',
                         662:b'\x06\x62', 664:b'\x06\x64', 703:b'\x07\x03',
                         712:b'\x07\x12', 723:b'\x07\x23', 731:b'\x07\x31',
                         732:b'\x07\x32', 734:b'\x07\x34', 743:b'\x07\x43',
                         754:b'\x07\x54'}
                            # the approximately 100 DCS codes and their hex
                            #equivelents (as the radio interperts them)
     


#------------------------------------------------------------------------------
# The next group of functions are for sending Yaesu CAT control blocks that
# take no arguments. Most of these commands are for turning functions and
# features on and off
#------------------------------------------------------------------------------


    def startRadioComm(self):
        #starts communication with radio

        self.radioConnection.open()
        self.radioConnection.flushOutput()
        self.radioConnection.flushInput()
        
    def stopRadioComm(self):
        #stops communication with radio

        self.radioConnection.flushOutput()
        self.radioConnection.flushInput()
        self.radioConnection.close()
    
    def lockOn (self):
        #turns radio keypad lock on

        self.radioConnection.write (b'\x00\x00\x00\x00\x00')
        response = self.radioConnection.read()
                
    def lockOff (self):
        #turns radio keypad lock off

        self.radioConnection.write(b'\x00\x00\x00\x00\x80')
        response = self.radioConnection.read()
        
    def pttOn (self):
        #engages Push-to-Talk (turns transmitter on)

        self.radioConnection.write(b'\x00\x00\x00\x00\x08')
        response = self.radioConnection.read()
        
    def pttOff (self):
        #disengages Push-to-Talk (turns transmitter off)

        self.radioConnection.write(b'\x00\x00\x00\x00\x88')
        response = self.radioConnection.read()
        
    def clarifierOn (self):
        #turns the clarifier feature on

        self.radioConnection.write(b'\x00\x00\x00\x00\x05')
        response = self.radioConnection.read()
        
    def clarifierOff (self):
        #turns the clarifier feature off

        self.radioConnection.write(b'\x00\x00\x00\x00\x85')
        response = self.radioConnection.read()
        
    def vfoToggle (self):
        #toggles between VFO A and B

        self.radioConnection.write(b'\x00\x00\x00\x00\x81')
        response = self.radioConnection.read()
        
    def splitOn (self):
        #turns the split transmit/receive funtion on.  This allows transmitting
        #on one frequency and receiving on another

        self.radioConnection.write(b'\x00\x00\x00\x00\x02')
        response = self.radioConnection.read()
        
    def splitOff (self):
        #turns the split transmit/receive off

        self.radioConnection.write(b'\x00\x00\x00\x00\x82')
        response = self.radioConnection.read()

       
#------------------------------------------------------------------------------
#The next functions are for reading data from the radio with CAT commands
#------------------------------------------------------------------------------
        

    def readFreqAndMode(self):
        #returns a string representing frequency and mode 

        self.radioConnection.write(b'\x00\x00\x00\x00\x03')
        freqAndModeFromRadio = binascii.hexlify(self.radioConnection.read(5))
        return freqAndModeFromRadio.decode()
    
    def readFrequency(self):
        #returns a float representing the current frequency of the
        #radio, in Mhz

        radioInfo = self.readFreqAndMode()
        frequencyRead = float(radioInfo[0:3]+'.'+radioInfo[3:8])

        return frequencyRead
    
    def readMode(self):
        #returns a string representing the operating mode of the radio,
        #in the standard abbreviations used in Amateur Radio Service

        self.radioConnection.write(b'\x00\x00\x00\x00\x03')
        outputFromRadio = self.radioConnection.read(5)
        modePart = chr(outputFromRadio[4]).encode('latin-1')
        mode = [key for (key, value) in self.radioModes.items()
                if value == modePart]
       
        return (mode[0])

    def readRXStatus(self):
        #potential future functions, but for now I don't see a need for the
        #data this command gets from the radio, and it is not in the scope
        #of the project

        return 0

    def readTXStatus(self):
        #potential future function, but for now I don't see a need for the
        #data this command gets from the radio, and it is not in the scope
        #of the project

        return 0

    def readThis(self):
        #This function is mostly for testing, to check for output from the
        #radio at times there seems to be extra data coming from the radio. 
        #This function reads the characters output by the radio one at a
        #time, and prints them to the screen, until nothing is sent by
        #the radio.

        while True:
            radioOutput = self.radioConnection.read()
            print (radioOutput)
            if radioOutput == b'' : break
        garbageCollection=input('enter to continue')
        


#------------------------------------------------------------------------------        
#The next functions are for sending CAT control blocks that take arguments
#------------------------------------------------------------------------------


        
    def setFrequency(self, frequency):
        #This function takes a float representing the frequency in MHz
        #(i.e. 14.225) and sets the radio to that frequency.  The frequency
        #must be in the Amateure allotment, from 1.8 - 450Mhz
        
        if frequency > 1.79999 and frequency < 450.00001:
            freq = '%09.05f' % frequency
                #formats the frequency float to the correct precision
                #and format
            freq = (freq[:3] + freq[4:])
                #takes out the '.' in preperation for creading the hex string

            commandbytes = []
            for i in range (0, len(freq), 2):
                #steps through freq and makes the hex string that the
                #radio needs
                commandbytes.append(chr(int(freq[i:i+2], 16)))

            command = ''.join(commandbytes).encode('latin-1')
                #creates the hex command, minus the final control character
                #latin encoding used here because UTF incorrectly codes some
                #some of the radio commnds, resulting in extra characters

            self.radioConnection.write(command)
                #writes the command to the radio       
            self.radioConnection.write(b'\x01')
                #writes the control command for change frequency

            response = self.radioConnection.read()

    def setOperatingMode(self, mode):
        #this function takes a string and sets the operating mode of the
        #radio. The string mode must be one of the standards, included
        #in the dictionary self.radioModes{}

        self.radioConnection.write(self.radioModes[mode])
        self.radioConnection.write(b'\x00\x00\x00\x07')
        response = self.radioConnection.read()

    def setClarifierOffset(self, kHzOffset):
        #this function takes a float representing the amount of the
        #clarifier offset, in kHz and sets the offset of the clarifier.  
        
        if kHzOffset < 10 and kHzOffset > -10:
            offset = '%+06.02f' % kHzOffset     #setting format
        else:
            return 0
        
        offset = (offset[:3] + offset[4:])      #removing '.'

        commandbytes = []
        if offset[0] == '+':
            #creates first hex charater in command
            commandbytes.append(chr(int('00', 16))) 
        else:
            commandbytes.append(chr(int('01', 16)))

        commandbytes.append(chr(int('00', 16)))
            #second hex character in this command is always 00

        for i in range (1, len(offset), 2):
            #sets the 3rd and 4th elements of the hex code
            commandbytes.append(chr(int(offset[i:i+2], 16)))

        command = ''.join(commandbytes).encode('latin-1')

        self.radioConnection.write(command)
        self.radioConnection.write(b'\xF5')
        response = self.radioConnection.read()

    def setRptOffsetDirection(self, offsetDirection):
        #sets the repeater offset shift direction by taking input of
        # '+' for positive offset, '-' for negative offset or 'simp'
        #for simplex
        
        directionFlag = {'+' : b'\x49', '-' : b'\x09', 'simp' : b'\x89'}

        self.radioConnection.write(directionFlag[offsetDirection])
        self.radioConnection.write(b'\x00\x00\x00\x09')
        response = self.radioConnection.read()

    def setRptOffsetFrequency(self, mHzOffset):
        # takes a float representing the desired offset frequency for the
        #repeater in MHz.  (the distance between the transmit and receive
        #frequencies) most 2 meter repeaters use 0.6MHz most 440 repeaters
        #use 5MHz
        
        if mHzOffset < 100 and mHzOffset > 0:
            offsetFreq = '%06.02f' % mHzOffset     #setting format
        else:
            return 0
       
        offsetFreq = (offsetFreq[:3] + offsetFreq[4:])
            #takes out the '.' in preperation for creading the hex string

        commandbytes = []
        for i in range (0, len(offsetFreq), 2):
            #steps through freq and makes the hex string that the radio needs
            commandbytes.append(chr(int(offsetFreq[i:i+2], 16)))

        command = ''.join(commandbytes).encode('latin-1')
            # creates the hex command, minus the final control character

        self.radioConnection.write(command)
            #write the frequency
        self.radioConnection.write(b'\x00\xf9')
            #write the control command for change frequency
        response = self.radioConnection.read()

    def setDCSmode(self, DCSflag):
        #Takes a string and turns on the digitally coded squelch.  Acceptable
        #commands are 'both', 'encode', or 'decode'.  Any othercommand turns
        #DCS encoding off
        
        if DCSflag == 'both':
            self.radioConnection.write(b'\x0a\x00\x00\x00\x0a')
        elif DCSflag == 'encode':
            self.radioConnection.write(b'\x0c\x00\x00\x00\x0a')
        elif DCSflag == 'decode':
            self.radioConnection.write(b'\x0b\x00\x00\x00\x0a')
        else:
            self.radioConnection.write(b'\x8a\x00\x00\x00\x0a')
        response = self.radioConnection.read()

    def setCTCSSmode(self, CTCSSflag):
        #Takes a string and turns on the CTCSS tone squelch.  Acceptable
        #commands are 'both', 'encode', or 'decode'.  Any other command turns
        #CTCSS encoding off
        
        if CTCSSflag == 'both':
            self.radioConnection.write(b'\x2a\x00\x00\x00\x0a')
        elif CTCSSflag == 'encode':
            self.radioConnection.write(b'\x4a\x00\x00\x00\x0a')
        elif CTCSSflag == 'decode':
            self.radioConnection.write(b'\x3a\x00\x00\x00\x0a')
        else:
            self.radioConnection.write(b'\x8a\x00\x00\x00\x0a')
        response = self.radioConnection.read()

    def setCTCSSTone (self, toneTX, toneRX):
        #takes a float and sets the CTCSSTone
        
        self.radioConnection.write(self.CTCSSTones[toneTX])
        self.radioConnection.write(self.CTCSSTones[toneRX])
        self.radioConnection.write(b'\x0b')
        response = self.radioConnection.read()

    def setDCSCode (self, codeTX, codeRX):
        #takes an integer and sets the DCS done 
        self.radioConnection.write(self.DCSCodes[codeTX])
        self.radioConnection.write(self.DCSCodes[codeRX])
        self.radioConnection.write(b'\x0c')
        response = self.radioConnection.read()
        
#------------------------------------------------------------------------------        
#The next functions are for performing user actions.  These functions will
#simluate user interface options, combinations of CAT commands that work
#together to perform actions, etc.
#------------------------------------------------------------------------------      

    def increaseFrequency(self, stepUp):
        #increases frequency by stepUp (float) amount (in MHz).  
        self.setFrequency(self.readFrequency()+stepUp)

    def decreaseFrequency(self, stepDown):
        #decreases frequency by stepDown (float) amount (in MHz).  
        self.setFrequency(self.readFrequency()-stepDown)
    

    def splitOperation(self, splitOffset, receiveFrequency):
        #sets up transceiver for split operation mode and engages
        #the split function. splitOffset is a float representing MHz. This
        #function uses whichever VFO is currently selected as the receive VFO,
        #and the opposite VFO as the transmit VFO
        
        self.setFrequency(receiveFrequency)
        self.vfoToggle()
        self.setFrequency(receiveFrequency + splitOffset)
        self.vfoToggle()
        self.splitOn()
        
    def repeaterSetup(self, repeaterOutput, rptOffset, direction, toneORdcs,
                      tone):
        #sets up transceiver for operation on a repeater.  uses whichever
        #VFO is currently in use.  Offset a float in MHZ. direction is either
        #'+' or '-', toneORdcs is either a 'T' or a 'D' to indicate whether
        #repeater uses a CTCSS or DCS.  CTCSS is the default (only 1 repeater
        #in Central PA uses DCS, for example). This function is for basic
        #repeater setup.
        #if advanced repeater setup is needed (i.e. split tones, etc) the
        #individual functions for each setting must be used
        
        self.setFrequency(repeaterOutput)
        self.setOperatingMode('FM')
        self.setRptOffsetFrequency(rptOffset)
        self.setRptOffsetDirection(direction)
        
        if str.lower(toneORdcs) == 'd':
            self.setDCSmode('both')
            self.setDCSCode(int(tone), int(tone))
        if str.lower(toneORdcs) =='t':
            self.setCTCSSmode('both')
            self.setCTCSSTone(float(tone), float(tone))
        else:
            self.setCTCSSmode('off')
            
    def bandSelection(self, band, mode):
        #gives a basic band selection feature band is the band of operation
        #mode is either V for voice, or D for digital/cw.  It sets the
        #frequency to the lowest in the respective portion of the band.
        #reference the "US Amateur Radio Bands" chart available from
        #www.arrl.org.  Bands available in this function are 160m, 80m, 40m,
        #30m, 20m, 17m, 15m, 12m, 10m, 6m, 2m, and 70cm

        if band == '160m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(1.8)
            else:
                self.setOperatingMode('LSB')
                self.setFrequency(1.8)
        elif band == '80m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(3.5)
            else:
                self.setOperatingMode('LSB')
                self.setFrequency(3.6)
        elif band == '40m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(7.0)
            else:
                self.setOperatingMode('LSB')
                self.setFrequency(7.125)
        elif band == '30m':
                self.setOperatingMode('CW')
                self.setFrequency(10.1)
        elif band == '20m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(14.0)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(14.150)
        elif band == '17m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(18.068)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(18.110)
        elif band == '15m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(21.0)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(21.200)
        elif band == '12m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(24.890)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(24.930)
        elif band == '10m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(28.0)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(28.300)
        elif band == '6m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(50.0)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(50.1)
        elif band == '2m':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(144.0)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(144.1)
        elif band == '70cm':
            if mode == 'd' or mode =='D':
                self.setOperatingMode('CW')
                self.setFrequency(420.0)
            else:
                self.setOperatingMode('USB')
                self.setFrequency(420.0)
