#!/usr/bin/env python
# Report what data is in a linefile. I think it should have breakdown by element/ion and 
# how many lines dont have damping coefficients.
# if pr == 0, this executes silently. If pr == 1, print the short table. If pr == 2, print the long table. if pr == 3, print both.
import time as t
file = str(raw_input('Enter linelist filename: '))

data = []
temp = []
flag = 0
c=0
k=0
with open(file,'r') as f:
	for line in f:
		try:
			line = line.split()
			# Z  I  WAVELENGTH  LOG(GF)  GAMMA  GAMMA  GAMMA  LOWER_ENERGY(EV)  0.00  REF #
			# 0  1  2           3        4      5      6      7                 8     9
			temp = []
			# Z and I as integers
			for x in line[0:2]:
				temp.append(int(x))
			# float values
			for x in line[2:8]:
				temp.append(float(x))
			# reference
			temp.append('')
			for i in line[9:]:
				temp[-1] += str(i)
			
			#Correct null values to what SFIT interprets an a null value
			if temp[4] == 0.0:
				temp[4] = -99.0
				flag = 1
				c += 1
			if temp[5] == 0.0:
				temp[5] = -99.0
				flag = 1
				c += 1
			if temp[6] == 0.0:
				temp[6] = -99.0
				flag = 1
				c += 1
			data.append(temp)
		except ValueError:
			k += 1
			print line
			print "There's a formatting error here I can't read! Please fix it"

if k>0:
	print '\nI couldnt read %d lines of the file!' % k

if flag == 1:
	print('There were %d bad data points that have been fixed. Writing to file...' % c)
	outfile = 'fixed_'+file
	with open(outfile, 'w') as f:
		for i in data:
			f.write('%3d %2d %10.3f %6.3f %10.3f %10.3f %10.3f %10.3f 0.00 %-20s\n' % (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]))
	print('\nWrote %d lines to the file %s' % (len(data), outfile))

elem = ['','H','He','Be','Li','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U']

Z = [0 for i in elem]
I = [[0 for i in range(40)] for i in elem]
bad_damp = [0 for i in elem]
min = 9.0e99
max = 0.0
refs = {}
for i in data:
	Z[i[0]]+=1
	I[i[0]][i[1]]+=1
	if i[4]==-99.0 or i[5]==-99.0 or i[6]==-99.0:
		bad_damp[i[0]]+=1
	if i[2] > max:
		max = i[2]
	if i[2] < min:
		min = i[2]
	if i[8] not in refs.keys():
		refs[i[8]] = 1
	elif i[8] in refs.keys():
		refs[i[8]] += 1

print '\n'
print ' Source                         | N lines  '
print '-------------------------------------------'
for i in refs:
	print ' %-30s | %-9d' % (str(i), refs[i])
print '-------------------------------------------'

pr = int(input('0: no print\n1: By element\n2: By ion\n3: Both\nEnter choice: '))

if pr == 1 or pr == 3:
	print('\nThe file covers the wavelength range %.2f to %.2f\n' % (min, max))
	print 'Number of lines for each element:'
	print ' Z | ID | N lines  | % lines Lacking Gammas'
	print '-------------------------------------------'
	for i in range(len(Z)):
		if Z[i] != 0:
			try:
				totBadDamp = (100.0*bad_damp[i]/Z[i])
			except ZeroDivisionError:
				totBadDamp = 0.
			print('%2d | %2s | %-8d | %6.2f%% ' % (i, elem[i], Z[i], totBadDamp ))
	print('-------------------------')
	print('Total : | %-8d | %3.2f%% ' % (sum(Z), (100*sum(bad_damp)/sum(Z)) ))
if pr == 2 or pr == 3:
	if pr != 2:
		raw_input('Hit enter for a breakdown by ion: ')
	fl = 1
	print 'Breakdown by ion:'
	print ' Z |  ID   | N lines'
	print '--------------------'
	for i in range(len(Z)):
		fl = 1
		for j in range(40):
			if I[i][j] != 0:
				if fl == 1:
					print('%2d | %2s %-2d | %-8d ' % (i, elem[i], j, I[i][j]))
					fl = 0
				else:
					print('   |    %-2s | %-8d ' % (j, I[i][j]))
if pr == 0:
	print '%s was successfully checked' % file
