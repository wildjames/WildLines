# Function module for plot_balmer.py

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
import numpy as np
from matplotlib import rc
import time
import os

def setup_plot(title=None, wr=20, figsize=[3.15, 4], lpad=0.15, dpad=0.10, rpad=0.95, upad=0.90):
# Setup a figure plotting area, with the right parameters.
    # Alter rcparams to make the font not look as terrible, and enable latex.
    rc('font', **{'family':'serif','serif':['Palatino'],'size':8})
    rc('text', usetex=True)
    rc('lines', linewidth=0.75)
    
    # Initiate a figure and a set of axes, with the right size (INCHES), 
    #  and the padding defined by the user.
    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=lpad, right=rpad, top=upad, bottom=dpad)
    # If we have a title, add the title
    if title != None:
        plt.title(title)

    # By default, MPL tries to use the 'best' formatting it can.
    #   MPL is an idiot, and I know better.
    # Also add the ticks to the axes in a consistent way.
    ax.yaxis.set_minor_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.tick_params('both', length=10, width=1, which='minor', direction='inout', top='on', bottom='on',
        labelright='off', labelleft='on', labelbottom='on', labeltop='off')
    ax.tick_params('both', length=5,  width=1, which='major', direction='inout', top='on', bottom='on',
        labelright='off', labelleft='on', labelbottom='on', labeltop='off')
    # Label the axes
    plt.xlabel(r'$\lambda$ - $\lambda_0$ ($\mathrm{\AA}$)', fontsize=9)
    plt.ylabel('Relative Flux + c', fontsize=9)

    # Add a horizontal line at 0 to guide the eye to the correct lines.
    ax.axvline(x=0.0, alpha=0.3, color='black')
    # Set the X axis range
    ax.set_xlim(0-wr, wr)
    return fig, ax

def generate_plots(lines, fname, wr=20, title=None, oname='out', N=6, labels=None, 
    offset=0.5, text_shift=0.2, out='n', figsize=[3.15,4], lpad=0.90, dpad=0.10, 
    rpad=0.15, upad=0.95, v=0.0, cols=[0,1]):
# Generate the plots.
    ### USAGE:
    ##  <lines>      - list of lines to plot
    ##  <obs>        - Dict of data
    ##  <wr>         - How far to extend the data, about the desired lines
    ##  <title>      - Title above the figure
    ##  <oname>      - File name to write to. If multiple images are created, they will be numbered
    ##  <N>          - Number of lines to include on a single figure
    ##  <labes>      - (Ordered!) list of custom labels to supply to the image
    ##  <offset>     - Offset incriment
    ##  <text_shift> - fractional shift inwards from the negative x axis limit
    ##  <cols>       - columns to plot
    # Retrieve observations and model
    
    # Grab the data from the file
    obs = get_data(fname, v)
    
    # Setup the plotting area
    fig, ax = setup_plot(title, wr, figsize, lpad, dpad, rpad, upad)
    
    # Get the data from the spectrum, and push the bits we want into the right lists.
    pwl = []              #wl to plot
    pfx = []              #flux to plot
    wmax, wmin = 0.,0.    #Range boundaries
    s = 0.                #Initial offset.
    n = 1                 #counter
    colours = ['red', 'blue', 'green', 'magenta', 'brown']
    c = 0                 #colors looper
    if len(lines) <= N:
        number = ''       #Filename counter, if we will need it. Otherwise, dont bother.
    else:
        number = 1
    fmin = 10             #Min plot 
    text_pos = (wr) * (text_shift - 1) # Text location

    if labels == None:
        # Use wavelengths as labels
        labels = ['%.2f$\mathrm{\AA}$' % x for x in lines]
    else:
        # Ensure that the labels are all strings.
        labels = [str(i) for i in labels]

    upperlim = 1.0

    for line, label in zip(lines, labels):
        c = 0
        wmax = line+wr
        wmin = line-wr

        # Plot the observations, assumed to be the first column supplied
        pwl = []
        pfx = []
        for wl, flux in zip(obs[cols[0]], obs[cols[1]]):
            if wl > wmin and wl < wmax:
                pwl.append(wl-line)
                pfx.append(flux + s)
        plt.step(pwl, pfx, color='black')

        # Loop through the desired columns
        for Y in cols[2:]:
            # re-initialise plot variables
            pwl = []
            pfx = []
            # Get desired model columns
            for wl, flux in zip(obs[cols[0]], obs[Y]):
                if wl > wmin and wl < wmax:
                    pwl.append(wl-line)
                    pfx.append(flux + s)
            plt.plot(pwl, pfx, color=colours[c%len(colours)])
            c += 1
        
        plt.annotate(label,
                      xy=(text_pos,1.05+s),
                      xytext=(text_pos, 1.05+s)
                     )

        # Keep an eye on the upper limit
        if 1.1+s > upperlim:
            upperlim = s+1.1
            upperlim *= 1.03

        s += offset
        # Check if we need to go to the next figure. 
        # If we do, print out the current one and start the new one.
        if n%N == 0:
            ax.set_ylim(top=upperlim)
            if out == 'y':
                plt.savefig(oname+str(number)+'.pdf')
                print 'Wrote to <%s>' % (oname+str(number)+'.pdf')
                if len(lines) > N:
                    number += 1
            else:
                plt.show()
            fig, ax = setup_plot(title, wr, figsize, lpad, dpad, rpad, upad)
            s = 0.
        n += 1
    # Account for the last n incriment.
    n -= 1
    # If we have any residual plotted lines, show them.
    if n%N != 0:
        ax.set_ylim(top=upperlim)
        if out == 'y':
            plt.savefig(oname+str(number)+'.pdf')
            print 'Wrote to <%s>' % (oname+str(number)+'.pdf')
            if len(lines) > N:
                number += 1
        else:
            plt.show()
    plt.close()

def get_data(fnames, v=0.0):
# Read in the data, return lists of data
    obs = [[] for x in range(20)]
    for fname in fnames:
        with open(fname, 'r') as f:
            # Skip over header
            for i in range(3):
                f.readline()
            for line in f:
                line = [float(x) for x in line.split()]
                if len(line) > 20:
                    print 'You have way too many columns in that file. Please strip it down so I can handle it (max 20 columns)'
                
                # Push the values into the right places in the lists.
                i = 0
                for x in line:
                    obs[i].append(x)
                    i += 1

    # velocity correction
    c = 3e5
    obs[0] = [x*(1-(v/c)) for x in obs[0]]

    return obs