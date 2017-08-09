#!/usr/bin/env python
#
#   James Wild, 2017
#
# Takes a columnated file from the user, and plot deisred columns. Assumes the zeroth column is wavelength, 
#  and since it's designed for spectra we plot the Y axis as a relative flux.
# Also has the option to write to a file.


import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
from matplotlib import rc
from cycler import cycler

# Alter rc parameters
rc('text', usetex=True)
rc('lines', linewidth=0.75)
# Cycle through colours
rc('axes', prop_cycle=(cycler('color', ['r', 'b', 'g', 'y'])))


### FIGURE SIZE (INCHES) ###
plt.rcParams["figure.figsize"] = (7,  4) # (width, height)
plt.rcParams["figure.figsize"] = (3.5,4) # two column size
### Y RANGE              ###
yyrange = [0.0, 1.2]
### FONT SIZE! IF YOU CHANGE THE FIGSIZE DRAMATICALLY, YOU PROBABLY WANT TO CHANGE THIS TOO
rc('font', **{'family':'sans','serif':['DejaVu'],'size':11})


## Set up the plotting area to look nice
fig, ax = plt.subplots()
# Define the percentages of the plot to leave at the sides.
fig.subplots_adjust(left=0.15, right=0.95, top=0.97, bottom=0.11)
# Define the formatting of the axis labels
ax.yaxis.set_minor_formatter(FormatStrFormatter('%d'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# Ticks. length is in pixels, other parameters are self-explainatory.
ax.tick_params('both', length=10, width=1, which='minor', direction='inout', top='on', bottom='on', 
    labelright='off', labelleft='on', labelbottom='on', labeltop='off')
ax.tick_params('both', length=5,  width=1, which='major', direction='inout', top='on', bottom='on', 
    labelright='off', labelleft='on', labelbottom='on', labeltop='off')

# X and Y labels. Accepts TeX formatting
plt.xlabel(r'Wavelength (${\mathrm \AA}$)')
plt.ylabel(r'Relative Flux')

# Get the filename from the user, as well as the delimiter for the columns
# raw_input so the code doesn't try to automatically convert the input to a type, just use string
flag = False
while not flag:
    fname = raw_input('Please enter filename: ')
    flag = os.path.isfile(fname)
    if not flag:
        if raw_input("Couldn't find that file! try again? [y/n]: ").lower() == 'y':
            exit()

delimiter = raw_input("Column delimiter (default is ' '): ")
if delimiter == '':
    delimiter = None

# Scan the file, and find out the mean number of columns
i = 0
j = 0
with open(fname, 'r') as f:
    for line in f:
        i += len(line.split(delimiter))
        j += 1
ncol = int(round(float(i)/float(j)))
print 'The file has %d columns' % (ncol)

# Read in the file to data. data[0] will be 0th column, data[1] is first col, etc.
data = []
for i in range(ncol):
    data.append([])
with open(fname, 'r') as f:
    for line in f:
        if len(line.split(delimiter)) == ncol:
            line = (line.split(delimiter))
            for i in range(ncol):
                data[i].append(float(line[i]))

# Get the user to input which columns they want to plot
print "I'll assume the zeroth column is X data..."
nY = ncol
# Ensure that the number of columns to plot isnt more than we have with a while loop
while nY >= ncol:
    if nY > ncol:
        print 'nY cannot exceed nCol (%d).' % ncol
    nY = raw_input('How many Y data do you want to plot? I assume the first entry are observations: ')
    while type(nY) != int:
        try:
            nY = int(nY)
        except:
            print "Couldn't get a number from that..."
            nY = raw_input('How many Y data do you want to plot?: ')

# Ask the user which columns they want
desiredY = []
for i in range(nY):
    temp = ncol+1
    while temp >= ncol:
        temp = raw_input('Column number > ')
        while type(temp) != int:
            try:
                temp = int(temp)
            except:
                print "Couldn't get a number from that..."
                temp = raw_input('Column number > ')
        if temp >= ncol:
            print 'Cannot exceed nCol (%d)' % (ncol-1)
    desiredY.append(temp)

# Plot the observations
if nY == 1:
    alpha = 1.0
else:
    alpha = 0.5
plt.step(data[0], data[desiredY[0]], color='black', alpha=alpha)
desiredY = desiredY[1:]

# for each additional column, plot it too
for i in desiredY:
    plt.plot(data[0], data[i])

# Get the desired X range from the user
xxrange = raw_input('Enter an X range, in the form <xxxx xxxx>: ')
while len(xxrange) != 2:
    try:
        xxrange = [float(x) for x in xxrange.split()]
    except:
        print "Whoops! Couldn't get a range from that."
        xxrange = raw_input('Enter an X range, in the form <xxxx xxxx>: ')

ax.set_xlim(xxrange)
ax.set_ylim(yyrange)

print 'S key to save the figure, or click the button'
plt.show()