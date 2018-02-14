"""
    assumes wavefile will have two parts the user wants to cut i.e. -----\/\/\/\/---\/\/\/\/\/---
    it then creates two new wave files: part 1, part 2

    INPUT WAVEFILE REQUIREMENTS:
        - 16bit pcm
        - 44100 Hz
        - mono

    TODO: 
        - set in point
        - set out point
        - then export from in and out point

"""
import pyaudio
import wave
from struct import pack, unpack
from math import sqrt
import os


paddingSeconds = 0.1 # in seconds
RATE=44100
chunk = 512
threshold = 4000
minimumTimeBetweenCuts = 0.5 # in seconds



def process_wave(filepath,saveas_0,saveas_1):
    """
        If rms amplitude is above threshold, keep it in, if it's below threshold, cut it out.
        filepath := a string
        returns: nothing
    """

    # --- cut spacing ---
    cutTimeChunks = int(RATE*minimumTimeBetweenCuts) / chunk # the minimum time to wait to make an edit, in chunks.
    chunksOfSilence = 0
    
    # --- i/o points ---
    inPoint = 0
    outPoint = 1
    paddingFrames = int(RATE*paddingSeconds) # in frames

    f = wave.open(filepath,"rb")  
    print("\n\nopening: "+filepath)
    print("samplerate: "+str(f.getframerate()))
    print("frames: "+str(f.getnframes()))
    print("channels: "+str(f.getnchannels()))
    print("sample width: "+str(f.getsampwidth()))

    # setup wave files -- \
    wv0 = wave.open(saveas_0, 'w')
    wv0.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))

    wv1 = wave.open(saveas_1, 'w')
    wv1.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
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
    allData = []

    for i in range(0, f.getnframes()-1):
        frameSample = f.readframes(1)
        if len(frameSample):
            d = unpack('h',frameSample)
            allData.append(d)

    f = wave.open(filepath,"rb")  

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

                    if amp > threshold: # reached start of pt1
                        if not part1:
                            print("amp",amp,i)
                            part1 = True
                            inPoint = max(0,i-paddingFrames)
                        
                        
                    else:
                        if part1:
                            chunksOfSilence += 1
                        if chunksOfSilence > cutTimeChunks:
                            outPoint = min(i+paddingFrames,f.getnframes()-1)
                            interlude = True # we are prob in the interlude as we have exceeded our time threshold
                            write_frames(inPoint,outPoint,allData,wv0,saveas_0)

                    subSamples = []
            else:
                if data: 
                    # get amplitude of chunk
                    amp = rms(subSamples[0:chunk-1]) # amp
                    # -- cut if amp is below threshold
                    if amp > threshold:
                        part2 = True
                        inPoint = max(0,i-paddingFrames)
                        outPoint = f.getnframes()-1

                        write_frames(inPoint,outPoint,allData,wv1,saveas_1)
                        break

                    subSamples = []

    # write file
 

   
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


def write_frames(i,o,data,wvFile,name):
    """
        i := an int (index of in point)
        o := an int (index of out point)
        data := a list of ints
        wvFile = a File Object
    """
    dataToWrite = ""
    print("trimming with [i:"+str(i)+",o:"+str(o)+"]")
    for d in range(i,o):
        sample = data[d][0]
        dataToWrite += pack('h', sample)
    
    print("writing file object: "+str(wvFile._file)+"...")
    wvFile.writeframes(dataToWrite)
    wvFile.close()
    print("    > wrote file: "+str(name))

# process_wave("stops_Untitled 177.wav","p0","p1")