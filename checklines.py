#!/usr/bin/env python
# Report what data is in a linefile, and fix some types of bad data. Breakdown 
#  by element/ion and how many lines dont have damping coefficients.
# Requires the linefile to be in the standard lte format, and can't handle the 
#  values that sometimes aren't space-separated. if it encounters these, it'll 
#  break, so try and fix it in advance.

def line_check(file, pr):
	# if pr == 0, this executes silently. If pr == 1, print the short table. If pr == 2, print the long table. if pr == 3, print both.
	# Data reading setup
	data = []
	temp = []
	flag = 0
	c=0
	# Data info setup
	elem = ['D','H','He','Be','Li','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U']
	Z = [0 for i in elem]
	I = [[0 for i in range(40)] for i in elem]
	bad_damp = [0 for i in elem]
	min = 9.0e99
	max = 0.0
	with open(file,'r') as f:
		# Scan throught the file and read the data into a list
		for line in f:
			# Check that there's no hyphenated numbers, and split the line.
			line = line.replace('-',' -').split()
			# Reset temp
			temp = []
			#Read the data into temp
			for x in line[0:2]:
				temp.append(int(x))
			for x in line[2:-1]:
				temp.append(float(x))
			temp.append(str(line[-1]))
			# Attempt to fix bad data points
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

			# Parse the data
			i = temp
			# Incriment the count for the proton number
			Z[i[0]]+=1
			# Incriment the count for the ion of that proton number
			I[i[0]][i[1]]+=1
			# Check for bad datapoints
			if i[4]==-99.0 or i[5]==-99.0 or i[6]==-99.0:
				bad_damp[i[0]]+=1
			# If lambda is greater than the current max, update max
			if i[2] > max:
				max = i[2]
			# If lambda is less than the current minimum, update min
			if i[2] < min:
				min = i[2]

			data.append(temp)

	if flag == 1:
		print('There were %d bad data points that have been fixed. Writing back to same file...' % c)
		with open(file, 'w') as f:
			for i in range(len(data)):
				temp = data[i]
				f.write('%3d %2d %8.3f %6.3f %8.3f %8.3f %8.3f %8.3f %6.2f %-20s\n' % (temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[7],temp[8],temp[9]))
		print('\nWrote %d lines to the file %s' % (len(data), file))

	if pr == 1 or pr == 3:
		print('\nThe file covers the wavelength range %.2f to %.2f\n' % (min, max))
		print 'Number of lines for each element:'
		print ' Z | ID | N lines  | %% lines Lacking Gammas'
		print '-------------------------------------------'
		for i in range(len(Z)):
			if Z[i] != 0:
				print('%2d | %2s | %-8d | %3d%% ' % (i, elem[i], Z[i], (100*bad_damp[i]/Z[i]) ))
		print('-------------------------')
		try:
			totBadDamp = (100*sum(bad_damp)/sum(Z))
		except ZeroDivisionError:
			totBadDamp = 0.
		print('Total : | %-8d | %3d%% ' % (sum(Z), totBadDamp ))

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
	return()
