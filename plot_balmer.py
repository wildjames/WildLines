#!/usr/bin/env python
#
#	James Wild, 2017
#
# Takes a spectrum, and a list of lines. Finds the lines in the spectra, cuts them out
#  and plot them on the same axis (offset progressively up) for comparison.
# Writes out to file, if you want
# To plot custom things, go to line 164
# TODO: MAKE THIS TAKE AN INPUT FILE???

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
import numpy as np
from matplotlib import rc
import time
import os
from LinesPlotLib import *

# Get the filename
fname = raw_input('Please enter a spectrum file: ')

# Ask if we want to write to a file, or diplay the plots on screen.
out = raw_input('print to file? y/n: ').lower()
if out == '':
	out = 'n'

# If we are writing to a file, we need some additional info
if out[0] == 'y':
	print 'Current file is: %s' % fname
	oname = raw_input('Enter filename prefix (can include folder): ')
	to_test = '/'.join(oname.split('/')[:-1])
	if to_test:
		print "I'll put the files in the following directory: %s" % to_test
		if not os.path.exists(to_test):
			time.sleep(0.3)
			os.makedirs(to_test)
else:
	oname = ''

# Line lists, hardcoded.
# Lines will be plotted in the order seen here. 
# If you want to pick out specific lines, new lists can easily be written.
Hlines  = [3970.078,
		   4101.7,
		   4340.4,
		   4861.29,
		   6562.72
		]
Hlabels = [r'H$\epsilon$',
		   r'H$\delta$',
		   r'H$\gamma$',
		   r'H$\beta$',
		   r'H$\alpha$'
		]

PGlines =  [1755.00,
            1313.10,
            2355.26,
            1251.39,
            1494.89,
            1500.61
        ]

PGLabels = [r'Pb IV 1755.0$\AA$',
            r'Pb IV 1313.1$\AA$',
            r'Ba II 2335.3$\AA$',
            r'Sn III 1251.4$\AA$',
            r'Ge IV 1494.9$\AA$',
            r'Ge IV 1500.6$\AA$'
            ]

generate_plots(PGlines, 'pg0909_Pb-Ba-Sn-Ge.fit', oname='PG0909+276_exotic_metals', N=6, labels=PGLabels, out='y')

# Generate the plots.
# generate_plots(Hlines, fname, oname=oname+'_Balmer-', N=5, labels=Hlabels, out=out)
# print 'Done balmer...'
    ### USAGE:
    ##  <lines>      - List of lines to plot
    ##  <fname>      - Spectrum filename.
    ## OPTIONAL ARGUMENTS ##
    ##  [wr]         - How far to extend the data, about the desired lines
    ##  [title]      - Title above the figure
    ##  [oname]      - File name to write to. If multiple images are created, they will be numbered
    ##  [N]          - Number of lines to include on a single figure
    ##  [labes]      - (Ordered!) list of custom labels to supply to the image
    ##  [offset]     - Offset incriment
    ##  [text_shift] - fractional shift inwards from the negative x axis limit
    ##  [out]        - y/n do we print to file? Default no.
    # Retrieve observations and model

print 'Finished!'