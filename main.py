from fingerprint import fingerprint
from utils import mp3_to_wav
import database as db

from pydub import AudioSegment
from hashlib import shake_128
import os
import numpy as np
from microphone import MicrophoneRecognizer


def unique_file(file_path):
	''' Hashes the file path to make a unique identifier of file

	:param file_path: file path relative to the parent folder audioplay 
					NOT the absolute file path
	:returns : hash of file path
	'''
	if os.path.exists(file_path):
		unique_id = shake_128(file_path.encode('utf-8'))
		return unique_id.hexdigest(8)
	else:
		print("File not found.")
	

def read_file(file_name, fingerprint=True):
	''' Returns raw data of file to be read into other fingerprint functions

	:param file_name: file path string
	:param fingerprint: 
	:returns : 
		if fingerprint = True, return a tuple of the form ([list: raw data], int: file_path hash)
		if not, return a list of raw data
	'''
	audiofile = AudioSegment.from_file(file_name)

	# bass might drown out other frequencies
	audiofile = audiofile.high_pass_filter(20)
	raw_data = np.frombuffer(audiofile.raw_data, np.int16)

	if fingerprint:
		return (raw_data, unique_file(file_name))
	else: 
		return raw_data

def read_dir(file_path):
	''' Returns list of raw data of every file in directory

	:param file_path: file path string
	:returns : a list of lists of numbers, raw data of each file in dir
	'''
	raw_datas = []
	try:
		for file in os.scandir(file_path):
			if file.name.endswith(".wav"):
				raw_datas.append(read_file(file, fingerprint=True))
	except FileNotFoundError:
		print("Directory not found")

	return raw_datas

def register_file(file_name, song_name):
	''' Registers file in database

	:param file_name: file path
	:param song_name: string of song name 
	'''
	raw_data, unique_id = read_file(file_name)
	hashes = fingerprint(raw_data)

	db.store_song(hashes, unique_id, song_name)

def delete_file(file_name):
	''' Deletes file's fingerprint / information from database

	:param file_name : file path
	'''
	song_id = unique_file(file_name)
	db.delete_song(song_id)

def get_scores(matches):
	''' Scores each song in list. The score is determined by organizing the time offset data into bins, then taking 
	the number of elements in the maximal bin.

	:param matches: dictionary of matched songs
	:returns : dictionary of the form {song_id : score}
	'''
	score_list = {}

	for song in matches.keys():
		hist, _ = np.histogram(matches[song])
		score_list[song] = np.max(hist)

	return score_list

def get_top_scored(score_list):
	''' Gets name of top scored song 

	:param score_list: dictionary of the form {song_id : score} (from get_scores)
	:returns : song name of top scored song
	'''
	sorted_scores = sorted(score_list, key=score_list.get, reverse=True)
	# print(sorted_scores)
	top_song = db.get_song_info(sorted_scores[0])

	return top_song

def identify_file(file_name):
	''' Identify song from file

	:param file_name: file path
	:returns : song name of matched song
	'''
	raw_data = read_file(file_name, fingerprint=False)
	matches = db.get_matches(fingerprint(raw_data))

	return get_top_scored(get_scores(matches))

def identify_mic(seconds=5):
	''' Identify song from microphone

	:param seconds: number of seconds to record
	:returns : song name of matched song
	'''
	mic = MicrophoneRecognizer()
	mic.record(seconds=seconds)
	matches = db.get_matches(fingerprint(mic.data))
	scores = get_scores(matches)
	#print(scores)
	return get_top_scored(scores)

