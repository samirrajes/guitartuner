import sounddevice as sd
import numpy as np
import scipy.fftpack
import os

# General settings
SAMPLE_FREQ = 44100 # sample frequency in Hz
WINDOW_SIZE = 44100 # window size of the DFT in samples
WINDOW_STEP = 21050 # step size of window
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ # length of the window in seconds
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ # length between two samples in seconds
windowSamples = [0 for _ in range(WINDOW_SIZE)]

CONCERT_PITCH = 440
NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]

# finds the closest whole note and pitch to the inputted reference pitch
def find_note(pitch):
    # get # of half steps between reference pitch and concert pitch
    x = int(np.round(12 * np.log2(pitch/CONCERT_PITCH)))
    cnote = NOTES[x%12] + str(4 + (x + 9) // 12)
    cpitch = CONCERT_PITCH * 2 ** (x/12)
    return cnote, cpitch

# sd callback function
def callback(indata, frames, time, status):
  global windowSamples
  if status: print(status)
  if any(indata):
    windowSamples = np.concatenate((windowSamples,indata[:, 0])) # append new
    windowSamples = windowSamples[len(indata[:, 0]):] # remove old
    
    # we get the magnitude spectrum using a fast fourier transform ***
    magnitudeSpec = abs( scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2] )
 
    # dealing with background whitenoise
    # sets all frequencies below 62Hz to 0Hz
    for i in range(int(62/(SAMPLE_FREQ/WINDOW_SIZE))):
      magnitudeSpec[i] = 0 #suppress mains hum

    # find and use the highest frequency peak to find the closest note and pitch
    maxInd = np.argmax(magnitudeSpec)
    maxFreq = maxInd * (SAMPLE_FREQ/WINDOW_SIZE)
    closestNote, closestPitch = find_note(maxFreq)

    os.system('cls' if os.name=='nt' else 'clear')
    print(f"Closest note: {closestNote} {maxFreq:.1f}/{closestPitch:.1f}")
  else:
    print('no input')

# Start the microphone input stream
try:
  with sd.InputStream(channels=1, callback=callback,
    blocksize=WINDOW_STEP,
    samplerate=SAMPLE_FREQ):
    while True:
      pass
except Exception as e:
    print(str(e))

    