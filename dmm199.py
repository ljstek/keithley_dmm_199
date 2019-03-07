#!/usr/bin/python3
import numpy as np
import serial
import time

class keithley_m199:

    def __init__(self, device, baud, bus_id = 1, setup = 'F0R0S1T0Q0G2X'):
        self.device = device
        self.baud = baud
        self.bus_id = bus_id
        self._disp_chars = 10
        self.ser = serial.Serial(device, baudrate = baud)
        self.display() # reset display on init
        self.write(setup)
        self.curfunc = 'F0'
        time.sleep(2)

    def write(self, com):
        return self.ser.write(('W' + str(self.bus_id) + ',' + com + '\n').encode('ascii'))

    def bus_reset(self):
        return self.ser.write(b'C\n')

    def bus_byte(self, integer):
        return self.ser.write(('G' + str(int) + '\n').encode('ascii'))

    def bus_info(self):
        self.ser.write(b'I\n')
        return self.ser.readline()

    def bus_srq(self):
        self.ser.write(b'S\n')
        return self.ser.readline()

    def bus_timeout(self, t):
        return self.ser.write(('T' + t + '\n').encode('ascii'))

    def writeread(self, com = ''):
        self.ser.write(('R' + str(self.bus_id) + ',' + com + '\n').encode('ascii'))
        return self.ser.readline()

    def byte(self, integer):
        return self.ser.write(('B' + str(self.bus_id) + ',' + str(integer) + '\n').encode('ascii'))

    def databyte(self, integer):
        return self.ser.write(('D' + str(integer)).encode('ascii'))

    def display(self, com = ''):
        return self.write('D' + com + 'X\n')

    def _proc(self, resp):

        if resp[0:5] == b'Error':
            resp_type = b'Error'
            resp_val = resp[6:-2]
        else:
            resp_type = resp[0:4]
            resp_val = resp[4:-2]

        return {'type': resp_type, 'val': resp_val}

    def _err(self, resp):
        return resp['type'] == b'Error'

    def read_single(self, no_proc = False, val_only = False):
        self.trigger('cont', 'X')
        resp = self.writeread('X')
        return (self._proc(resp) if not val_only else float(self._proc(resp)['val'])) if not no_proc else resp

    def read_buffered(self, size, interval = 'default', dataformat = '+buf+pre-chan', raw = False, clear_when_done = True):
        self.readmode('all')
        self.format(dataformat)
        self.interval(interval)
        self.trigger('cont', 'X')
        self.datastore(size)

        self.write('X') # send a trigger
        time.sleep(size * (interval if isinstance(interval, int) else 175) * 1E-3)

        vals = self.writeread('')

        if clear_when_done:
            self.write('FX' + self.curfunc + 'X')

        if dataformat == '+buf+pre-chan' and not raw:
            spl_vals = str(vals)[2:].split(',')
            vals = []
            for i in range(int(len(spl_vals)/2)):
                vals.append(float(str(spl_vals[2*i])[4:]))
            vals = np.array(vals)

        return vals

    def volt_dc(self):
        self.func('DC_V')
        resp = self.read_single()

        if not self._err(resp):
            return float(resp['val'])
        else:
            print(resp)
            return np.NaN

    def func(self, f):
        funcs = {   'DC_V':     'F0',
                    'AC_V':     'F1',
                    'OHM':      'F2',
                    'DC_I':     'F3',
                    'AC_I':     'F4',
                    'AC_V_DB':  'F5',
                    'AC_I_DB':  'F6'
                }

        if f in funcs:
            self.curfunc = funcs[f]
            return self.write(funcs[f] + 'X')
        else:
            raise ValueError('Faulty function selection')
            return False;

    def range(self, r): # based off of the 'Ohms' column since thats the only one changing each row
        ranges = {  'auto':     'R0',
                    '300':      'R1',
                    '3k':       'R2',
                    '30k':      'R3',
                    '300k':     'R4',
                    '3M':       'R5',
                    '30M':      'R6',
                    '300M':     'R7'
                 }

        if r in ranges:
            return self.write(ranges[r] + 'X')
        else:
            raise ValueError('Faulty range selection')
            return False

    def zero(self, z):
        zeros = {   'disabled':     'Z0',
                    '0':            'Z0',
                    'enabled':      'Z1',
                    '1':            'Z1',
                    'enabled_zero': 'Z2',
                    '10':           'Z2'
                }

        z = str(z)
        if z in zeros:
            return self.write(zeros[z] + 'X')
        else:
            raise ValueError('Faulty zero selection')
            return False

    def filter(self, f):
        filters = { 'disabled':     'P0',
                    '0':            'P0',
                    'internal':     'P1',
                    'front':        'P2'
                  }

        f = str(f)
        if f in filters:
            return self.write(filters[f] + 'X')
        else:
            raise ValueError('Faulty filter selection')
            return False

    def rate(self, r):
        rates = {   '4.5':  'S0',
                    '5.5':  'S1'
                }

        if r in rates:
            return self.write(rates[r] + 'X')
        else:
            raise ValueError('Faulty rate/resolution selection')
            return False

    resolution = rate # alias

    def trigger(self, shot, when):
        shots = {   'continuous':   0,
                    'cont':         0,
                    'c':            0,
                    'single':       1,
                    's':            1
                }

        triggers = {    'TALK':     0,
                        'GET':      2,
                        'X':        4,
                        'EXT':      6
                   }

        if shot in shots and when in triggers:
            return self.write('T' + str(shots[shot] + triggers[when]) + 'X')
        else:
            raise ValueError('Faulty trigger selection')
            return False

    def readmode(self, r):
        readings = {    'A/D':          'B0',
                        'AD':           'B0',
                        'individual':   'B1',
                        'ind':          'B1',
                        'all':          'B2'
                   }

        r = str(r)
        if r in readings:
            return self.write(readings[r] + 'X')
        else:
            raise ValueError('Faulty reading mode selection')
            return False

    def datastore(self, s):
        sizes = {'wrap':     'I0'}

        if s in sizes:
            return self.write(sizes[wrap] + 'X')
        elif isinstance(s, int) and s > 0 and s < 501:
            return self.write('I' + str(s) + 'X')
        else:
            raise ValueError('Faulty data store size selection')
            return False

    def interval(self, i):
        intervals = {'default': 'Q0'}

        if i in intervals:
            return self.write(intervals[i] + 'X')
        elif isinstance(i, int) and i > 14 and i < 1E6:
            return self.write('Q' + str(i) + 'X')
        else:
            raise ValueError('Faulty interval selection')
            return False

    def format(self, f):
        formats = { '-buf+pre-chan':        'G0',
                    '-buf-pre-chan':        'G1',
                    '+buf+pre-chan':        'G2',
                    '+buf-pre-chan':        'G3',
                    '-buf+pre+chan':        'G4',
                    '-buf-pre+chan':        'G5',
                    '+buf+pre+chan':        'G6',
                    '+buf-pre+chan':        'G7'
                  }

        if f in formats:
            return self.write(formats[f] + 'X')
        else:
            raise ValueError('Faulty output format selection')
            return False

    def set_srq(self, s):
        srqs = {    'disabled':         'M0',
                    '0':                'M0',
                    'off':              'M0',
                    'read_overflow':    'M1',
                    'data_store_full':  'M2',
                    'data_store_half':  'M4',
                    'reading_done':     'M8',
                    'ready':            'M16',
                    'error':            'M32'
               }

        if s in srqs:
            return self.write(srqs[s] + 'X')
        else:
            raise ValueError('Faulty SRQ selection')
            return False

    def delay(self, d):
        d = int(d)

        if d < 0 or d > (1E6 - 1):
            raise ValueError('Delay out of bounds (0 < d < 1E6)')
            return False

        return self.write('W' + str(d) + 'X')

    def selftest(self):
        return self.write('J0')

    def hit(self, n):
        n = int(n)
        return self.write('H' + str(n) + 'X')

    def text_flash(self, msgloop, t = 0.15, N = 0):

        msgloop = msgloop.split(' ')

        i = 0
        while(True):

            this_msg = msgloop[i % len(msgloop)]

            self.display(this_msg + 'X')
            time.sleep(t)
            i = i+1

            if N*len(msgloop) == i:
                self.display()
                break;

        return None

    def text_marquee(self, msgloop, t = 0.15, delim = ' - ', space = '_', N = 0):

        msgloop = msgloop + delim

        i = 0
        while(True):

            this_msg = ''
            for j in range(self._disp_chars):
                this_msg = this_msg + msgloop[(i+j) % len(msgloop)]

            this_msg = this_msg.replace(' ', space)

            self.display(this_msg)
            time.sleep(t)
            i = i+1

            if N*len(msgloop) == i:
                self.display()
                break;

        return None

    def save(self, filename, data, mode = 'a', newline = '\n'):
        with open(filename, mode) as datafile:
            datafile.write(','.join([str(datum) for datum in data]) + newline)
