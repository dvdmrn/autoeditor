import pyaudio
import wave
from struct import pack, unpack
from math import sqrt
import os

def process_wave(filepath):
    """
        If rms amplitude is above threshold, keep it in, if it's below threshold, cut it out.
        filepath := a string
        returns: nothing
    """
RATE=44100
chunk = 512
threshold = 1000

minimumTimeBetweenCuts = 0.5 # in seconds

cutTimeChunks = int(RATE*minimumTimeBetweenCuts) / 512 # the minimum time to wait to make an edit, in chunks.

    f = wave.open(filepath,"rb")  
    print("\n\nopening: "+filepath)
    print("samplerate: "+str(f.getframerate()))
    print("frames: "+str(f.getnframes()))
    print("channels: "+str(f.getnchannels()))
    print("sample width: "+str(f.getsampwidth()))

    ## GENERATE STEREO FILE ##
    wv = wave.open('temp-edited.wav', 'w')
    wv.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
    maxVol=2**14-1.0 # maximum amplitude
    wvData="" # c string
    i = 0
    subSamples = []

    ezToRead = []

    for i in range(0, f.getnframes()):
    
        frameSample = f.readframes(1)
        # print frameSample
        # print len(frameSample)
        if len(frameSample):
            try:
                data = unpack('h',frameSample)
                subSamples.append(data)
            except:
                print ("Unpacking error, may be from an invalid frameSample")
                print ("frame sample length: "+str(len(frameSample)))
                print ("frame sample string: "+frameSample)
            
        else:
            data = 0
        if (i % chunk == 0 and i != 0) or (i == f.getnframes()-1):    
            if data: 
                # get amplitude of chunk
                amp = rms(subSamples[0:chunk-1]) # amp
                ezToRead.append(amp) #array of amps
                # -- write wave info
                # -- cut if amp is below threshold
                if amp > threshold:
                    for d in range(0,len(subSamples)-1):
                        wvData += pack('h', subSamples[d][0])
                subSamples = []

            else:
                break
    wv.writeframes(wvData)
    wv.close()
    print("amp data: ",ezToRead)
    print("processed file!")

def rms(samples):
    """
        returns the root mean square of an list of samples
        samples := a list
        returns: a float
    """
    sumOfSquares = 0

    for sample in samples:
        sumOfSquares += sample[0]**2

    return sqrt(sumOfSquares/float(len(samples)))

process_wave("1214_p1_hearth_m.wav")