

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

mwrite('\x03', 1)
mwrite('\x03', 1)
mwrite('apos', 1)
mwrite('p', 1)    

c = 0
c_limit = 30

while True:

    l = s.read()

    if l[0:4].decode('utf-8') == id:
        a = l.split()
        if (b'RT' in a) and (b'C' in a):
            print(c, '>>', l.decode('utf-8'))
            c += 1
            if c > c_limit:
                break
        else:
            print(l)

mwrite('p', 1)                
mwrite('\0x03', 1)
s.close()