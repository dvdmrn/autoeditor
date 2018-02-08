"""
    assumes wavefile will have two parts the user wants to cut i.e. -----\/\/\/\/---\/\/\/\/\/---
    it then creates two new wave files: part 1, part 2

    INPUT WAVEFILE REQUIREMENTS:
        - 16bit pcm
        - 44100 Hz
        - mono
"""
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
    threshold = 650

    minimumTimeBetweenCuts = 1 # in seconds

    cutTimeChunks = int(RATE*minimumTimeBetweenCuts) / 512 # the minimum time to wait to make an edit, in chunks.

    chunksOfSilence = 0

    f = wave.open(filepath,"rb")  
    print("\n\nopening: "+filepath)
    print("samplerate: "+str(f.getframerate()))
    print("frames: "+str(f.getnframes()))
    print("channels: "+str(f.getnchannels()))
    print("sample width: "+str(f.getsampwidth()))

    # setup wave files -- \
    wv0 = wave.open('edit0.wav', 'w')
    wv0.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
    wv0Data="" 

    wv1 = wave.open('edit1.wav', 'w')
    wv1.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
    wv1Data="" 
    #                 -- /


    # control flow for wave partitioning
    part1 = False
    part2 = False
    interlude = False

    maxVol=2**15-1.0 # maximum amplitude
    # this is just handy to have onhand
    # explaination:
    # for 16 bit audio, amp ranges from +32768 : -32768
    # this is because 2^16 = 65536, and 65536/2 = 32768

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
            if not interlude:
                if data: 
                    # get amplitude of chunk
                    amp = rms(subSamples[0:chunk-1]) # amp
                    ezToRead.append(amp) # array of amps
                    # -- write wave info
                    # -- cut if amp is below threshold

                    if amp > threshold:
                        part1 = True
                        for d in range(0,len(subSamples)-1):
                            wv0Data += pack('h', subSamples[d][0])
                    else:
                        if part1:
                            for d in range(0,len(subSamples)-1):
                                wv0Data += pack('h', subSamples[d][0])
                            # we are at least in part 1, and we have now reached silence.
                            chunksOfSilence += 1
                        if chunksOfSilence > cutTimeChunks:
                            interlude = True # we are prob in the interlude as we have exceeded our time threshold

                    subSamples = []
            else:
                if data: 
                    # get amplitude of chunk
                    amp = rms(subSamples[0:chunk-1]) # amp
                    ezToRead.append(amp) #array of amps
                    # -- write wave info
                    # -- cut if amp is below threshold
                    if amp > threshold:
                        part2 = True
                        for d in range(0,len(subSamples)-1):
                            wv1Data += pack('h', subSamples[d][0])
                    elif part2:
                        for d in range(0,len(subSamples)-1):
                            wv1Data += pack('h', subSamples[d][0])

                    subSamples = []

    # write file
    print("writing file 1...")
    wv0.writeframes(wv0Data)
    wv0.close()

    print("writing file 2...")
    wv1.writeframes(wv1Data)
    wv1.close()
    print("editing complete!")

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

process_wave("raw_minpair_stimuli/male/fricatives/fricativeVoicing_Untitled 46.wav")