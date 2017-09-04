#!/usr/bin/env python
### James Wild, 2017 ###
# This is a spectral line plotting tool, designed to be used with columnated
#  spectra files and plot sections of them for publication. 
# It takes an input file with parameters, and constructs a pass to a function
#  in the module file, LinesPlotLib.py (which should be in the same directory
#  as this file) for plotting.
# An example file is available in the downloaded zip from Git, and contains
#  all the arguments that can be passed, and default values. Alternatively, 
#  an MWE would be:
#spec <file>
#lines
#<lambda>
#
#run
#  This would show on screen, the 20A on either side of <lambda> from <file>.

import LinesPlotLib as lpl
class lplinterp():

    def __init__(self, finput=None):
        # Initialise all the variables
            ### USAGE:
            ##  <lines>      - List of lines to plot
            ##  <fname>      - Spectrum filename.
            ## OPTIONAL ARGUMENTS ##
            ##  [wr]         - (number) How far to extend the data, about the desired lines
            ##  [title]      - Title above the figure
            ##  [oname]      - File name to write to. If multiple images are created, they will be numbered. Appended with .pdf by the program
            ##  [N]          - Number of lines to include on a single figure
            ##  [labes]      - (Ordered!) list of custom labels to supply to the image
            ##  [offset]     - Offset incriment
            ##  [text_shift] - fractional shift inwards from the negative x axis limit
            ##  [out]        - y/n do we print to file? Default no.
            # Retrieve observations and model
        self.echo       = False
        self.lines      = []
        self.fname      = []
        self.cols       = []
        self.wr         = 20
        self.title      = None
        self.oname      = 'Lines'
        self.N          = 6
        self.v          = 0.0
        self.labels     = []
        self.offset     = 1.1
        self.text_shift = 0.5
        self.out        = 'n'
        self.lpad       = 0.15
        self.dpad       = 0.10
        self.rpad       = 0.95
        self.upad       = 0.95
        self.figsize    = [3.15, 4.0]
                        # width, height

        # Get the command file, and read in each command. Pass it to the interpreter.
        if finput == None:
            finput = raw_input('Please enter a control filename: ')

        if finput == '':
            print 'No input file, printing Help:'


        self.commandfile =  open(finput, 'r')
        
        # Get the number of lines in the command file
        num_lines = sum(1 for line in open(finput))

        self.i = 0
        while self.i < num_lines:
            # read line, clean newline character, parse escape character
            line = self.commandfile.readline().strip().split('!')[0]
            self.i += 1
            if line != '':
                self.interp_line(line)
        
        self.commandfile.close()

    def interp_line(self, line):
        line = line.split()
        command = line[0].lower()
        instruction = line[1:]
        try:
            if self.echo == True:
                print 'Command: <%s>' % (command)

            if command == 'echo':
                self.echo = (instruction[0].lower() == 'on' or instruction[0].lower() == 'true' or instruction[0] == '1')

            elif command == 'lines':
                self.read_lines()
                if self.echo:
                    print 'Plotting the following lines:'
                    for i in self.lines:
                        print i

            elif command == 'cols' or command == 'col':
                self.cols = [int(x) for x in instruction]
                if self.echo:
                    print 'Reading data from columns %s.' % (self.cols)

            elif command == 'labels':
                self.read_labels()
                if self.echo:
                    print "Using the following labels:"
                    for i in self.labels:
                        print "<%s>" % i

            elif command == 'lspace':
                self.lpad = float(instruction[0])
                if self.echo:
                    print "Using a left padding space of %d%%" % int(100*self.lpad) 

            elif command == 'dspace':
                self.dpad = float(instruction[0])
                if self.echo:
                    print "Using a bottom padding space of %d%%" % int(100*self.dpad) 

            elif command == 'uspace':
                self.upad = float(instruction[0])
                if self.echo:
                    print "Using an upper padding space of %d%%" % int(100*self.upad) 

            elif command == 'rspace':
                self.rpad = float(instruction[0])
                if self.echo:
                    print "Using a right padding space of %d%%" % int(100*self.rpad) 

            elif command == 'offset':
                self.offset = float(instruction[0])
                if self.echo:
                    print "Offsetting each subsequent line by %.2f" % self.offset

            elif command == 'text_shift':
                self.text_shift = float(instruction[0])
                if self.echo:
                    print "Text location (fractional distance from the left) -- %.2f" % self.text_shift

            elif command == 'out':
                if instruction[0][0] == 'y' or instruction[0][0] == 'n':
                    self.out = instruction[0][0]
                else:
                    print 'Invalid <out> argument! [y/n]'
                if self.echo:
                    print "Print to file? %1s" % self.out

            elif command == 'spec':
                self.fname.append(instruction[0])
                if self.echo:
                    print "Reading data from the following files:"
                    for i in self.fname:
                        print "<%s>" % i

            elif command == 'figsize':
                self.figsize = [float(instruction[0]), float(instruction[1])]
                if self.echo:
                    print "Figure will be %.2f inches wide and %.2f inches tall." % (self.figsize[0], self.figsize[1])

            elif command == 'wr':
                self.wr = float(instruction[0])
                if self.echo:
                    print "Snipping data from %.2fA about the lines"

            elif command == 'title':
                self.title = ' '.join(instruction)
                if self.echo:
                    print "Figure Title: <%s>" % self.title

            elif command == 'oname':
                self.oname = '_'.join(instruction)
                if self.echo:
                    print "Writing to %s.pdf" % self.oname

            elif command == 'n':
                self.N = int(instruction[0])
                if self.echo:
                    print "Plotting %d lines per figure" % self.N

            elif command == 'v':
                self.v = float(instruction[0])
                if self.echo:
                    print 'Velocity correction: %.2f' % self.v

            elif command == 'run':
                self.run()

            elif command == 'end':
                exit()

            else:
                print 'ERROR: Command <%s %s> is not valid.' % (command, ''.join(line))

        except IndexError:
            print 'ERROR: No argument passed to %s, but one is required!' % command

        if self.echo:
            print '\n'

    def read_lines(self):
        # Read in numbers from the file until we find an empty line.
        # Clear the current lines and labels lists.
        self.lines = []
        
        # Read in first line
        oline = self.commandfile.readline().strip()
        line  = oline.split('!')[0]
        self.i += 1 
        
        # While the line is NOT blank (blank line is a terminator) OR the line has comments in it,
        #  keep reading in data.
        while line != '' or len(oline.split('!')) != 1:
            try:
                if line != '':
                    self.lines.append(float(line))
                oline = self.commandfile.readline().strip()
                line = oline.split('!')[0]
                self.i += 1
            except ValueError:
                print 'There was an error reading in your line wavelengths!'
                print 'Error was on line %d\n%s' % (self.i, line)
                break

    def read_labels(self):
        # Read in the labels from the file until we find an empty line
        oline = self.commandfile.readline().strip()
        line  = oline.split('!')[0]
        self.i += 1
        self.labels = []

        # While the line is NOT blank (blank line is a terminator) OR the line has comments in it,
        #  keep reading in data.
        while line != '' or len(oline.split('!')) != 1:
            # Use keyword 'None' to specify a blank label
            if line.lower() == 'none':
                line = None
            # If the line is blank, it's because of a commented out line.
            if line != '':
                self.labels.append(line)
            # Read in next line. Incriment line counter.
            oline = self.commandfile.readline().strip()
            line = oline.split('!')[0]
            self.i += 1

    def check_lines_labels(self):
        # If lines and labels aren't the same shape, alter the labels list to be so.

        if self.labels == []:
            self.labels = None
            return

        labels = ['' for x in self.lines] # List of the shape lines

        i = len(self.labels)
        labels[:i] = self.labels
        self.labels = labels
        for j in range(i):
            if self.labels[j] == None or self.labels[j].lower() == 'none':
                print self.labels[j].lower()
                self.labels[j] = ''

        if self.echo:
            print 'Lines and labels:'
            for i, j in zip(self.lines, self.labels):
                print 'Line: %.2f --- Label: %s' % (i, j)
            print '\n'


    def run(self):
        # Run the plotting function
        
        # If we only have one fname, we can use a different reading function. 
        ## I don't know why I did this since it's not any faster, but it's not any slower either so whatever.
        if len(self.fname) == 1:
            self.fname = str(self.fname[0])
        # Check that an fname has been given at all:
        if self.fname[0] == '':
            print 'Please supply a spectrum file!!'
            exit()

        # Check the line/label lists
        self.check_lines_labels()

        if self.echo:
            print('lines=%s,\nfname=%s,\nwr=%s,\ntitle=%s,\noname=%s,\nN=%s,\nlabels=%s,\noffest=%s,\ntext_shift=%s,\nout=%s,\nlspace=%s,\ndspace=%s,\nrspace=%s,\nuspace=%s,\nv=%s' % 
                                    (self.lines, self.fname, self.wr, self.title, self.oname, self.N, 
                                        self.labels, self.offset, self.text_shift, self.out, self.lpad, 
                                        self.dpad, self.rpad, self.upad, self.v))

        # Pass all the arguments we've collected over to the module
        lpl.generate_plots(self.lines, self.fname, wr=self.wr, title=self.title, oname=self.oname, 
                            N=self.N, labels=self.labels, offset=self.offset, text_shift=self.text_shift, 
                            out=self.out, figsize=self.figsize, lpad=self.lpad, dpad=self.dpad, 
                            rpad=self.rpad, upad=self.upad, v=self.v, cols=self.cols)

active = lplinterp('input.pwl')