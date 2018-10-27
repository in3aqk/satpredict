#! /usr/bin/python3

#------------------------------------------------------------------------------
#right now this is just for testing the functions etc. in yaesuControl
#as a write them.  eventually it will turn into a nicer command line interface
#------------------------------------------------------------------------------

import yaesuControl
import os


radio = yaesuControl.YaesuControl()
radio.startRadioComm()

print ('Starting communication with radio\n\r')

bands={'160cw':['160m','d'],'160ssb':['160m','v'],'80cw':['80m','d'],
       '80ssb':['80m','v'],'40cw':['40m','d'],'40ssb':['40m','v'],
       '20cw':['20m','d'],'20ssb':['20m','v'],'17cw':['17m','d'],
       '17ssb':['17m','v'],'15cw':['15m','d'],'15ssb':['15m','v'],
       '12cw':['12m','d'],'12ssb':['12m','v'],'10cw':['10m','d'],
       '10ssb':['10m','v'],'6cw':['6m','d'],'6ssb':['6m','v'],
       '2cw':['2m','d'],'2ssb':['2m','v'],'70cw':['70cm','d'],
       '70ssb':['70cm','v'],'30cw':['30m','d']}

radio.lockOn()  #turn this on, so that things don't get changed at the radio
lock = 'Y'      #accidentally, while the software is controlling it
radio.pttOff()
ptt = False
radio.clarifierOff()
clarifier = 'N'
radio.splitOff()
split = 'N'

def repeaterOperation():
    offset = 0.6
    direction = '-'
    encoding = 'Off'
    tone = 0.0
    radio.pttOff()
    pttRpt = False
    
    radio.repeaterSetup(145.2, offset, direction, encoding, tone)

    while True:
        if pttRpt:
            transmit = 'T(X)'
        else:
            transmit = 'R(X)'
        
        os.system('clear')
        choice = input('-'*80 + '\n' + ' '*35 + 'Yeasu 857d' + ' '*29 +
                       '(Q)uit\n' + '-'*80 + '\n\n'+' '*31+'Repeater Operation'
                       +'\n'+ ' '*35 +'%010.06f' % radio.readFrequency()
                       +'\n'+' '*35 + radio.readMode() + '   ' + transmit
                       +'\n\n'+ ' (D)irection: ' + direction
                       +'    (O)ffset: ' + str(offset)
                       +'    (E)ncoding: ' + encoding
                       +'    (T)one or code: ' + str(tone) + '\n'
                       + '-'*80 +' '*19
                       + 'Frequency can be directly input at prompt.'+' '*19
                       + '\n' + '-'*80
                       +'\n>>')

        if str.lower(choice)=='q':break
        elif str.lower(choice)=='x':
            if pttRpt:
                radio.pttOff()
                pttRpt = False
            else:
                radio.pttOn()
                pttRpt = True
        elif str.lower(choice)=='d':
            if direction == '-':
                direction = '+'
                radio.setRptOffsetDirection(direction)
            elif direction == '+':
                direction = 'simp'
                radio.setRptOffsetDirection(direction)
            else:
                direction='-'
                radio.setRptOffsetDirection(direction)
                
        elif str.lower(choice)=='o':
            offset = float(input('Enter offset Frequency in MHz: '))
            radio.setRptOffsetFrequency(offset)
            
        elif str.lower(choice)=='e':
            entry = input('Enter (Tone), (DCS), or (off) encoding: ')
            if str.lower(entry) == 'tone':
                encoding = 'Tone'
                radio.setCTCSSmode('both')
                radio.setCTCSSTone(67.0,67.0)
                tone=67.0
                
            elif str.lower(entry) == 'dcs':
                encoding = 'DCS'
                radio.setDCSmode('both')
                radio.setDCSCode(23,23)
                tone=23
                
            else:
                encoding = 'Off'
                radio.setCTCSSmode('Off')
                            
        elif str.lower(choice)=='t':
            toneinput = float(input('Enter CTCSS tone or DCS code: '))
            if encoding == 'Tone':
                tone = toneinput
                radio.setCTCSSTone(tone, tone)
            elif encoding == 'DCS':
                tone=int(toneinput)
                radio.setDCSCode(tone, tone)
                
        else:
            try:
                radio.setFrequency(float(choice))
            except:
                pass
            
            

        


while True:
    if ptt:
        transmit = 'T(X)'
    else:
        transmit = 'R(X)'
    try:        
        os.system('clear')
        choice = input('-'*80 + '\n' + ' '*35 + 'Yeasu 857d' + ' '*29 +
                       '(Q)uit\n' + '-'*80 + '\n\n' +
                       'Decrease (-10H)z (-1k)Hz' + ' '*11 +
                       '%010.06f' % radio.readFrequency() + ' '*12 +
                       'Increase (10H)z (1k)Hz' + '\n' +
                       '         (-5k)Hz (-10k)Hz' +
                       ' '*10 + radio.readMode() + '   ' + transmit +
                       ' '*21 + '(5k)Hz (10k)Hz' + '\n\n' +
                       'Keypad (L)ocked: ' + lock + '             (C)larifier On: '+
                       clarifier + '             (S)plit Mode On: ' + split +
                       '\nToggle (V)FO' +' '*19 + '(Cl)arifier Offset' + ' '*12 +
                       '(Sp)lit Setup\n\n' +
                       '-'*80 + '\nModes (type to choose): ' +
                       'LSB    USB    CW    CWR    AM    FM    NFM   DIG    PKT' +
                       '\n' + ' '*30 + '(Re)peater Operation' +
                       '\n' + '-'*80 + '\nBands (type to choose):\n' +
                       ' 160cw 160ssb 80cw 80ssb 40cw 40ssb 30cw 20cw 20ssb 17cw ' +
                       '17ssb 15cw 15ssb\n 12cw  12ssb  10cw 10ssb 6cw  6ssb  2cw  2ssb' +
                       ' 70cw  70ssb\n'+ '-'*80 +
                       ' '*19 + 'Frequency can be directly input at prompt.'+' '*19
                       + '\n' + '-'*80 + '\n>>')
    except:
        print('Error Encountered.  Verify Radio is powered on, and connected')
        garbage=input('type "r" to retry.  Enter to quit: ')
        if str.lower(garbage) == 'r':
            continue
        else:
            break
       
    if choice =='F' or choice =='f':
        #This option isn't displayed in the menu.  It's here for some
        #testing that was done early on.
        #garbage = input(radio.readFreqAndMode())
        pass
    elif choice == 'Q' or choice == 'q':
        print ('Stopping communication and exiting')
        break
    elif choice == 'x' or choice == 'X':
        if ptt:
            radio.pttOff()
            ptt = False
        else:
            radio.pttOn()
            ptt = True
    elif choice == 'L' or choice == 'l':
        if lock == 'Y':
            radio.lockOff()
            lock = 'N'
        else:
            radio.lockOn()
            lock = 'Y'
    elif choice == 'C' or choice == 'c':
        if clarifier =='Y':
            radio.clarifierOff()
            clarifier = 'N'
        else:
            radio.clarifierOn()
            clarifier = 'Y'
    elif choice  == 'S' or choice == 's':
        if split == 'Y':
            radio.splitOff()
            split = 'N'
        else:
            radio.splitOn()
            split = 'Y'
    elif choice == '-10h' or choice == '-10H':
        radio.decreaseFrequency(0.00001)
    elif choice == '-1k' or choice == '-1K':
        radio.decreaseFrequency(0.001)
    elif choice == '-5k' or choice == '-5K':
        radio.decreaseFrequency(0.005)
    elif choice == '-10k' or choice == '-10K':
        radio.decreaseFrequency(0.01)
    elif choice == '10h' or choice == '10H':
        radio.increaseFrequency(0.00001)
    elif choice == '1k' or choice == '-K':
        radio.increaseFrequency(0.001)
    elif choice == '5k' or choice == '5K':
        radio.increaseFrequency(0.005)
    elif choice == '10k' or choice == '10K':
        radio.increaseFrequency(0.01)
    elif choice == 'V' or choice =='v':
        radio.vfoToggle()
    elif str.lower(choice) == 'cl':
        offsetAmount = input('Enter offset from -99.99 to 99.99: ')
        radio.setClarifierOffset(float(offsetAmount))
    elif str.lower(choice) == 'sp':
        splitOffset = (float(input('Enter offset in (+ or -)kHz: ')))*.001
        radio.splitOperation(splitOffset, float(radio.readFrequency()))
        split = 'Y'
    elif choice in radio.radioModes:
        radio.setOperatingMode(choice)
    elif choice in bands:
        radio.bandSelection(bands[choice][0], bands[choice][1])
    elif str.lower(choice)=='re':
        repeaterOperation()
    else:
        try:
            radio.setFrequency(float(choice))
        except:
            pass

    
radio.pttOff()      #be sure to stop transmitting before exting program
radio.stopRadioComm()
os.system('clear')

