#!/usr/bin/env python
# TODO: add in functionality for generating a STERNE model??

import numpy as np
import os
import signal
import subprocess
import fnmatch
import time

import matplotlib.pyplot as mpl
from matplotlib.ticker import FormatStrFormatter
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rc

from Tkinter import *
import tkFileDialog
import tkMessageBox
import threading
from ScrolledText import *

class mplplotter():

    def __init__(self, finput=None, flines=None, fname=None, idfile=None):
        print "James Wild's matplotlib plotting tool, designed for use with SFIT - Press 'h' to show the controls."

        # Set up our matplotlib stuff
        # rc('font', **{'family':'serif','serif':['Palatino']})
        rc('font', **{'size':11})
        rc('text', usetex=False)
        rc('lines', linewidth=0.75)
        mpl.rcParams['keymap.xscale'] = ''
        mpl.rcParams['keymap.yscale'] = ''
        mpl.rcParams['keymap.forward'] = ''
        mpl.rcParams['keymap.back'] = ''
        mpl.rcParams['keymap.fullscreen'] = ''

        # Resize terminal window
        print "\x1b[8;15;140t"

        # print 'init'
        self.finput = finput
        self.flines = flines
        self.fname  = fname
        self.idfile = idfile
        self.interval = 10.
        self.v = 0.0
        self.get_files(finput=finput, fname=fname, flines=flines, idfile=idfile)

        # Enforce that we pick a fit file, otherwise what would we plot?
        while self.fname == None or self.fname == 'None':
            choice = raw_input('No fit file entered, I need one to start. Run SFIT with current parameters, Select a new file, or quit? [r/s/q] > ').lower()
            if choice == 'q':
                exit()
            elif choice == 'r':
                if self.finput == None or self.flines == None:
                    print 'You need to choose some inputs for sfit first!'
                else:
                    run = 'Sfit.csh %s %s' % (self.finput, self.flines)
                    print '\nUsing the command:\n'+run+'\n'
                    self.sfit = subprocess.Popen(run.split(), preexec_fn=os.setsid)
                    # Wait for SFIT to finish, then ask the user for files again.
                    self.sfit.wait()
                    self.get_files(fname=self.fname, flines=self.flines, finput=self.finput, idfile=self.idfile, interval=self.interval, v=self.v)
            elif choice == 's':
                self.get_files(fname=self.fname, flines=self.flines, finput=self.finput, idfile=self.idfile, interval=self.interval, v=self.v)

        #Initialise the subprocess for SFIT
        if self.finput != None and self.flines != None:
            self.run = 'Sfit.csh %s %s' % (self.finput, self.flines)
            self.sfit = subprocess.Popen('echo SFIT initialised'.split())
            self.sfit.wait()
            print '\nUsing the command:\n'+self.run+'\n'
        else:
            print 'No SFIT files supplied.'

        # Flag for labels, list for line labels
        self.labels_flag = False
        self.idlines = []
        self.plotted_labels = []

        # Element list
        self.elem = ['D' ,'H',                                                                            'He',
                     'Li','Be',                                                  'B' ,'C' ,'N' ,'O' ,'F' ,'Ne',
                     'Na','Mg',                                                  'Al','Si','P', 'S' ,'Cl','Ar',
                     'K' ,'Ca','Sc','Ti','V' ,'Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr',
                     'Rb','Sr','Y' ,'Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I' ,'Xe',
                     'Cs','Ba',
                     'La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',
                                    'Hf','Ta','W' ,'Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn',
                     'Fr','Ra',
                     'Ac','Th','Pa','U' ,'Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr',
                                    'Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Uut','Fl','Uup','Lv','Uus','Uuo']

        # Get the original data
        self.input_data = self.read_data(self.fname, self.v, report=True)
        
        #Setup the plotting zone
        self.spawn_plot()

        #Grab the first chunk of data we want to plot, and pop it to the right objects
        self.window(self.input_data['wobs'][0], self.interval)
        self.window(self.input_data['wobs'][0], self.interval)

        # Show it off
        mpl.show()

    def press(self, event):
    # Key commands
        if event.key == 'q':
        # Quit the program
            mpl.close()
            try:
                os.killpg(os.getpgid(self.sfit.pid), signal.SIGTERM)
                print 'SFIT process killed'
            except:
                if self.sfit.poll() > 0:
                    print 'I failed to kill SFIT. Is it still running?'
            exit()
        
        elif event.key == 'r':
        # Refresh the data
            self.refresh_data()
            self.redraw()
            print 'Refreshed data!'

        elif event.key == 'R':
        # Reload the data, and redraw the plot from scratch. Sometimes is necessary.
            zero = self.ax.get_xlim()[0]
            mpl.close()
            self.input_data = self.read_data(self.fname, self.v)
            self.spawn_plot()
            
            self.window(zero, self.interval)
            self.window(zero, self.interval)

            mpl.show()


        elif event.key == 'left':
        # Pan left by a step size of <self.interval>
            current_window = self.ax.get_xlim()
            interval = self.interval
            if current_window[0]-interval >= self.input_data['wobs'][0]:
                self.window(current_window[0]-interval, interval)
                self.redraw()
        elif event.key == 'right':
        # Pan right
            # t0 = time.clock()
            current_window = self.ax.get_xlim()
            interval = self.interval
            if current_window[1] < self.input_data['wobs'][-1]:
                self.window(current_window[0]+interval, interval)
                self.redraw()
                # print 'Shifting took %fs\n' % (time.clock() - t0)

        elif event.key == 'w':
            self.window(self.input_data['wobs'][0], self.interval)
            self.redraw()
        elif event.key == 'e':
            self.window(self.input_data['wobs'][-1]-self.interval, self.interval)
            self.redraw()

        elif event.key == 'up':
        # Increase the window size
            self.interval += 1.0
            self.refresh_data()
            self.redraw()
        elif event.key == 'down':
        # Decrease the window size
            self.interval -= 1.0
            self.refresh_data()
            self.redraw()

        elif event.key == ' ':
        # Print the files we're using
            self.report_files()

        elif event.key == 'u':
        # Run SFIT
            self.run_sfit()

        elif event.key == 'k':
        # Kill a running SFIT process
            self.kill_sfit()

        elif event.key == 'l':
        # Toggles showing labels
            self.labels_flag = not self.labels_flag
            self.refresh_data()
            self.redraw()

        elif event.key == 'L':
        # Get new lines to label
            self.get_labels()

        elif event.key == 'n':
        # Open a new notepad
            try:
                self.root.destroy()
            except:
                True
            self.root = Tk(className="Input file")
            self.notepad()

        elif event.key == 'f':
            self.get_files(fname=self.fname, flines=self.flines, finput=self.finput, idfile=self.idfile, interval=self.interval, v=self.v)

        elif event.key.lower() == 'h':
            self.help()

    def help(self):
        print 'Keyboard controls:'
        print ''
        print 'h - Show this message'
        print 'q - Quit this program'
        print 'r - Refresh data, and redraw the plot'
        print 'R - Close the plot, refresh the data, and reopen the plot'
        print 'L - Choose an element to label'
        print 'l - Toggle showing labels'
        print ''
        print 'u - Run SFIT'
        print "k - Kill SFIT, if it's running"
        print "f - Re-enter files for SFIT to use"
        print ''
        print 'left/right - Scan through the spectrum'
        print 'w/e        - Skip to the beginning/end of the spectrum'
        print 'up/down    - Increase/decrease the window size'
        print 'space      - Print the current input files'
        print ''
        print 'n - Open a notepad with the SFIT input file loaded into it'
        print 'Click on a location to print its values to the terminal'
        print ''

    def get_labels(self):
    # Takes a desired ion, and an eq. W threshold and appends a list to self.idlines() of the labels in the form [labels, locations]
        if len(self.idlines) != 0:
            print 'You currently label the following:'
        i=0
        for lines in self.idlines:
            print '%2d - Z: %s / Thresh: %f' % (i, ', '.join(map(str, lines[2])), lines[3])
            i += 1
        
        idfile = self.idfile
        if idfile == '' or idfile == None:
            print 'No linefile entered!'
            return

        # Get the element we want to label, and the eq. width threshold to apply to it
        try:
            desired = raw_input('Enter the Z of an element to label (space separated numbers are accepted): ')
            desired = map(int, desired.split())
            thresh  = float(raw_input('Enter the minimum eq. width: '))
        except:
            print 'Bad input.'
            return

        # To stop this script from wrecking the ram too much, read in only the lines that we actually want, rather than storing the whole damn thing
        #       [Z IZ, WL, input, threshold]
        lines = [[],[],desired,thresh]
        with open(idfile, 'r') as f:
            f.readline()
            f.readline()
            for line in f:
                line = [float(x) for x in line.replace('-', ' -').split()]
                if line[0] in desired and line[10]>=thresh:
                    line[1] = self.num2roman(int(line[1]))
                    line[0] = self.elem[int(line[0])]
                    lines[0].append(str(line[0]) + ' ' + str(line[1]) )
                    lines[1].append(float(line[2]))

        # idlines is a list of lines lists
        self.idlines.append(lines)

    def label_lines(self, xr):
    # Plots the labels contained in self.idlines(), which are in the window [xr]
        #         [label, wav, color]
        to_plot = [[],[],[]]
        color = 'black'

        # For each entry in idlines, pull out the data in the right window
        for lines in self.idlines:
            k = lines[2]
            for i,j in zip(lines[0], lines[1]):
                if j < xr[1] and j > xr[0]:
                    to_plot[0].append(i)
                    to_plot[1].append(j)
                    if k[0] < 3:
                        color = 'red'
                    elif k[0] > 2 and k[0] < 20:
                        color = 'blue'
                    elif k[0] > 19:
                        color = 'green'
                    to_plot[2].append(color)

        # Plot labels.
        size = self.fig.get_size_inches()*self.fig.dpi
        size = [float(x) for x in size]
        txt_height = (50./size[1])*(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])
        txt_width  = (15./size[0])*(self.ax.get_xlim()[1] - self.ax.get_xlim()[0])
        text_positions = self.get_text_positions(to_plot[1], [1.1 for x in to_plot[1]], txt_width, txt_height)
        self.plotted_labels.append(self.text_plotter(to_plot[1], [1.0 for x in to_plot[1]], text_positions, self.ax, txt_width, txt_height, to_plot[0], to_plot[2]))

    def clear_label_cache(self):
        print 'Clearing label cache data!'
        self.remove_labels()
        self.idlines=[]

    def remove_labels(self):
    # Removes all labels from the plot
        try:
            for i,j in self.plotted_labels:
                for k in i:
                    k.remove()
                for l in j:
                    l.remove()
            self.plotted_labels = []
            self.redraw()
        except:
            print 'Failed to remove lines!'

    def get_text_positions(self, x_data, y_data, txt_width, txt_height):
    # Copypasted from stack exchange...
    # Works out how to put labels on the plot without them overlapping.
    # Returns a list of these postions that can be passed to the text_plotter function
        a = zip(y_data, x_data)
        text_positions = y_data


        for index, (y, x) in enumerate(a):
            # Gets a list of the data that overlap the label we are considering
            local_text_positions = [i for i in a if i[0] > (y - txt_height) 
                                        and (abs(i[1] - x) < txt_width * 2) and i != (y,x)]

            if local_text_positions:
                # Sort the positions, to make the positions line up better later
                sorted_ltp = sorted(local_text_positions)

                if abs(sorted_ltp[0][0] - y) < txt_height: #True == collision
                    # differ is a list of the distances between the text boxes
                    differ = np.diff(sorted_ltp, axis=0)
                    # edit the list of data, a, to shift the y data up by txt_height
                    a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                    
                    text_positions[index] = sorted_ltp[-1][0] + txt_height
                    for k, (j, m) in enumerate(differ):
                        #j is the vertical distance between words
                        if j > txt_height * 2: #if True then room to fit a word in
                            a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                            text_positions[index] = sorted_ltp[k][0] + txt_height
                            break
        return text_positions

    def text_plotter(self, x_data, y_data, text_positions, axis,txt_width,txt_height,text_labels,colors):
    # Plots labels at a provided x,y coords, given the widths and heights.
    # returns a list of the objects created, allowing manipulation of them later.
        holder = [[],[]]
        for x,y,t,l,col in zip(x_data, y_data, text_positions, text_labels,colors):
            holder[0].append(axis.text(x - (txt_width/2), t+txt_height, str(l),rotation=90, color=col))

            # If the textheight goes above the plot's upper limit, rescale the axis to capture it. This significantly slows the redraw process
            if t+txt_height > self.ax.get_ylim()[1]:
                self.ax.set_ylim([0., t+txt_height])

            if y != t:
                holder[1].append(axis.arrow(x, t,0,y-t, color='red',alpha=0.2, 
                            head_width=txt_width*0.2, head_length=txt_height*0.2, zorder=0,length_includes_head=True))
        return holder

    def num2roman(self, num):
    # Convert an integer to roman numerals for idlabel
        roman = ''
        num_map = [(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        while num > 0:
            for i, r in num_map:
                while num >= i:
                    roman += r
                    num -= i
        return roman

    def click(self, event):
    # When the user clicks on a point, report the values at that point.
    # TODO: Have a second threshold for labelling lines, and when the user right-clicks,
    #  label extra lines about that point?
        if event.xdata != None and event.ydata != None:
            print 'Wavelength: %f\nFlux:       %f\n' % (event.xdata, event.ydata)

    def redraw(self):
    # I got sick of forgetting to prefix this with 'self' so I use this as a shorthand.
        # t0 = time.clock()
        self.fig.canvas.draw_idle()
        # print 'Drawing took %fs' % (time.clock() - t0)

    def refresh_data(self):
    # Re-reads in data, then populates the plot with it.
        self.input_data = self.read_data(self.fname, self.v)
        self.current_window = self.ax.get_xlim()
        self.obsdata = self.window(self.current_window[0], self.interval)
        self.fitdata = self.window(self.current_window[0], self.interval)
        return

    def report_files(self):
    # Print the inputs that we're currently working with.
        print ''
        print 'Using files:'
        print 'Fit file:       %s' % self.fname
        print 'Linefile:       %s' % self.flines
        print 'Input file:     %s' % self.finput
        print 'Window range:   %.2f' % self.interval
        print 'Velocity Shift: %.2gkm/s' % self.v
        print ''

    def get_files(self, fname=None, flines=None, finput=None, idfile=None, interval=10.0, v=0.0):
    # Takes a list of 5 filenames, and sill search the current directory for files
    #  that match the correct suffixes. 
    # Also allows for manual entry of names.

        #Set up inital values. Is there a prettier way of doing this?
        if fname:
            fnames = [fname]
        else:
            fnames = ['None']

        if flines:
            fliness = [flines]
        else:
            fliness = ['No Linefile']

        if finput:
            finputs = [finput]
        else:
            finputs = ['No SFIT control file']

        if idfile:
            idfiles = [idfile]
        else:
            idfiles = ['No SPECTRUM line file']

        oint    = interval
        ov      = v

        search = raw_input('Search current directory automatically, or enter files manually? (s/m/-): ').lower().strip()
        if search == 's':
            # fname
            for root, dirnames, filenames in os.walk('.', followlinks=True):
                for filename in fnmatch.filter(filenames, '*.fit'):
                    fnames.append(os.path.join(root,filename))
            fnames[1:] = sorted(fnames[1:])
            
            for i in range(len(fnames)):
                print '%d: %s' % (i,fnames[i])
            try:
                search = int(raw_input('Select a prior fit file: '))
            except:
                search = 0
            
            fname = fnames[search]
            print 'fit file:   %s\n' % fname
            time.sleep(1)

            #flines
            for root, dirnames, filenames in os.walk('.', followlinks=True):
                for filename in fnmatch.filter(filenames, '*.lte'):
                    fliness.append(os.path.join(root,filename))
            fliness[1:] = sorted(fliness[1:])
            for i in range(len(fliness)):
                print '%d: %s' % (i,fliness[i])
            
            try:
                search = int(raw_input('Select a line file: '))
            except:
                search = 0
            
            flines = fliness[search]
            print 'Line file:  %s\n' % flines
            time.sleep(1)

            #finput
            for root, dirnames, filenames in os.walk('.', followlinks=True):
                for filename in fnmatch.filter(filenames, '*.sfit'):
                    finputs.append(os.path.join(root,filename))
            finputs[1:] = sorted(finputs[1:])
            for i in range(len(finputs)):
                print '%d: %s' % (i,finputs[i])
            try:
                search = int(raw_input('Select an input file: '))
            except:
                search = 0
            
            finput = finputs[search]
            print 'Input file: %s\n' % finput
            time.sleep(1)

            #spectrum file
            for root, dirnames, filenames in os.walk('.', followlinks=True):
                for filename in fnmatch.filter(filenames, '*.000'):
                    idfiles.append(os.path.join(root,filename))
            idfiles[1:] = sorted(idfiles[1:])
            for i in range(len(idfiles)):
                print '%d: %s' % (i,idfiles[i])
            try:
                search = int(raw_input('Select an input file: '))
            except:
                search = 0
            
            idfile = idfiles[search]
            print 'Spectrum output file: %s\n' % idfile
            time.sleep(1)



            #interval
            interval = raw_input('Enter an interval size (if no value is entered, I will use %.2f): ' % oint)
            if interval == '':
                interval = oint
            else:
                interval = float(interval)

            #velocity
            v = raw_input('Enter a velocity shift (if no value is entered, I will use %.2f): ' % ov)
            if v == '':
                v = ov
            else:
                v = float(v)

        #Manual entry, like a caveman.
        elif search == 'm':
            search = str(raw_input('Enter a .fit file: '))
            if search != '':
                fname = search
            search = str(raw_input('Enter a file line list: '))
            if search != '':
                flines = search
            search = str(raw_input('Enter an input file: '))
            if search != '':
                finput = search
            search = str(raw_input('Enter a spectrum lines file: '))
            if search != '':
                idfile = search
            search = str(raw_input('Enter a velocity shift: '))
            if search != '':
                v = float(search)
        else:
            self.report_files()
        
        self.fname = fname
        self.flines = flines
        self.finput = finput
        self.interval = float(interval)
        self.idfile = idfile
        self.v = float(v)

        # Update the notepad with the new input file, if possible
        try:
            self.update_notepad(finput)
            self.open_filename = finput
        except:
            True

        return(fname, flines, finput, float(interval), float(v))

    def read_data(self, fname, v=0.0, report=False):
    # Reads in a spectrum file (4 columns) and returns a dict of the data.
        v = float(v)
        wobs = []
        fobs = []
        ferr = []
        fgen = []
        
        with open(fname, 'r') as f:
            f.readline()
            f.readline()
            f.readline()
            for line in f:
                line = [float(x) for x in line.lower().replace('-', ' -').replace('e -', 'e-').split()]
                wobs.append(line[0])
                fobs.append(line[1])
                ferr.append(line[2])
                fgen.append(line[3])
        
        # Apply velocity shift
        wobs = [i/(1+(v/3e5)) for i in wobs]
        
        #Calculate a chisq on the data
        chisq = 0.0
        sig   = 0.0
        for i,j,k in zip(fobs, fgen, ferr):
            chisq += ((i-j)*(i-j))/(k*k)
            sig   += 1/(k*k)
        chisq /= sig

        if report:
            print '%d lines of data read in from %s' % (len(wobs), fname)
            print 'With accounting for errors:'
            print 'Data has chisq = %f' % chisq
            print 'reduced chisq = %.4g' % (chisq/len(fobs))
            print 'Without accounting for errors:'

        chisq = 0.0
        sig   = 0.0
        for i,k in zip(fobs, fgen):
            chisq += ((i-j)*(i-j))
        chisq /= len(fobs)
        if report:
            print 'chisq = %f' % chisq

        # Return data
        out = {'wobs': wobs,
               'fobs': fobs,
               'fgen': fgen,
               'ferr': ferr
               }
        return out

    def spawn_plot(self):
    # Create an instance of a figure and axes, with no data. Saved in self for access.
        fig, ax = mpl.subplots(figsize=(12,7))

        fig.canvas.set_window_title('SFIT plotting tool - Wild 2017')
        fig.subplots_adjust(left=0.05, bottom=0.13, right=0.98, top = 0.98, hspace=0.0)
        fig.canvas.mpl_connect('key_release_event', self.press)
        fig.canvas.mpl_connect('button_release_event', self.click)

        ax.set_ylim([0.,1.3])

        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.xaxis.set_minor_formatter(FormatStrFormatter('%.1f'))

        ax.set_ylabel('Normalised Flux')
        ax.set_xlabel('Wavelength (A)')

        ax.axhline(y=1.0, alpha=0.3, color='black')
        obs, = ax.step([], [], color='black')
        fit, = ax.plot([], [], color='red')

        self.fig, self.ax, self.obs, self.fit = fig, ax, obs, fit

    def pop_data(self, xx, yy, plot_object):
    # Takes <plot_object> (axes object) and populates it with xx and yy.
        plot_object.set_xdata(xx)
        plot_object.set_ydata(yy)
        return plot_object

    def window(self, minimum_wavelength, window_size):
    # Takes a minimum lambda, which is the left side of the x axis, and a window size,
    # And a plot object. It then takes the wobs, fobs, and fgen and plots them.

        # t0 = time.clock()
        #Get list of x range
        xx = self.input_data['wobs']
        yy1 = self.input_data['fobs']
        yy2 = self.input_data['fgen']
        xxrange = [float(minimum_wavelength), (float(minimum_wavelength)+float(window_size))]
        #Slice out the right data
        new_xx, new_yy1, new_yy2 = [], [], []
        for x,y,z in zip(xx,yy1, yy2):
            if x > 0.9*xxrange[0]:
                if x < 1.1*xxrange[1]:
                    new_xx.append(x)
                    new_yy1.append(y)
                    new_yy2.append(z)
        xx = new_xx
        yy1 = new_yy1
        yy2 = new_yy2

        #Set range, pop data
        self.ax.set_xlim(xxrange)
        self.ax.set_ylim([0., 1.3])
        self.obs = self.pop_data(xx, yy1, self.obs)
        self.fit = self.pop_data(xx, yy2, self.fit)

        # Remove old labels
        self.remove_labels()

        # Label this section
        if self.labels_flag:
            self.label_lines(xxrange)
        # print 'Window took %fs' % (time.clock() - t0)
    
    def run_sfit(self):
    # Open a subprocess, and run SFIT in it. Also checks that there's no SFIT process already running.
        # Make the run command, just in case it's been changed without me noticing
        print 'Current directory:'
        subprocess.Popen('pwd', preexec_fn=os.setsid)
        time.sleep(0.2) # This has to be here, to stop the python script racing off ahead of bash. Hopefully, the user won't be able to notice this.
        self.run = 'Sfit.csh %s %s' % (self.finput, self.flines)

        self.report_files()
        print 'Using the following command:\n %s' % self.run
        time.sleep(1)

        if self.sfit.poll() >0:
            # If this returns a value greater than 0, SFIT is running. Therefore, kill it.
            print "SFIT is already running! Multiple instances messes with the output, please wait a few minutes for it to finish, or kill it with 'k'"
        else:
            # Spawn a subprocess, start the program
            self.sfit = subprocess.Popen(self.run.split(), preexec_fn=os.setsid)
        
    def kill_sfit(self):
    # Kills SFIT, if it's running.
        print 'Attempting to kill SFIT...'
        try:
            os.killpg(os.getpgid(self.sfit.pid), signal.SIGTERM)
            print 'Sent kill signal...'
            time.sleep(0.3)
            if self.sfit.poll() <= 0:
                print 'SFIT killed.'
            else:
                print "Failed to kill SFIT! Here's the poll:"
                print self.sfit.poll()
        except:
            print 'Failed to even attempt to kill sfit! Thats weird, check the code...'


    ### Functions for the notepad ###
    def open_command(self):
    # Open a dialogue box to get a file to push to the textpad
            file = tkFileDialog.askopenfile(parent=self.root, mode='rb', initialfile=self.finput, title='Select a file', filetypes = (("SFIT files","*.sfit"),("all files","*.*")))
            if file != None:
                self.textPad.delete('1.0', END)
                contents = file.read()
                self.textPad.insert('1.0',contents)
                file.close()
                self.open_filename = file.name
                self.root.title(self.open_filename.split('/')[-1])

    def update_notepad(self, fname):
    # When finput is changed, this function should be called to update the textpad contents
        file = open(fname, 'r')
        self.textPad.delete('1.0', END)
        contents = file.read()
        self.textPad.insert('1.0', contents)
        file.close()
        self.open_filename = fname
        self.root.title(self.open_filename.split('/')[-1])

    def saveas_command(self):
    # Save the content to a file, which we get the user to choose from a dialogue box
        file = tkFileDialog.asksaveasfile(mode='w', parent = self.root, initialfile=self.finput, filetypes = (("SFIT files","*.sfit"),("all files","*.*")))
        # print file
        if file != None:
        # slice off the last character from get, as an extra return is added
            data = self.textPad.get('1.0', END+'-1c')
            file.write(data)
            file.close()

    def save_command(self):
    # Save to the filename stored in self.open_filename
        file = open(self.open_filename, 'w')
        if file != None:
        # slice off the last character from get, as an extra return is added
            data = self.textPad.get('1.0', END+'-1c')
            file.write(data)
            file.close()
            
    def exit_command(self):
    # Close the textpad. Also ask if they want to close the whole script.
        askuser = tkMessageBox.askquestion("Quit", "Close everything?")
        if askuser == 'yes':
            mpl.close()
            try:
                os.killpg(os.getpgid(self.sfit.pid), signal.SIGTERM)
                print 'SFIT process killed'
            except:
                if self.sfit.poll() > 0:
                    print 'I failed to kill SFIT. Is it still running?'
        self.root.destroy()

    def new_file(self):
    # Open a new file
        file = tkFileDialog.asksaveasfilename(initialdir='.', parent=self.root, filetypes = (("SFIT files","*.sfit"),("all files","*.*")), title='Create new .sfit file')
        self.open_filename = self.finput

    def enableLabel(self):
        self.labels_flag = not self.labels_flag
        self.refresh_data()
        self.redraw()

    def print_label_cache(self):
    # Print the labels that are stored in self.idlines
        if len(self.idlines) != 0:
            print 'You currently label the following:'
        else:
            print 'No labels in the cache'
        i=0
        for lines in self.idlines:
            els = map(int, lines[2])
            els = [self.elem[i] for i in els]
            print els
            print '%2d - Z: %s / Thresh: %f' % (i, ', '.join(map(str, lines[2])), lines[3])
            i += 1

    def save_and_run_sfit(self):
        self.save_command()
        self.run_sfit()

    def notepad(self, file=None):
    # Add in a lightweight text editor to edit the .sfit file
        self.textPad = ScrolledText(self.root, width=60, height=50)
        self.open_filename = ''

        # Open the input file
        if self.finput != None:
            file = open(self.finput, 'r')
            contents = file.read()
            self.textPad.insert('1.0',contents)
            file.close()
            self.open_filename = self.finput

        self.root.title(self.open_filename.split('/')[-1])

        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open...", command=self.open_command)
        filemenu.add_command(label='Save', command=self.save_command)
        filemenu.add_command(label="Save As", command=self.saveas_command)
        filemenu.add_separator()
        filemenu.add_command(label="Help", command=self.help)

        sfitmenu = Menu(menu)
        menu.add_cascade(label='SFIT', menu=sfitmenu)
        sfitmenu.add_command(label='Print Files', command=self.report_files)
        sfitmenu.add_command(label='Re-enter Files', command=lambda: self.get_files(finput=self.finput, fname=self.fname, flines=self.flines, idfile=self.idfile))
        sfitmenu.add_command(label='Save & Run SFIT', command=self.save_and_run_sfit)
        sfitmenu.add_command(label='Kill SFIT', command=self.kill_sfit)

        idlinesmenu = Menu(menu)
        menu.add_cascade(label='IDlines', menu=idlinesmenu)
        idlinesmenu.add_command(label='Toggle labels', command=self.enableLabel)
        idlinesmenu.add_separator()   
        idlinesmenu.add_command(label='Label new element', command=self.get_labels)
        idlinesmenu.add_command(label='Print label cache', command=self.print_label_cache)
        idlinesmenu.add_command(label='Clear label cache', command=self.clear_label_cache)

        self.textPad.pack(fill=BOTH, side=LEFT)
        self.root.mainloop()

########################### MAIN ############################################

plotter = mplplotter()
