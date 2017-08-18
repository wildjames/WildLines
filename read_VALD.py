#!/usr/bin/env python
# Reads data from the Vienna Atomic Line Databas (VALD) http://vald.astro.uu.se/
#
#### Make sure that you use the following parameters!
# begin request
# extract all
# default configuration
# via ftp
# short format
# waveunit angstrom
# energyunit eV
# medium vacuum
# isotopic scaling off
# default waals
# have rad
# have stark
# have waals
# 
# 
# wmin, wmax
# end request

file = raw_input('Please enter the filename: ')

# Reading in file variables
# Element list
elem = ['D' ,'H',                                                                            'He',
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
data = []
line = ''
i=0
flag = True
# Writing out file variables
outfile = (file+'.lte')
fout = open(outfile, 'w')
line = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '']

with open(file, 'r') as f:
    # Check that the top line is of the correct format. This may need to be tweaked with updates to VALD.
    for line in f:
        line = line.split()
        # Scan the file until we find the header
        if line[:2] == ['Elm','Ion'] and line[3:] == ['Excit(eV)','log','gf*','Rad.','Stark','Waals','factor','References'] and line[2][:2] == 'WL':
            flag = False
            break
    if flag:
        print "Couldn't read the file!"
        print "I accept VALD data pulled from the online form (http://vald.astro.uu.se/), with the following parameters..."
        print ''
        print '-extract all'
        print '-default configuration'
        print '-short format'
        print '-waveunit angstrom'
        print '-energyunit eV'
        print '-isotopic scaling off'
        print '-default waals'
        print '-have rad'
        print '-have stark'
        print '-have waals'
        print 'I check for this by searching for the following string:'
        print 'Elm Ion       WL(A) Excit(eV) log gf*   Rad.  Stark    Waals factor   References'
        exit()

    for line in f:
        try:
        	# Read in data
            elem.index(line.split(',')[0][1:3])
            n = line.split(',')[0:-1]
            i += 1
            
            # Parse data into .lte format
            line = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '']
            
            name = n[0].replace("'",'')
            name = [name[:2],name[2:]]
            
            line[0] = elem.index(name[0]) #Z
            line[1] = int(name[1]) #Ionisation state
            line[2] = float(n[1]) # lambda
            line[3] = float(n[3]) # log(gf)
            line[4] = float(n[5]) # elec
            line[5] = float(n[4]) # rad
            line[6] = float(n[6]) # vdw
            line[7] = float(n[2]) # excitation pot
            line[8] = 0.00
            line[9] = 'VALD'      #ref

            # Write to file
            fout.write('%3d %2d %8.3f %6.3f %8.3f %8.3f %8.3f %8.3f %6.2f %-20s\n' % (line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9]))

        # Catch a ValueError, signifying that we've reached a line of text and have finished reading the file.
        except ValueError:
        	print('Reached End of file after %d lines.' % i)
        	break

fout.close()

detail = int(raw_input('0: no print\n1: By element\n2: By ion\n3: Both\nEnter choice: '))
import checklines as ch
ch.line_check(outfile, detail)

print('Wrote %d lines to the file %s.' % (i, outfile))