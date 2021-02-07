import sqlite3 as sql
import fingerprint

def get_cursor():
	''' Connect to database and get cursor
	'''
	cxn = sql.connect("fingerprint.db")

	return cxn, cxn.cursor()

def init_db():
	''' Initialize database with necessary tables 
	'''
	cxn, c = get_cursor()

	# hash = hashed peak from fingerprint.get_hash
	# offset = absolute time offset from fingerprint.get_hash
	# song_id = unique file hash from main.unique_file
	c.execute('''CREATE TABLE IF NOT EXISTS fingerprints (
			hash text not null,
			offset int not null,
			song_id text not null
		);''')

	# song_id = unique file hash from main.unique_file
	# song_name = song name (I'm too lazy so no artist field or anything)
	# fingerprinted = boolean (0 / 1) of whether or not song has been fingerprinted 
	c.execute('''CREATE TABLE IF NOT EXISTS songs (
			song_id text not null,
			song_name text not null,
			fingerprinted int default 0
		);''')

def drop_db():
	''' Deletes both fingerprints + songs tables 
	'''
	cxn, c = get_cursor()
	c.execute('''DROP TABLE fingerprints;''')
	c.execute('''DROP TABLE songs;''')
	cxn.commit()


def in_db(song_id=None, song_name=None):
	''' Returns if song is in database or not. Can search by id or song name

	:params song_id: unique file hash
	:params song_name: string of song name
	:returns : True, False, None
	'''
	cxn, c = get_cursor()

	if song_id == None and song_name == None:
		return None
	elif song_id != None: 
		c.execute('''SELECT 1 FROM songs WHERE song_id = ?''', (song_id,))
		return (c.fetchone() != None)
	elif song_name != None:
		c.execute('''SELECT 1 FROM songs WHERE song_name = ?''', (song_name,))
		return (c.fetchone() != None)
	

def store_song(hashes, song_id, song_name):
	''' Registers song + its fingerprints

	:param hashes: list of tuples in the form (hash, time offset) - meant to be 
		used in conjunction with fingerprint.fingerprint
	:param song_id: unique file hash (see main.py)
	:param song_name : string of song name - song_id not needed because of autoincrementing
	'''
	cxn, c = get_cursor()
	for h, off in hashes:
		c.execute('''INSERT INTO fingerprints VALUES (?, ?, ?);''', (h, int(off), song_id))
	c.execute('''INSERT INTO songs VALUES (?, ?, ?)''', (song_id, song_name, 1))
	cxn.commit()

def delete_song(song_id):
	''' Deletes a song's fingerprint and its information

	:param song_id: unique file hash (see main.py) - to be used in conjunction with unique_file(file_path)
	'''
	cxn, c = get_cursor()
	c.execute('''DELETE FROM fingerprints WHERE song_id =?;''', (song_id,))
	c.execute('''DELETE FROM songs WHERE song_id =?;''', (song_id,))
	cxn.commit()

def get_matches(hashes):
	''' Gets all song matches for inputted hashes

	:param hashes: list of tuples of the form (hash, absolute time offset)
	:returns: dictionary of the form {song_id : [list of time differences]}
	'''
	cxn, c = get_cursor()
	matches = {}

	for input_hash, input_time in hashes:
		c.execute('''SELECT * FROM fingerprints WHERE hash = ?''', (input_hash,))
		results = c.fetchall()
		for output_hash, output_time, song_id in results:
			t_delta = output_time - input_time
			matches.setdefault(song_id, []).append(t_delta)

	return matches

def get_song_info(song_id):
	''' Gets song name from song_id (inverse of unique hash essentially)
	
	:param song_id: unique file hash 
	:returns : song name 
	'''
	cxn, c = get_cursor()
	c.execute('''SELECT song_name from songs WHERE song_id=?''', (song_id,))
	return c.fetchone()[0]

def get_songs():
	''' Gets all available songs
	'''
	cxn, c = get_cursor()
	c.execute('''SELECT * from songs;''')
	return c.fetchall()

