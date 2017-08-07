#!/usr/bin/env python
# Reads in the Kurucz database, and converts it to a .lte file with given constraints.

import numpy as np

file = 'gfallvac21oct16.dat.txt'

s = 'Enter min wavelength (range from 19A to 9960160A): '
min = float(input(s))
max = float(input('Enter max wavelength: '))
air = raw_input('Air or vacuum? (a/v): ')
air = air.lower()

# Element cutoff.
# zmax = 31
zmax = 99

data = []
with open(file, 'r') as f:
	for line in f:
		data.append(line)

elem = ['','H','He','Be','Li','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U']

Z = 0
io = 0
wl = 0.0
gf = 0.0
damp = [0.0,0.0,0.0] #elec/rad/vdw
ex = 0.0
out = []

temp = [[],[]]
for i in data:
	temp = i[18:24].split('.')
	w = float(i[0:11])*10
	# Do not include H/He data since it causes conflicts.
	if w < max and w > min:
		if int(temp[0])!=1:
			if int(temp[0])!=2:
				if int(temp[0])<zmax:
					wl = (float(i[0:11])*10)
					gf = (float(i[11:18]))
					damp[0] = (float(i[86:92]))
					damp[1] = (float(i[80:86]))
					damp[2] = (float(i[92:98]))
					ex = (float(i[52:64])/8065.544)
					Z = (int(temp[0]))
					io = (int(temp[1])+1)
					# If we want an in-air observation, convert wavelength.
					if air == 'a':
						wl = wl/1.000277
					# Stick it in out.
					out.append([Z,io,wl,gf,damp[0],damp[1],damp[2],ex,0.0,'Kurucz_2016'])


outfile = 'gf'+str(int(min/100))+str(int(max/100))+air+'_LiZn_K16.lte'
with open(outfile, 'w') as f:
    for i in range(len(out)):
		temp = out[i]
		f.write('%3d %2d %8.3f %6.3f %8.3f %8.3f %8.3f %8.3f %6.2f %-20s\n' % (temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[7],temp[8],temp[9]))
print('\nWrote %d lines to the file %s.\n' % (len(out), outfile))

detail = int(raw_input('0: no print\n1: By element\n2: By ion\n3: Both\nEnter choice: '))
import checklines as ch
ch.line_check(outfile, detail)