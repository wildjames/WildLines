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
        self.lines      = []
        self.fname      = []
        self.wr         = 20
        self.title      = None
        self.oname      = 'SpectralLines'
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

        print 'Command: <%s>\nInstruction: <%s>\n' % (command, instruction)

        if command == 'lines':
            self.read_lines()

        elif command == 'labels':
            self.read_labels()

        elif command == 'whitespace':
            self.pad = float(instruction[0])

        elif command == 'offset':
            self.offset = float(instruction[0])

        elif command == 'text_shift':
            self.text_shift = float(instruction[0])

        elif command == 'out':
            if instruction[0][0] == 'y' or instruction[0][0] == 'n':
                self.out = instruction[0][0]
            else:
                print 'Invalid <out> argument! [y/n]'

        elif command == 'spec':
            self.fname.append(instruction[0])

        elif command == 'figsize':
            self.figsize = [float(instruction[0]), float(instruction[1])]

        elif command == 'wr':
            self.wr = float(instruction[0])

        elif command == 'title':
            self.title = ' '.join(instruction)

        elif command == 'oname':
            self.oname = '_'.join(instruction)

        elif command == 'n':
            self.N = int(instruction[0])

        elif command == 'v':
            self.v = float(instruction[0])

        elif command == 'run':
            self.run()

        elif command == 'end':
            exit()

        else:
            print 'ERROR: Command <%s %s> is not valid.' % (command, ''.join(line))

    def read_lines(self):
        # Read in numbers from the file until we find an empty line
        line = self.commandfile.readline().strip()
        self.i += 1 
        while line != '':
            try:
                self.lines.append(float(line))
                line = self.commandfile.readline().strip()
                self.i += 1
            except ValueError:
                print 'There was an error reading in your line wavelengths!'
                print 'Error was on line %d\n' % self.i
                break
        self.labels = [None for x in self.lines]

    def read_labels(self):
        # Read in the labels from the file until we find an empty line
        line = self.commandfile.readline().strip()
        self.i += 1
        labels = []
        while line != '':
            try:
                labels.append(line)
                line = self.commandfile.readline().strip()
                self.i += 1
            except ValueError:
                break

        for j in range(len(self.lines)):
            self.labels[j] = labels[j]

    def run(self):
        # Run the plotting function
        # Generate the plots.
        # generate_plots(Hlines, fname, oname=oname+'_Balmer-', N=5, labels=Hlabels, out=out)
        # print 'Done balmer...'
        if len(self.fname) == 1:
            fname = str(fname[0])

        # print('lpl.generate_plots(lines=%s, fname=%s, wr=%s, title=%s, oname=%s, N=%s, labels=%s, offest=%s, text_shift=%s, out=%s, pad=%s, v=%s)' % 
        #                         (self.lines, self.fname, self.wr, self.title, self.oname, self.N, 
        #                             self.labels, self.offset, self.text_shift, self.out, self.pad, self.v))

        # Pass all the arguments we've collected over to the module
        lpl.generate_plots(self.lines, self.fname, wr=self.wr, title=self.title, oname=self.oname, 
                            N=self.N, labels=self.labels, offset=self.offset, text_shift=self.text_shift, 
                            out=self.out, figsize=self.figsize, pad=self.pad, v=self.v)

active = lplinterp('input.pwl')