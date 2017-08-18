#!/usr/bin/env python

def roman_to_int(input):
# Takes a string numeral and converts it to integer
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

elem = ['','H','He','Be','Li','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U']

file = raw_input('Enter Filename (default to raw_tubingen): ')
if file == '':
	file = 'raw_tubingen'

data = []
#  Lambda [A] | Z | I | log(gf) | gA [1e9 s&-1] | E_init [cm^-1] | - | J_i | E_final [cm^-1] | - | J_f | Ref
with open(file, 'r') as f:
   if f.readline() != 'c_wavelength,chemical_element,ion_stage,log_gf,ga,initial_level_energy,par_init,j_init,final_level_energy,par_final,j_final,pub':
   	for line in f:
         data.append(line.split(','))

lam = []
Z =   []
I =   []
gf =  []
ex =  []
for i in range(len(data)):
	Z.append(elem.index(data[i][1]))
	lam.append(float(data[i][0]))
	gf.append(float(data[i][3]))
	ex.append(float(data[i][5]))
	I.append(roman_to_int(data[i][2]))

ex = [x*1.239842e-4 for x in ex]

count = [0 for x in elem]
for i in Z:
	count[i] += 1

outfile = file+'.lte'
with open(outfile, 'w') as f:
	for i in range(len(lam)):
		f.write('%3d %2d %8.3f %6.3f %8.3f %8.3f %8.3f %8.3f %6.2f %-20s\n' % 
				(Z[i], I[i], lam[i], gf[i], -99.0, -99.0, -99.0, ex[i], 0.0, 'Tubingen_database' ))
print 'Wrote to',outfile

detail = int(raw_input('0: no print\n1: By element\n2: By ion\n3: Both\nEnter choice: '))
import checklines as ch
ch.line_check(outfile, detail)