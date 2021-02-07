import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import hashlib
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import binary_erosion
from operator import itemgetter


def fingerprint(raw_data, plot: bool=False):
	''' Returns fingerprint of raw data file

	:params raw_data: raw data from read_file or read_dir in main file
	:returns: list of hashes in the form (hash, time offset)
	'''

	return get_hash(get_peaks(specgram(raw_data), plot=plot))


def specgram(raw_data):
	''' Returns 2D array of spectrogram image 

	:params raw_data: the raw numbers data from song file via read_file
	:returns : 2D array of spectrogram
	'''
	# size of window i.e. the number of samples that compose signal
	window_size = int(2**13)

	# number of sample points that overlap
	# 0.5 seems closest to actual time length
	window_overlap = 0.5 * window_size 
	sampling_rate = 44100

	# code below heavily borrowed from worldveil's dejavu project

	arr2D,_ ,_  = mlab.specgram(
		raw_data,
		NFFT=window_size,
		Fs=sampling_rate,
		window=mlab.window_hanning,
		noverlap=window_overlap)

	# logarithmic scale for amplitude
	arr2D = np.log10(arr2D, where=(arr2D != 0), out=np.zeros_like(arr2D))

	return arr2D

def get_peaks(spectrogram, min_amp=0, plot=False):
	''' Identifies peaks in the spectrogram

	:param spectrogram: 2D array from specgram 
	:param min_amp: point should have amplitude greater than min_amp to even be considered a peak
	:param plot: if true, displays the spectrogram and the detected peaks 
	:returns : list of detected peaks. Peaks have coordinates of the form (frequency, time) 
	'''

	# code below heavily borrowed from worldveil's dejavu project

	''' morphology mask is of the form : 
			T T T
			T T T ...
			T T T
			  .			
	'''
	mask_size = 19 # should be odd so that there's a center
	mask = np.ones((mask_size, mask_size), dtype=bool)

	# points in spectrogram that have the greatest amplitudes in their 
	# respective square neighborhoods 
	peaks_loc = maximum_filter(spectrogram, footprint=mask) == spectrogram

	# make the peaks sharper by eroding the background
	background = (spectrogram == 0)
	eroded_background = binary_erosion(background, structure=mask, border_value=1)

	detected_peaks = peaks_loc != eroded_background

	''' Actual values of spectrogram array are the amplitudes, whereas the frequency and 
	times are represented by the coordinates i.e. the position of the amplitude value in the matrix
	'''	
	amps = spectrogram[detected_peaks]
	# minimum threshold amplitude
	filtered_idx = np.where(amps > min_amp)[0]

	p_freq, p_time = np.where(detected_peaks) 
	freq, time = p_freq[filtered_idx], p_time[filtered_idx]

	print(detected_peaks)

	if plot:
		fig = plt.figure()
		ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
		bounds = [0, 5000, 0, 4000]
		ax1.imshow(spectrogram, extent=bounds, cmap='plasma')
		ax2.imshow(detected_peaks, extent=bounds)
		plt.show()

	return list(zip(freq, time))

def get_hash(peaks, fanout=10):
	''' Hashes the list of peak coordinates 

	:param peaks: list of peak coordinates found in get_peaks
	:param fanout: the number of points that should be associated with a given anchor point
	:returns : list of the form [(hash, absolute time offset)], offset being the time of the anchor point
	'''
	fingerprint = []

	# sort peaks by time
	peaks.sort(key=itemgetter(1))

	peak_num = len(peaks)
	for anchor in range(peak_num):
		# anchor point designated as the point that occurs 3 steps before the first target in the ordering 
		for target in range(3, 3 + fanout):
			if anchor + target < peak_num:
				freq1 = peaks[anchor][0]
				freq2 = peaks[anchor + target][0]
				time1 = peaks[anchor][1]
				time2 = peaks[anchor + target][1]

				# hash together freq1 + freq2 + (time delta)
				hashed = multi_hasher([freq1, freq2, time2-time1])

				fingerprint.append((hashed.hexdigest(), time1))

	return fingerprint

def multi_hasher(hash_list):
	''' Helper function that hashes together multiple inputs 

	:param hash_list: list of input values
	:returns : a hashlib object of the hash
	'''
	combined = ""

	# separate each input in the hash with '|'
	for i in hash_list:
		combined += str(i) + "|"

	combo_hash = hashlib.sha1(combined.encode('utf-8'))
	return combo_hash # returns hashlib object






