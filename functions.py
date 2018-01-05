from decimal import *
import binascii

def extract_filename(midiFile):
    if midiFile.rfind('/') == -1:
        return midiFile[:-4]
    else:
        return midiFile[midiFile.rfind('/')+1:-4]

def read_file(midiFile):
    #reads a midi file converting its contents into a string of hex numbers.
    mfile = open(midiFile, 'rb')
    midiHex = binascii.hexlify(mfile.read())
    print midiHex
    mfile.close() #changed .close to .close() suspected mistake
    return midiHex
    
def check_length(track):
    #extracts the length of a track in chars.
    return (int(track[8:16], 16)*2)
    
def return_range(track, i, bottom, top): 
    #returns a string of characters from a track in a given range.
    return track[(i + 16 + bottom):(i + 16 + top)]
    
            
def get_delta_time(i, track):
    d = return_range(track,i,0,2)
    
    if int(d, 16) >= 128:
        if int(return_range(track,i,2,4), 16) >= 128:
            if int(return_range(track,i,4,6), 16) >= 128:
                d = return_range(track,i,0,8)
                i += 8
            else:
                d = return_range(track,i,0,6)
                i += 6    
        else:
            d = return_range(track,i,0,4)
            i += 4  
    else:
        i += 2
        
    dInt = delta_time_to_int(d)
        
    return (i, dInt)
    
def delta_time_to_int(d):
    dBinary = ''
    i=0
    while i < (len(d)-1):
        byte = d[(0+i):(2+i)]
        dEightBitBinary = bin(int(byte, 16))[2:].zfill(8)
        dSevenBitBinary = dEightBitBinary[1:]
        dBinary = ''.join([dBinary, dSevenBitBinary])
        i += 2
    return int(dBinary, 2)
    
def get_event_type(i, track):
    return return_range(track,i,0,2)
    
def return_adjustment(runningMode):
    if runningMode == False:
        return 0
    elif runningMode == True:
        return -2
        
def collapse_events(track, events):
    collapsed = ''
    for i in events:
        collapsed = ''.join([collapsed, i.collapse()])
    collapsed = ''.join(['4d54726b', track[8:16], collapsed])
    return collapsed
    

    

    
    
    
    
    
    
    
