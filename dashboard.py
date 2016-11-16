

#from bokeh.plotting import figure

#p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])

import time
import atexit
import queue
import json
from gserial import gserial
from gserial import scan


class TermData(object):
    def __init__(self):
        self.zpon = queue.Queue()
        self.zpof = queue.Queue()
        self.spon = queue.Queue()
        self.spof = queue.Queue()
        self.epon = queue.Queue()
        self.epof = queue.Queue()
        self.apon = queue.Queue()
        self.apof = queue.Queue()

class TermTest(object):
    def __init__(self, id):
        self.id = id
        self.ss = scan.Scan()
        self.baudrates = [9600]
        self.data = queue.Queue()
        
    
    def current_ports(self, verbose=False):
        self.ss.scan()
        if verbose:
            print('All ports found:')
            print(self.ss.current_ports)            
        return self.ss.current_ports
        
    def scan_ports(self, verbose=False):
        i = scan.ID(hint=[self.id, 'pCO2'], poll=b'\r')
        i.baudrates = self.baudrates
        p, b = i.get(verbose=verbose)
        if verbose:
            print('Port found with config:', p, b)
        return p, b
        
#ss = scan.Scan()
#ss.scan()
#print('All ports found:')
#print(ss.current_ports)
#
#id = '0005'

#i = scan.ID(hint=[id, 'pCO2'], poll=b'\r')
#i.baudrates = [9600]
#p, b = i.get(verbose=True)
#print('Port found with config:', p, b)

pt = TermTest(id='0005')
pt.current_ports(verbose=True)
p, b = pt.scan_ports(verbose=True)

s = gserial.GenericSerial(port=p, br=b)
s.open()
atexit.register(s.close)

def mwrite(x, n):
    s.write(bytes(x, 'utf-8') + b'\r')
    time.sleep(n)

mwrite('\x03', 2)
mwrite('\x03', 2)
mwrite('apos', 2)  # this will be redundant but gets into test loop

cycles = (('ZERO', 'z'),
          ('SPAN', 's'),
          ('EQUIL', 'e'),
          ('AIR', 'a'))

i = 0
i_limit = 10

location = 'room_1066'

for cycle, c in cycles:
    mwrite(c, 2)
    p_s = (('ON', 'p'), ('OFF', 'p'))
    for state, p in p_s:
        mwrite(p, 3)
        print('==== ', cycle, 'PUMP', state, '====')
        while True:        
            line = s.read()
            a = line.split()
            if (b'RT' in a) and (b'C' in a):
                count = '{:03d}'.format(i)
                line_utf8 = line.decode('utf-8')
                print(count, '>>', line_utf8)
                # TODO: establish json format
                data = {'time': time.time(),
                        'location': location,
                        'count': count,
                        'cycle': cycle,
                        'pump': state,
                        'data': line_utf8}
                print(json.dumps(data))
                i += 1
                if i > i_limit:
                    i = 0
                    break

mwrite('\0x03', 3)
s.close()