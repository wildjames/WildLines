#!/usr/bin/env python
# James Wild, 2017
# Plots a WASP lightcurve, and does extremely rudimentary analysis for variations.

fname = '1SWASP_J091251.66+272031.3.csv'
fname = raw_input('Please enter a WASP .csv file: ')



import numpy as np
import matplotlib.pyplot as plt

def plot_hist(data,bins, label):
	ax=plt.axes()
	plt.hist(data, bins)
	ax.yaxis.grid(True)
	plt.xlabel(label)
	plt.ylabel('Count')
	plt.show()
	return

t = []
mag = []
err = []

with open(fname, 'r') as f:
	f.readline()
	for line in f:
		temp = line.split(',')
		t.append(float(temp[0]))
		mag.append(float(temp[2]))
		err.append(float(temp[3]))

avmag = np.mean(mag)

l=0    #Number of points > 3 sigma from mean
n=0    #Number of points > 4 sigma from mean
sigs = [] #how many sigmas the point it from the mean
SDs  = []
SD   = 0

for m in mag:
	SD += abs(m-avmag)**2
SD = np.sqrt(SD/len(mag))

# Check to see how far from the mean the data are
for m,e in zip(mag,err):
	if abs(m-e-avmag) > 3*SD:
		l += 1
	if abs(m-e-avmag) > 4*SD:
		n += 1
	SDs.append((m-avmag)/SD)
	sigs.append((m-avmag)/e)

print 'The mean magnitude is %5.2f.' % avmag
print 'The standard deviation is %f' % SD
print "There were %d points (%5.2f%%) more than 3 standard deviations from the mean\n%d points (%5.2f%%) more than 4 SD's from the mean.\nThis was from a total of %d points." % (l, (100*l/len(mag)), n, (100*n/len(mag)), len(mag))


plt.plot(t,mag,'o')
plt.errorbar(t,mag, yerr=err, linestyle='None')
plt.show()

plot_hist(SDs, 50, 'Number of standard deviations from the mean')