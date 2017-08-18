#!/usr/bin/env python
# Reads in Kentucky data
# http://www.pa.uky.edu/~peter/newpage/

import numpy as np

def roman_to_int(input):
   if type(input) != type(""):
      raise TypeError, "expected string, got %s" % type(input)
   input = input.upper()
   nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
   ints = [1000, 500, 100, 50,  10,  5,   1]
   places = []
   for c in input:
      if not c in nums:
         raise ValueError, "input is not a valid roman numeral: %s" % input
   for i in range(len(input)):
      c = input[i]
      value = ints[nums.index(c)]
      # If the next place holds a larger number, this value is negative.
      try:
         nextvalue = ints[nums.index(input[i +1])]
         if nextvalue > value:
            value *= -1
      except IndexError:
         # there is no next place.
         pass
      places.append(value)
   sum = 0
   for n in places: sum += n
   return sum

def ann_format():
	print "Ensure that you click the 'exclude lines without atomic data' box (or the form will fetch a load of lines with poor wavelengths and no gf values) and that you've selected eV as the energy units."
	print "\nOutput Format:\n[ ] Wavelength Accuracy\n[X] Spectrum\n[ ] Transition Type\n[ ] Configuration\n[ ] Term\n[ ] Angular Momentum ( ) as J ( ) as g ( ) combine with term\n[X] Transition Probability [ ] as Aki [ ] As gAki [ ] As f_ik [ ] as S [X] as log(gf)\n[X] Level Energies\nOutput Mode: (o) plain"
	print ""
	print "The top line of the data should be:"
	print "-LAB-WAVL-ANG-VAC-|-SPECTRUM-|TT|-lg(gf)-|-TPF-|-----LEVEL-ENERGY--EV------|-REF---|"

#Ensure that you click the 'exclude lines without atomic data' box (or the form will 
#  fetch a load of lines with poor wavelengths and no gf values) and that you've 
#  selected eV as the energy units.
#Output Format:
# [ ] Wavelength Accuracy
# [X] Spectrum
# [ ] Transition Type
# [ ] Configuration
# [ ] Term
# [ ] Angular Momentum ( ) as J ( ) as g ( ) combine with term
# [X] Transition Probability [ ] as Aki [ ] As gAki [ ] As f_ik [ ] as S [X] as log(gf)
# [X] Level Energies
# Output Mode: (o) plain
# 
# The top line of the data should be:
# -LAB-WAVL-ANG-VAC-|-SPECTRUM-|TT|-lg(gf)-|-TPF-|-----LEVEL-ENERGY--EV------|-REF---|

while True:
	try:
		file = raw_input('Enter filename: ')
		open(file,'r')
		break
	except IOError:
		print 'File not found, please try again.'

data = []
a=''
with open(file,'r') as f:
	a = f.readline()
	if a != "-LAB-WAVL-ANG-VAC-|-SPECTRUM-|-lg(gf)-|-TPF-|-----LEVEL-ENERGY--EV------|-REF---|\n":
		print "Sorry, you've given me the wrong output format!\n"
		ann_format()
		print 'your top line is:'
		print a
		exit()
	l = 0
	for line in f:
		data.append(line.split())
		l += 1

wl = []#lambda
z  = []#Element
io = []#ionisation level
lg = []#log(gf)
ex = []#excitation potential

#for ID-ing elements
elem = ['','H','He','Be','Li','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U']
u=0
for line in data:
	try:
		wl.append(float(line[0]))
	except ValueError:
		wl.append(float(line[0][:-1]))
		#print 'Uncertain wavelength:', line[0]
		u += 1
	lg.append(float(line[3]))
	if line[5].endswith('?'):
		line[5] = line[5][:-1]
	if line[5].endswith('+x') or line[5].endswith('+y'):
		line[5] = line[5][:-2]
	ex.append(float(line[5]))
	if line[1].startswith('['):
		line[1] = line[1][1:]
	z.append(elem.index(line[1]))
	
	if line[2].endswith(']'):
		line[2] = line[2][:-1]
	if line[2][0] == '[':
		line[2] = line[2][1:]
	io.append(roman_to_int(line[2]))


outfile = file+'.lte'

with open(outfile, 'w') as f:
	for i in range(l):
		f.write('%3d %2d %8.3f %6.3f %8.3f %8.3f %8.3f %8.3f %6.2f %-20s\n' % 
				(z[i], io[i], wl[i], lg[i], -99.0, -99.0, -99.0, ex[i], 0.0, 'Kentucky_Line_List' ))
print('Wrote %d lines to %s' % (l, outfile))

detail = int(raw_input('0: no print\n1: By element\n2: By ion\n3: Both\nEnter choice: '))
import checklines as ch
ch.line_check(outfile, detail)