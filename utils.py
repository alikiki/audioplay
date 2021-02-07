from pydub import AudioSegment
import numpy as np
import os

def mp3_to_wav(file_name, seconds=None):
	''' Converts mp3 to wav, and also stereo to mono

	:param file_name: file path 
	:param seconds : keep only the first n seconds of the song. NoneType by default
	'''
	audiofile = AudioSegment.from_file(file_name)
	audiofile = audiofile.set_channels(1) # convert to mono

	# file name 
	new_name = file_name[:-4]
	if seconds != None:
		audiofile = audiofile[:seconds * 1000]
		new_name = file_name[:-4] + "_" + str(seconds)

	audiofile.export(new_name + ".wav", format="wav") 

	if not file_name.endswith('.wav'):
		os.remove(file_name)
		print(file_name + " removed.")


def slicer(file_name, start, end):
	''' Exports user-chosen snippet of song 
	
	:param file_name : file path
	:param start : second at which snippet should start
	:param end : second at which snippet should end
	'''
	audiofile = AudioSegment.from_file(file_name)
	audiofile = audiofile[start * 1000 : end * 1000]
	new_name = file_name[:-4] + "_sliced_" + str(start) + "-" + str(end) + ".wav"

	audiofile.export(new_name, format='wav')


