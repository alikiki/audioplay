import click
import os
from main import *
from database import init_db, get_songs
from utils import mp3_to_wav

@click.group()
def cli(): 
	pass

@click.command(help="Initialize fingerprint database (run first)")
def init():
	init_db()

@click.command(help="Convert mp3 to mono wav")
@click.argument('path')
@click.option(
	'--cut', 
	default=None, 
	type=int,
	help='Keeps only first n seconds. The rest of the file will be cut.')
def prep(path, cut):
	if os.path.isdir(path):
		for file in os.scandir(path):
			if file.name.endswith('.mp3') or file.name.endswith('.wav'):
				mp3_to_wav(os.path.join(path, file.name), seconds=cut)
	else:
		mp3_to_wav(path, seconds=cut)

@click.command(help="Register a song")
@click.argument('path')
@click.argument('song_name')
def register(path, song_name):
	register_file(path, song_name)

@click.command(help="Delete a song")
@click.argument('path')
def delete(path):
	delete_file(path)

@click.command(help="See all identified songs")
def see():
	for _, song, _ in get_songs():
		click.echo(song)

@click.command(help="Identify a song by file or microphone")
@click.option('--mic', 
	default=None, 
	type=int, 
	help='Number of seconds to record using the microphone.')
@click.option('--file', 
	default=None,
	type=str,
	help='Identify a file.')
def ID(mic, file):
	if file != None and mic != None:
		click.echo('Please choose either mic or file.')
	elif mic != None:
		click.echo('Identified: %s' % identify_mic(mic))
	else:
		click.echo('Identified: %s' % identify_file(mic))

cli.add_command(init)
cli.add_command(prep)
cli.add_command(register)
cli.add_command(delete)
cli.add_command(see)
cli.add_command(ID)

if __name__ == '__main__':
	cli()