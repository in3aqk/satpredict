#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import re
import operator
import datetime
import time
import subprocess
import atexit
import serial
import platform
import zipfile

VERSION = 1.6

# NOTE: Versions 1.6 and above are written in Python 3

# set this flag to True for development work

DEBUG = True

class IcomIO:

    def __init__(self):

       
        # change these if needed

        self.baud_rate = '19200'

        # Linux: ttyS0, ttyS1 for conventional serial interfaces
        # or ttyUSB0, ttyUSB1 for USB serial adaptors
        self.linux_port = 'ttyUSB0'

        # Windows: COM1, COM2, etc
        self.windows_port = 'COM1'

        # Windows: COM1, COM2, etc
        self.mac_port = 'cu.SLAB_USBtoUART'

        self.icom_codes = {
            # Ham Radios:
            'IC-703': 0x68,
            'IC-706': 0x4e,
            'IC-706MKIIG': 0x58,
            'IC-718': 0x5e,
            'IC-725': 0x28,
            'IC-726': 0x30,
            'IC-728': 0x38,
            'IC-729': 0x3a,
            'IC-735': 0x04,
            'IC-736': 0x40,
            'IC-746': 0x56,
            'IC-746Pro': 0x66,
            'IC-751': 0x1c,
            'IC-756Pro': 0x5c,
            'IC-756Pro-II': 0x64,
            'IC-756Pro-III': 0x6e,
            'IC-761': 0x1e,
            'IC-765': 0x2c,
            'IC-775': 0x46,
            'IC-781': 0x26,
            'IC-970': 0x2e,
            'IC-7000': 0x70,
            'IC-7100': 0x88,
            'IC-7200': 0x76,
            'IC-7600': 0x7a,
            'IC-7700': 0x74,
            'IC-7800': 0x6a,
            # Receivers
            'IC-R71': 0x1A,
            'IC-R72': 0x32,
            'IC-R75': 0x5a,
            'IC-R7000': 0x08,
            'IC-R7100': 0x34,
            'IC-R8500': 0x4a,
            'IC-R9000': 0x2a,
            # Marine Radios
            'M-7000Pro': 0x02,
            'M-710': 0x01,
            'M-710RT': 0x03,
            'M-802': 0x08,
            'Any': 0x00  # (any Icom marine radio)
        }


        self.memory_label_sizes = {
            'IC-R75': 8,
            'IC-R8500': 8,
            'IC-746': 9,
            'IC-746Pro': 9,
            'IC-756Pro': 10,
            'IC-756Pro-II': 10,
            'IC-756Pro-III': 10,
            'IC-7000': 9,
            'IC-7100': 9,
            'IC-7200': 9,
            'IC-7600': 9,
            'IC-7700': 9,
            'IC-7800': 9
        }

        self.bank_sizes = {
            'IC-R8500': 40,
            'IC-7000': 99,
            'IC-7200': 99,
            'IC-7100': 99,
            'IC-7600': 99,
            'IC-7700': 99,
            'IC-7800': 99
        }

        self.modes = {
            'lsb': 0,
            'usb': 1,
            'am': 2,
            'cw': 3,
            'rtty': 4,
            'fm': 5,
            'wfm': 6
        }

        self.field_names = (
            'Bank', 'Mem', 'Name', 'MemTag', 'Mode', 'RxFreq',
            'TxFreq', 'RxTone', 'TxTone', 'Comment',
            'Place', 'Call', 'Sponsor', 'Region'
        )

        self.field_hash = {}
        for n, name in enumerate(self.field_names):
            self.field_hash[name] = n



        self.serial = False
        self.opsys = platform.system()
        if(re.search('(?i)linux', self.opsys)):
            self.port = '/dev/' + self.linux_port
        if(re.search('(?i)Darwin', self.opsys)):
            self.port = '/dev/' + self.mac_port    
        elif(re.search('(?i)windows', self.opsys)):
            self.port = self.windows_port
        else:
            sys.stderr.write(
                'Error: Cannot identify operating system: "%s".\n' % self.opsys)
            sys.exit(0)
        self.set_defaults(0)
        # Register exit function
        atexit.register(self.exit)

    def process_radio(self, radio_model):
        """ Get configuration for the selected radio
            :param: radio_model the radio type
            :return: none
        """
        erase_unused = False
        master_array = []
                
        if(not radio_model in self.icom_codes):
            sys.stderr.write(
                'Error: no hex code for radio model "%s".\n' % radio_model)
        else:
            hex_code = self.icom_codes[radio_model]
            self.radio_id = hex_code
            if(radio_model in self.bank_sizes):
                bank_size = self.bank_sizes[radio_model]
            else:
                bank_size = 0
            

    def debug_print(self, s, linefeed=True):
        """Debug print to standard error
        """
        if(DEBUG):
            sys.stderr.write(s)
            if(linefeed):
                sys.stderr.write('\n')

    def set_defaults(self, banksize):
        """Default configuration
        """
        self.banksize = banksize
        self.current_vfo = -1
        self.mem_bank = -1
        self.mem_loc = -1
        self.split = False

    def exit(self):
        """Exit from class
        """
        self.close_serial()
        self.debug_print('IcomIO exit')

    def close_serial(self):
        """Close the serial port connection
        """
        if(self.serial):
            self.serial.flush()
            self.serial.close()
        self.serial = False

    def init_serial(self, force=False):
        """Serial init
        """
        if(force or not self.serial):
            try:
                self.close_serial()
                self.serial = serial.Serial(
                    self.port,
                    self.baud_rate,
                    parity=serial.PARITY_NONE,
                    timeout=1000,
                    rtscts=0
                )
                self.serial.flushOutput()
                self.serial.flushInput()
            except serial.SerialException as e:
                self.debug_print('Serial INIT ERROR {0}'.format(e))
                self.serial = False
        return self.serial != False

    def read_radio_n(self, n):
        """Read n bytes from radio
           :param: n bytes to read 
        """
        self.debug_print('Read Radio count %d: ' % n, False)
        count = 0
        reply = []
        while(count < n):
            s = self.serial.read(1)
            c = 0
            if(len(s) > 0):
                c = s[0]
            reply.append(c)
            self.debug_print('%02x ' % c, False)
            count += 1
        self.debug_print('Read done ',True)
        return reply

    def render_list_as_hex(self, data):
        """Convert a list to hex
        """
        s = '[ '
        for c in data:
            s += '%02x ' % c
        s += ']'
        return s

    def read_radio_s(self):
        """ Read from radio 
        """
        
        self.debug_print('Read Radio until 0xfd: ', False)
        count = 0
        reply = []
        c = 0
        while(c != 0xfd):
            s = self.serial.read(1)
            c = 0
            if(len(s) > 0):
                c = s[0]
            reply.append(c)
            self.debug_print('%02x ' % c, False)
            count += 1
        self.debug_print('')
        return reply

    def write_radio(self, com,fullResponse=False):
        """Write on Radio a command
        """
        response = ""
        self.debug_print('Write Radio: ', False)
        if self.serial:
            for c in com:
                self.debug_print('%02x ' % c, False)
                self.serial.write(bytes([c]))
            self.debug_print('')
            if fullResponse:
                response = self.read_radio_s()
            else:
                # discard echo reply
                self.read_radio_n(len(com))
                response = ""
        else:
            self.debug_print('Unable to write serial error', False)
        return response     

    def read_radio_response(self):
        """ Read response from radio
        """
        reply = self.read_radio_n(6)
        return reply[4] == 0xfb  # meaning no errors

    def convert_bcd(self, n, count):
        """Convert to bcd
        """
        n = int(n)
        bcd = []
        for i in range(count):
            bcd.append((n % 10) | ((n//10) % 10) << 4)
            n //= 100
        return bcd

    def send_com_core(self, c, data=False):
        """Send a command wrapper
        """
        com = [0xfe, 0xfe, self.radio_id, 0xe0, c]
        if(data):
            com += data
        com.append(0xfd)
        result = self.write_radio(com)
        return com

    def send_and_receive(self, c, data=False):
        """Send a command wrapper
        """
        com = [0xfe, 0xfe, self.radio_id, 0xe0, c]
        if(data):
            com += data
        com.append(0xfd)
        self.write_radio(com,True)
        return com

    def send_com(self, c, data=False):
        """Send a command
        """
        com = self.send_com_core(c, data)
        r = self.read_radio_response()
        if(not r):
            err = 'Error: ' + self.render_list_as_hex(com)
            self.debug_print(err)
        return r

    def set_memory_mode(self):
        """Change to memory mode
        """
        self.debug_print('set memory mode')
        self.send_com(0x08)

    def set_vfo(self, n):
        """Set the vfo
        """
        self.debug_print('set vfo: %d' % n)
        if(self.current_vfo != n):
            self.current_vfo = n
            self.send_com(0x07)  # select VFO mode (required for IC-756)
            # select VFO main/sub (required for IC-756)
            self.send_com(0x07, [0xd0 + n])
            return self.send_com(0x07, [n])  # select VFO

    
    def set_split(self, split, force=True):
        """Activate split mode
        01.24.2018 default force = True to avoid
        a default setting of split mode
        """
        if(force or self.split != split):
            c = (0, 1)[split]
            self.debug_print('set split mode: %d' % c)
            r = self.send_com(0x0f, [c])
            if(r):
                self.split = split
            return r

    def set_memory_bank(self, mb):
        """Set a memory Bank
        """
        if(mb != self.mem_bank):
            self.mem_bank = mb
            bcd = self.convert_bcd(mb, 1)
            # bcd.reverse()
            bcd = [0xa0] + bcd
            self.debug_print('set memory bank: %d : %s' %
                             (mb, self.render_list_as_hex(bcd)))
            return self.send_com(0x08, bcd)
        else:
            return True

    def set_memory_addr(self, m, banksize):
        """ Set a memory address
        """
        # the R8500 uses zero-based indexing
        # all other radios use 1-based
        offset = (1, 0)[self.r8500]
        if(banksize != 0):
            ma = m % banksize
            mb = m / banksize
            r = self.set_memory_bank(mb+offset)
            if(not r):
                self.debug_print('fail set memory bank: %d' % (mb+offset))
                return False
            bcd = self.convert_bcd(ma+offset, 2)
            bcd.reverse()
        else:
            bcd = self.convert_bcd(m+offset, 2)
            bcd.reverse()
        self.debug_print('set memory address: %d %s' %
                         (m, self.render_list_as_hex(bcd)))
        r = self.send_com(0x08, bcd)
        # user feedback
        sys.stdout.write('.')
        sys.stdout.flush()
        return r

    def pad_char(self, s, length, c):
        while(len(s) < length):
            s += c
        return s

    def set_memory_name(self, mem, banksize, mem_tag, radio_tag):
        """Set the memory name
        """
        self.debug_print('setting memory tag %s' % mem_tag)
        if(radio_tag in self.memory_label_sizes):
            tag_len = self.memory_label_sizes[radio_tag]
        else:
            self.debug_print('Fail mem tag on radio %s' % radio_tag)
            return
        # the R8500 uses zero-based indexing
        # all other radios use 1-based
        offset = (1, 0)[self.r8500]
        # special read com for the IC-R8500
        read_com = (0, 1)[self.r8500]
        if(banksize != 0):
            ma = mem % banksize
            mb = mem / banksize
            mab = self.convert_bcd(ma+offset, 2)
            mab.reverse()
            mbb = self.convert_bcd(mb+offset, 1)
            mbb.reverse()
            self.send_com_core(0x1a, [read_com] + mbb + mab)
        else:
            mab = self.convert_bcd(mem+offset, 2)
            mab.reverse()
            self.send_com_core(0x1a, [read_com] + mab)
        result = self.read_radio_s()
        if(result):
            rl = len(result)
            if(rl > tag_len):
                # limit tag size to max
                mem_tag = mem_tag[:tag_len]
                # extend tag length for short tags
                mem_tag = self.pad_char(mem_tag, tag_len, ' ')
                # convert from chars to numbers
                mem_tag = [ord(c) for c in mem_tag]
                delta = tag_len+1
                for n in range(tag_len):
                    result[-(delta - n)] = mem_tag[n]
                # to transmit the received data block,
                # must change order of sender and recipient
                temp = result[2]
                result[2] = result[3]
                result[3] = temp
                # for the IC-R8500, change com
                if(self.r8500):
                    result[5] = 0
                self.write_radio(result)
                r = self.read_radio_response()
                if(not r):
                    err = 'Error in set memory name: ' + \
                        self.render_list_as_hex(result)
                    self.debug_print(err)
                return r

            else:
                self.debug_print('wrong reply length in set memory name: %d %s' % (
                    rl, self.render_list_as_hex(result)))
        else:
            self.debug_print('fail from read_radio_s')

    def set_vfo_freq(self, n):
        """Set VFO frequency
        """
        f = (n * 1.0e6) + 0.5
        self.debug_print('set VFO freq: %f' % f)
        n = int(f)
        bcd = self.convert_bcd(n, 5)
        self.send_com(0x05, bcd)

    def set_vfo_tone(self, n, f):
        """Set VFO Tone
        """
        self.debug_print('set_vfo_tone',True)
        f = (f * 10.0) + 0.5
        f = int(f)
        bcd = self.convert_bcd(f, 2)
        bcd.reverse()
        bcd = [n] + bcd
        self.send_com(0x1b, bcd)

    def set_vfo_mode(self, s):
        """Set VFO Mode
        """
        self.debug_print('set VFO mode: %s %d' % (s, self.modes[s]))
        self.send_com(0x06, [self.modes[s]])

    def read_vfo_freq(self):
        """Read VFO Frequency
        """
        self.debug_print('Read VFO Freq:')

        self.send_and_receive(0x03)
        result = self.read_radio_s()
        freq = ""
        for i in range (9,4,-1):
            byte = hex(result[i])[2:]
            freq+=byte
        return freq





io = IcomIO()
io.process_radio('IC-7100')
result = io.init_serial()
#io.set_vfo_freq(145.50010)
#io.set_vfo_mode('usb')
if result:
    #io.set_vfo_freq(150.00000)
    #io.set_vfo_mode('usb')
    print(io.read_vfo_freq())
