#!/usr/bin/env python
# Takes a load of hot subdwarf models and allows plotting of various parameters against
#  each other. Contains some potentially useful functions, though. 
# Writes plots to a load of files.
# Searches the current directory for models and creates a list. 
# In order to plot the ZAEHB and ZAHeMS, it needs two files containing their data.

def intflx(x, y, xlo, xhi):
#Nothing fancy, just use trapezium style numerical integration
	sum = 0.0
	prevx = x[0]
	prevy = y[0]
	for i,j in zip(x,y):
		if i <= xhi and i >= xlo:
			sum = sum + 0.5 * abs(i-prevx) * (j + prevy)
		prevx = i
		prevy = j
	if sum ==0:
		#print '\n!!! No flux detected in the region',xlo,'-',xhi, '!!!\n'
		sum = 1
	return sum

def flx2mag(flx):
# Convert a flux to magnitude
	ten_pc = 3.086e+17\
	#Convert to absolute magnitudes?
	mag = -2.5*np.log10(flx)
	return mag

def getinfo(filename):
# Takes .s files, and reads in their data
# The file contains a header like this:
# STERNE: Teff=42000. log g=6.0 H=0.85 He=0.15 CN=0.00309                        
# 
#       3668
# Third line is the number of data in the file. I'll read this all in and store it.
# Takes a filename, and returns a list with that stars T, logg, H and He fractions, CN 
#  and FUV, NUV and Visible magnitudes, in that order.
	Teff = 0
	logg = 0.0
	H    = 0.0
	He   = 0.0
	CN   = 0.0
	vega_FUV = -flx2mag(3.8120435e-07)
	vega_NUV = -flx2mag(1.51599900001565e-07)
	vega_V   = -flx2mag(1.45069e-06)
	#Assumed that I have surface fluxes, and the stars all have radii of 0.25R_sun.
	distmod  = 46.24
	
	temp = []
	data = [[],[]]
	back = 0
	with open(file, 'r') as f:
		temp = f.readline().split()
		Teff = int(float(temp[1][5:]))
		logg = float(temp[3][2:])
		H  = float(temp[4][2:])
		He = float(temp[5][3:])
		CN = float(temp[6][3:])
		f.readline()
		f.readline()
		for line in f:
			temp = (line.split())
			data[0].append(float(temp[0]))
			data[1].append(float(temp[1]))
	# Data is a list with the columns <lambda (A)> <Surface Flux>
	
	# Save data as the various regions
	FUV_flx = intflx(data[0], data[1], 1220, 2000)
	FUV_mag = flx2mag(FUV_flx)+vega_FUV+distmod
	
	NUV_flx = intflx(data[0], data[1], 3000, 4000)
	NUV_mag = flx2mag(NUV_flx)+vega_NUV+distmod
	
	vis_flx = intflx(data[0], data[1], 4000, 7500)
	vis_mag = flx2mag(vis_flx)+vega_V+distmod
	
	#print 'Teff =',Teff,'| log(g) =',logg,'| H =', H,'| He =', He,'| CN =', CN
	#print("FUV mag: %-5.2f | NUV mag: %-5.2f | Visible mag: %-5.2f" % (FUV_mag, NUV_mag, vis_mag))
	
	out = [Teff, logg, H, He, CN, FUV_mag, NUV_mag, vis_mag]
	return out

import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import cm

map = 'copper'
labels = ['Teff','log(g)','H frac','He frac','CN frac','','','','Distance from HB','Distance from He MS']
list_of_models = [str(os.path.join(dp, f)) for dp, dn, fn in os.walk(os.path.expanduser(".")) for f in fn if f.endswith('.s')]

if list_of_models == []:
	print 'ERROR: no models found in the current directory.'
	exit()

# Get what the color of the points should be
col = input('What should the colour stand for?\n0: Teff\n1: log(g)\n2: H frac\n3: He frac\n4: CN frac\n5: Distance from HB in T/g line\n6: Distance from the He MS in T/g plane\nEnter value: ')
if col == 5:
	col = 8
if col == 6:
	col = 9

print 'Loading data...'
stars = [[],[],[],[],[],[],[],[]]
temp  = []
count = 0
for file in list_of_models[:]:
	temp = getinfo(file)
	#temp = [Teff, logg, H, He, CN, FUV_mag, NUV_mag, vis_mag]
	#Add in selection criteria here. e.g if you only want stars hotter than 30000K,
	if True:
		for i in range(8):
			stars[i].append(temp[i])
		count += 1

# Reporting! Who doesnt love more info?
print('The %d models used have: \nA temperature range of %d to %d, \nA log(g) range of %2.2f to %2.2f,\nA H range of %2.2f to %2.2f,\nA He range of %2.2f to %2.2f,\nAnd a CN range of %2.2f to %2.2f.' 
				% (count, min(stars[0]), max(stars[0]), min(stars[1]), max(stars[1]), min(stars[2]), max(stars[2]), min(stars[3]), max(stars[3]), min(stars[4]), max(stars[4])))

# 
zaehb = np.genfromtxt('zaehb_Teff_log_g.data', names=True)
zahems = np.genfromtxt('zahems_Teff_log_g.data', names=True)

colour =  [y-x for x,y in zip(stars[5], stars[6])]

#distance from the HB in the T/g plane
dist = []
temp = 0.0
for i in range(len(stars[0])):
	dist.append(0.0)
	mindist = 1000.0
	x = stars[0][i]/10000.
	y = stars[1][i]
	for j,k in zip(zaehb['Teff_kK'], zaehb['log_g']):
		temp = 0.0
		temp = np.sqrt((((j/10)-x)**2)+((k-y)**2))
		if temp < mindist:
			mindist = temp
	dist[i] = mindist
stars.append(dist)

tol = 999
for i in range(len(stars[-1])):
	if stars[-1][i] > tol:
		for j in range(len(stars)):
			stars[j][i] = -99.0
for i in range(len(stars)):
	temp = stars[i]
	stars[i] = [x for x in temp if x!= -99.0]

print('\nPicked out %d models that lie in within a distance of %.2fkK of the HB.' % 
																	(len(stars[0]),tol))

#distance from the MS in the T/g plane
dist = []
temp = 0.0
for i in range(len(stars[0])):
	dist.append(0.0)
	mindist = 1000.0
	x = stars[0][i]/10000.
	y = stars[1][i]
	for j,k in zip(zahems['Teff_kK'], zahems['log_g']):
		temp = 0.0
		temp = np.sqrt((((j/10)-x)**2)+((k-y)**2))
		if temp < mindist:
			mindist = temp
	dist[i] = mindist
stars.append(dist)

tol = 999
for i in range(len(stars[-1])):
	if stars[-1][i] > tol:
		for j in range(len(stars)):
			stars[j][i] = -99.0
for i in range(len(stars)):
	temp = stars[i]
	stars[i] = [x for x in temp if x!= -99.0]

print('\nPicked out %d models that lie in within a distance of %.2fkK of the He MS.' % 
																	(len(stars[0]),tol))

F_N = [y-x for x,y in zip(stars[5], stars[6])]
F_V = [y-x for x,y in zip(stars[5], stars[7])]
N_V = [y-x for x,y in zip(stars[6], stars[7])]

# Plots
for col in range(6):
	if col == 5:
		col = 8
	if col == 6:
		col = 9

	#Plot Teff logg plane
	plt.figure(figsize=(20,10))
		#Data phil gave me
	plt.plot(zaehb['Teff_kK'], zaehb['log_g'], label='Zero age HB')
	plt.plot(zahems['Teff_kK'], zahems['log_g'], label='Zero age MS')

	plt.scatter([x/1000 for x in stars[0]], stars[1], label='Models', c=stars[col], edgecolors='none', cmap=map)
	cbar = plt.colorbar(plt.scatter([x/1000 for x in stars[0]], stars[1], c=stars[col], edgecolors='none', cmap=map))
	cbar.set_label(labels[col], rotation=270, labelpad=20)

	plt.xlim(70.0,0.0)
	plt.ylim(6.5,5.0)
	plt.xlabel('T/1000')
	plt.ylabel('log(g)')
	plt.legend()

	fname = 'figures/T_g_plane_'+str(labels[col])+'.png'
	plt.savefig(fname, bbox_inches='tight')
	#plt.show()

	#Plot F-N vs F
	fig, ax = plt.subplots(figsize=(20,10))
	ax.grid()
	ax.set_title('FUV / FUV-NUV')
	ax.title.set_fontsize(20)

	ax.set_xlabel('FUV-NUV')
	ax.set_ylabel('FUV mag')

	ax.set_xlim(max(F_N)+1, min(F_N)-1)
	ax.set_ylim(max(stars[5])+0.3, min(stars[5])-0.3)

	ax.scatter(F_N, stars[5], c=stars[col], alpha=0.1, edgecolors='none', cmap=map)

	cbar = plt.colorbar(plt.scatter(F_N, stars[5], c=stars[col], edgecolors='none', cmap=map))
	cbar.set_label(labels[col], rotation=270, labelpad=20)

	fname = 'figures/F-N_F_'+str(labels[col])+'.png'
	plt.savefig(fname, bbox_inches='tight')
	#plt.show()

	#Plot F-V vs F
	fig, ax = plt.subplots(figsize=(20,10))
	ax.grid()
	ax.set_title('FUV / FUV-V')
	ax.title.set_fontsize(20)

	ax.set_xlabel('FUV-V')
	ax.set_ylabel('V mag')

	ax.set_xlim(max(F_V)+1, min(F_V)-1)
	ax.set_ylim(max(stars[7])+0.3, min(stars[7])-0.3)

	ax.scatter(F_V, stars[7], c=stars[col], alpha=0.1, edgecolors='none', cmap=map)

	cbar = plt.colorbar(plt.scatter(F_V, stars[7], c=stars[col], edgecolors='none', cmap=map))
	cbar.set_label(labels[col], rotation=270, labelpad=20)

	fname = 'figures/F-V_F_'+str(labels[col])+'.png'
	plt.savefig(fname, bbox_inches='tight')
	#plt.show()


	#Plot N-V vs N
	fig, ax = plt.subplots(figsize=(20,10))
	ax.grid()
	ax.set_title('NUV / NUV-V')
	ax.title.set_fontsize(20)

	ax.set_xlabel('NUV-V')
	ax.set_ylabel('NUV mag')

	ax.set_xlim(max(N_V)+1, min(N_V)-1)
	ax.set_ylim(max(stars[6])+0.3, min(stars[6])-0.3)

	ax.scatter(N_V, stars[6], c=stars[col], alpha=0.1, edgecolors='none', cmap=map)

	cbar = plt.colorbar(plt.scatter(N_V, stars[5], c=stars[col], edgecolors='none', cmap=map))
	cbar.set_label(labels[col], rotation=270, labelpad=20)

	fname = 'figures/N-V_N_'+str(labels[col])+'.png'
	plt.savefig(fname, bbox_inches='tight')
	#plt.show()
	
	
	plt.close("all")