

#from bokeh.plotting import figure

#p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])

import time
import atexit
from gserial import gserial
from gserial import scan

ss = scan.Scan()
ss.scan()
print('All ports found:')
print(ss.current_ports)

id = '0005'

i = scan.ID(hint=[id, 'pCO2'], poll=b'\r')
i.baudrates = [9600]
p, b = i.get(verbose=True)
print('Port found with config:', p, b)

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
                print('{:02d}'.format(i), '>>', line.decode('utf-8'))
                i += 1
                if i > i_limit:
                    i = 0
                    break

mwrite('\0x03', 3)
s.close()