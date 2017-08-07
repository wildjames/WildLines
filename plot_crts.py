#!/usr/bin/env python
# James Wild, 2017
# Takes a 

filename = raw_input('Enter the filename: ')


def plot_hist(data,bins, label):
	ax=plt.axes()
	plt.hist(data, bins)
	ax.yaxis.grid(True)
	plt.xlabel(label)
	plt.ylabel('Count')
	plt.show()
	return

def plot_scatter(x, y, err, title, x_lab, y_lab):
	ax=plt.axes()
	ax.yaxis.grid(True)
	plt.xlabel(x_lab)
	plt.ylabel(y_lab)
	plt.plot(x, y, 'o')
	plt.errorbar(x,y,yerr=err, linestyle='None')
	plt.title(title)
	plt.show()
	return

import matplotlib.pyplot as plt
import numpy as np

mag    = []
magerr = []
RA     = []
DEC    = []
MJD    = []
temp   = []
with open(filename,'r') as f:
	f.readline()
	for line in f:
		temp = [float(x) for x in line.split(',')]
		mag.append(temp[1])
		magerr.append(temp[2])
		RA.append(temp[3])
		DEC.append(temp[4])
		MJD.append(temp[5])

avmag = np.mean(mag)

l=0    #Number of points > 3 sigma from mean
n=0    #Number of points > 4 sigma from mean
sigs = [] #how many sigmas the point it from the mean
SDs  = []
SD   = 0

for m in mag:
	SD += abs(m-avmag)**2
SD = np.sqrt(SD/len(mag))


for m,e in zip(mag,magerr):
	if abs(m-SD) > 3*e:
		l += 1
	if abs(m-SD) > 3*e:
		n += 1
	SDs.append((m-avmag)/SD)
	sigs.append((m-avmag)/e)

print 'The mean magnitude is %5.2f.' % avmag
print 'The standard deviation is %f' % SD
print "There were %d points more than 3 standard deviations from the mean\n%d points more than 4 SD's from the mean.\nThis was from a total of %d points." % (l, m, len(mag))


plot_hist(sigs, 50, 'Number of sigmas from the mean')
plot_hist(SDs, 50, 'Number of standard deviations from the mean')
plot_scatter(MJD, mag, magerr, 'MJD', 'Magnitude', 'CRTS Lightcurve of PG 0909+276')

