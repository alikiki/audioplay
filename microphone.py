import numpy as np
import pyaudio


class MicrophoneRecognizer():
    ''' Used for handling microphone recordings + input
    '''
    default_format = pyaudio.paInt16

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.data = []
        self.channels = 1
        self.chunksize = int(2**14)
        self.samplerate = 44100
        self.recorded = False

    def start_recording(self):
    ''' Starts recording
    '''
        print("> start recording")
        self.recorded = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = self.audio.open(
            format=self.default_format,
            channels=self.channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.chunksize,
            input_device_index=0)

    def process_recording(self):
    ''' Converts stream into number data
    '''
        print(".", sep=" ", end="", flush=True)
        data = self.stream.read(self.chunksize)
        nums = np.frombuffer(data, np.int16)
        self.data.extend(nums)

    def stop_recording(self):
    ''' Stops recording and saves recorded data
    '''
        print("\n> end recording")
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

        self.recorded = True
        self.data = np.array(self.data)

    def record(self, seconds=5):
    ''' Wrapped recording process

    :param: seconds : number of seconds to record
    '''
        self.start_recording()
        for i in range(0, int(self.samplerate / self.chunksize * int(seconds))):
            self.process_recording()
        self.stop_recording()





