

#from bokeh.plotting import figure

#p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])

from gserial import scan

ss = scan.Scan()
ss.scan()
print('All ports found:')
print(ss.current_ports)

i = scan.ID(hint=['0005', 'pCO2'], poll=b'\r')
i.baudrates = [9600]
p, b = i.get(verbose=True)
print('Port found with config:', p, b)