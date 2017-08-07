#!/usr/bin/env python
# Reads data from the Vienna Atomic Line Databas (VALD) 
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

elem = ['','H ','He','Be','Li','B ','C ','N ','O ','F ','Ne','Na','Mg','Al','Si','P ','S ','Cl','Ar','K ','Ca','Sc','Ti','V ','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y ','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I ','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W ','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U ']

data = []
line = ''
i=0
with open(file, 'r') as f:
    f.readline()
    if f.readline() != 'Elm Ion       WL_vac(A) Excit(eV) log gf*   Rad.  Stark    Waals factor  References\n':
    	print 'Incorrect format.'
    	sys.exit()
    for line in f:
        try:
        	elem.index(line.split(',')[0][1:3])
        	i += 1
        except ValueError:
        	print('Reached End of file after %d lines.' % i)
        	break
        data.append(line.split(',')[0:-1])


out = []
line = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '']

for n in data:
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
    
    out.append(line)
outfile = (file+'.lte')
with open(outfile, 'w') as f:
    for i in range(len(out)):
		temp = out[i]
		f.write('%3d %2d %8.3f %6.3f %8.3f %8.3f %8.3f %8.3f %6.2f %-20s\n' % (temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[7],temp[8],temp[9]))
print('Wrote %d lines to the file %s.' % (len(out), outfile))

detail = int(raw_input('0: no print\n1: By element\n2: By ion\n3: Both\nEnter choice: '))
import checklines as ch
ch.line_check(outfile, detail)