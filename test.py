import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import hashlib
from scipy import misc
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import binary_erosion
from operator import itemgetter
from main import read_file

def sinecoswave(freq=1, amp=1):
	time = np.arange(0, 10, 0.1)
	sine_fn = amp * (np.sin(freq * time))
	cose_fn = amp * (np.cos(freq * time))

	plt.plot(time, sine_fn, time, cose_fn)
	plt.xlabel('Time')
	plt.title('Sinusoidal Functions')
	plt.legend(['sine', 'cosine'])
	plt.show()

def adder():
	time = np.arange(0,20, 0.1)

	f1 = np.sin(1*time)
	f2 = np.sin(1.4*time)
	f3 = 2*np.cos(1.7*time)
	f4 = 3*np.sin(1.2*time)

	added = f1 + f3 + f4

	fourier = np.fft.fft(added)/len(added)
	fourier = fourier[range(int(len(added)/2))]

	plt.plot(time, added)
	plt.plot(time, f1, alpha=0.2)
	plt.plot(time, f3, alpha=0.2)
	plt.plot(time, f4, alpha=0.2)
	plt.xlabel('Time')
	plt.title('Waveform and Its Constituents')
	plt.show()

def morphology(size=19):
	fig = plt.figure()
	plt.gray()  # show the filtered result in grayscale
	ax1 = fig.add_subplot(131)  # left side
	ax2 = fig.add_subplot(132)  # right side
	ax3 = fig.add_subplot(133)
	ascent = misc.ascent()
	masked = maximum_filter(ascent, 
		footprint=np.ones((size,size), dtype=bool))
	peaks = masked == ascent
	ax1.imshow(ascent)
	ax2.imshow(masked)
	ax3.imshow(peaks)

	ax1.set_title('Original')
	ax2.set_title('Mask Applied')
	ax3.set_title('Identified Peaks')
	plt.show()

def waveform(list):
	return np.sin(list) + np.cos(0.4*list) + np.sin(0.3*list) + np.sin(2*list)

def sample(speed, length=20):
	sampled_time = np.arange(0, length, speed)
	analog_time = np.arange(0, length, 0.1)
	analog_fn = waveform(analog_time)
	sample_fn = waveform(sampled_time)

	fig = plt.figure(figsize=[10,5])
	ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
	ax2.plot(analog_time, analog_fn, alpha=0.15)
	ax2.plot(analog_time, analog_fn, 'k.')
	ax2.set_title('Fast sample rate')
	ax1.plot(analog_time, analog_fn, alpha=0.15)
	ax1.plot(sampled_time, sample_fn, 'k.')
	ax1.set_title('Slow sample rate')
	plt.show()

def mess_discern(speed, length=20):
	sampled_time = np.arange(0, length, speed)
	sampled_fn = waveform(sampled_time)

	analog_time = np.arange(0, length, 0.05)
	analog_fn = waveform(analog_time)

	plt.plot(analog_time, analog_fn, alpha=0.0)
	plt.plot(sampled_time, sampled_fn, 'k.')
	plt.show()

sample(1.8)