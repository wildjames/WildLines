#!/usr/bin/env python
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
        self.col1       = 0
        self.col2       = 1
        self.col3       = None
        self.col4       = None
        self.wr         = 20
        self.title      = None
        self.oname      = 'Lines'
        self.N          = 6
        self.v          = 0.0
        self.labels     = []
        self.offset     = 1.1
        self.text_shift = 0.5
        self.out        = 'y'
        self.pad        = 0.15
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

        if self.echo == True:
            print 'Command: <%s>' % (command)

        if command == 'echo':
            self.echo = (instruction[0].lower() == 'on' or instruction[0].lower() == 'true' or int(instruction[0]) == 1)

        elif command == 'lines':
            self.read_lines()
            if self.echo:
                print 'Plotting the following lines:'
                for i in self.lines:
                    print i

        elif command == 'cols':
            # Ugly code. Think of a better way of doing this... Might take some work though.

            self.col1, self.col2, self.col3, self.col4 = [None, None, None, None]

            if len(instruction) == 2:
                self.col1, self.col2 = [int(x) for x in instruction]
                if self.echo:
                    print 'Reading data from columns %d and %d' % (self.col1, self.col2)

            elif len(instruction) == 3:
                self.col1, self.col2, self.col3 = [int(x) for x in instruction]
                if self.echo:
                    print 'Reading data from columns %d, %d, %d.' % (self.col1, self.col2, self.col3)
            
            elif len(instruction) == 4:
                self.col1, self.col2, self.col3, self.col4 = [int(x) for x in instruction]
                if self.echo:
                    print 'Reading data from columns %d, %d, %d, %d.' % (self.col1, self.col2, self.col3, self.col4)

        elif command == 'labels':
            self.read_labels()
            if self.echo:
                print "Using the following labels:"
                for i in self.labels:
                    print "<%s>" % i

        elif command == 'whitespace':
            self.pad = float(instruction[0])
            if self.echo:
                print "Using a left padding space of %.2f%%" % self.pad 

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

        if self.echo:
            print '\n'

    def read_lines(self):
        # Read in numbers from the file until we find an empty line.
        # Clear the current lines and labels lists.
        self.lines = []
        line = self.commandfile.readline().strip()
        self.i += 1 
        while line != '':
            try:
                self.lines.append(float(line))
                line = self.commandfile.readline().strip()
                self.i += 1
            except ValueError:
                print 'There was an error reading in your line wavelengths!'
                print 'Error was on line %d\n%s' % (self.i, line)
                break

    def read_labels(self):
        # Read in the labels from the file until we find an empty line
        line = self.commandfile.readline().strip()
        self.i += 1
        labels = []

        while line != '':
            labels.append(line)
            line = self.commandfile.readline().strip()
            self.i += 1

        self.labels = labels

    def check_lines_labels(self):
        # If lines and labels aren't the same shape, alter the labels list to be so.

        labels = [None for x in self.lines] # List of the shape lines

        i = len(self.lines)
        for j in range(i):
            labels[j] = self.labels[j]


    def run(self):
        # Run the plotting function
        
        # If we only have one fname, we can use a different reading function. 
        ## I don't know why I did this since it's not any faster, but it's not any slower either so whatever.
        if len(self.fname) == 1:
            fname = str(fname[0])
        # Check that an fname has been given at all:
        if self.fname[0] == '':
            print 'Please supply a spectrum file!!'
            exit()

        # Check the line/label lists
        self.check_lines_labels()

        if self.echo:
            print('lpl.generate_plots(lines=%s, fname=%s, wr=%s, title=%s, oname=%s, N=%s, labels=%s, offest=%s, text_shift=%s, out=%s, pad=%s, v=%s)' % 
                                    (self.lines, self.fname, self.wr, self.title, self.oname, self.N, 
                                        self.labels, self.offset, self.text_shift, self.out, self.pad, self.v))

        # Pass all the arguments we've collected over to the module
        lpl.generate_plots(self.lines, self.fname, wr=self.wr, title=self.title, oname=self.oname, 
                            N=self.N, labels=self.labels, offset=self.offset, text_shift=self.text_shift, 
                            out=self.out, figsize=self.figsize, pad=self.pad, v=self.v, col1=self.col1, 
                            col2=self.col2, col3=self.col3, col4=self.col4)

active = lplinterp()