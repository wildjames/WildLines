# Function module for plot_balmer.py

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
import numpy as np
from matplotlib import rc
import time
import os

def setup_plot(title=None, wr=20):
# Setup a figure plotting area, with the right parameters.
    # Alter rcparams to make the font not look as terrible, and enable latex.
    rc('font', **{'family':'serif','serif':['Palatino'],'size':10})
    rc('text', usetex=True)
    rc('lines', linewidth=0.75)
    
    fig, ax = plt.subplots(figsize=(3.15,4))
    if title != None:
        fig.subplots_adjust(left=0.15, right=0.95, top=0.94, bottom=0.12)
        plt.title(title)
    else:
        fig.subplots_adjust(left=0.15, right=0.95, top=0.97, bottom=0.12)

    ax.yaxis.set_minor_formatter(FormatStrFormatter('%d'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.xlabel(r'Wavelength ($\mathrm{\AA}$)', fontsize=11)
    plt.ylabel('Normalised Flux', fontsize=11)
    ax.tick_params('both', length=10, width=1, which='minor', direction='inout', top='on', bottom='on', 
        labelright='off', labelleft='on', labelbottom='on', labeltop='off')
    ax.tick_params('both', length=5,  width=1, which='major', direction='inout', top='on', bottom='on', 
        labelright='off', labelleft='on', labelbottom='on', labeltop='off')
    ax.axvline(x=0.0, alpha=0.3, color='black')
    ax.set_xlim(0-wr, wr)
    return fig, ax

def generate_plots(lines, fname, wr=20, title=None, oname='out', N=6, labels=None, offset=0.5, text_shift=0.2, out='n'):
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
    # Retrieve observations and model
    
    # Grab the data from the file
    obs = get_data(fname)

    # Setup the plotting area
    fig, ax = setup_plot(title, wr)
    wl   = obs['wl']
    fobs = obs['fobs']
    fgen = obs['fgen']

    pwl = []              #wl to plot
    pfo = []              #obs to plot
    pfg = []              #gen to plot
    wmax, wmin = 0.,0.    #Range boundaries
    s = 0.                #Initial offset.
    n = 1                 #counter
    number = 0            #Filename counter
    fmin = 10             #Min plot  
    text_pos = -wr + (wr*text_shift)

    if labels == None:
        # Use wavelengths as labels
        labels = ['%.2f$\mathrm{\AA}$' % x for x in lines]
    else:
        # Ensure that the labels are all strings.
        labels = [str(i) for i in labels]
    # scan through the list of lines and pull out sections about the wavelengths we want.
    for i, label in zip(lines, labels):
        # Reset variables
        pwl = []
        pfo = []
        pfg = []
        wmax = i+wr
        wmin = i-wr
        # search the wavelength lists
        for j,k,l in zip(wl, fobs, fgen):
            if j > wmin and j < wmax:
                pwl.append(j-i)
                pfo.append(k+s)
                pfg.append(l+s)
                if pfo[-1] < fmin:
                    fmin = pfo[-1]
        plt.step(pwl, pfo, color='black')
        plt.plot(pwl, pfg, color='red')

        plt.annotate(label,
                      xy=(text_pos,1.1+s),
                      xytext=(text_pos, 1.1+s)
                     )
        
        s += offset
        if n%N == 0:
            ax.set_ylim(top=(s+0.8))
            if out == 'y':
                plt.savefig(oname+str(number)+'.pdf')
                number += 1
            else:
                plt.show()
            fig, ax = setup_plot(title)
            s = 0.
        n += 1
    n -= 1
    if n%N != 0:
        plt.show()
    plt.close()

def get_data(fname):
# Read in the data, return dict of data
    wl = []
    fobs = []
    fgen = []
    with open(fname, 'r') as f:
        for i in range(3):
            f.readline()
        for line in f:
            line = [float(x) for x in line.split()]
            wl.append(line[0])
            fobs.append(line[1])
            fgen.append(line[3])
    # velocity correction
    v = 28.898 # float(input('Please enter a velocity shift: '))
    c = 3e5
    wl = [x*(1-(v/c)) for x in wl]

    #Store data in a dict
    obs = {'wl': wl,
           'fobs': fobs,
           'fgen': fgen
           }
    return obs
