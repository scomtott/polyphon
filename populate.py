from decimal import *
import binascii
import functions
import copy
              
def track_list(midiHex):

    listOfTracks = []
    numTracks = int(midiHex[20:24], 16)
    i = 0
    j = 0
    while j <= numTracks:
        trackLength = int(functions.return_range(midiHex, i, -8, 0), 16)*2
        thing = functions.return_range(midiHex, i, -16, trackLength)
        listOfTracks.append(functions.return_range(midiHex, i, -16, trackLength))
        i += (16 + trackLength)
        j += 1
    return listOfTracks
    
    
def header_info(header):
#returns an object with the header info stored in it.
    
    class Header(object):
    #creates an object with the header chunk info in it.
        
        def __init__(self, header):
            self.header = header
            self.fileFormat = int(self.header[16:20], 16)
            self.numTracks = int(self.header[20:24], 16)
            self.ticksPerQuarterNote = int(self.header[24:28], 16)
            
        def print_properties(self):
            print "The file format is %d." % self.fileFormat
            print "The number of tracks is %d." % self.numTracks
            print "There are %d ticks per quarter note." % self.ticksPerQuarterNote
            print "-"*50
    
    return Header(header)
    
def midi_tempos(listOfTrackDicts):
    tempos = []
    
    #extracts all tempo events from all tracks.
    for trackDict in listOfTrackDicts:
        for k in trackDict['allEvents']:
            if k.eventType[0] == 'f' and k.metaType == '51':
                tempos.append([k.cumulativeDeltaTime, int(k.data, 16)])
    
    #tempo events in a midi file [delta time at which to change tempo, new tempo]
    #so that the first tempo event has a delta time of 0
    #but this programme requires [delta time at which to change tempo, old tempo]
    #An additional tempo is added with the greatest possible tempo and all of the
    #delta times are shifted to the previous event with the first delta time (0)
    #being deleted e.g. [0, a] [1, b] [2, c] >> [1, a] [2, b] [4294967168, c]
    greatestDeltaTime = 4294967168
    tempos.append([greatestDeltaTime, 0])
    buff = []
  
    for tempo in tempos:
        buff.append(tempo[0])
    
    buff.pop(0)
    tempos.pop()

    for i in range(len(tempos)):
        tempos[i][0] = buff[i]
                
    return tempos
    
def all_events(listOfTrackDicts):
    listOfAllEvents = []
    
    for trackDict in listOfTrackDicts:
        for k in trackDict['allEvents']: 
            listOfAllEvents.append(k)
    
    return listOfAllEvents
    
def real_times(midi):
    #converts the delta times for midi events into a real time (in seconds)
    #based on information in the midi's header track such as the number of
    #ticks per quarter note and the various midi tempo events throughout
    #the other tracks.
    
    for trackDict in midi.listOfTrackDicts:
        #process is repeated separately for each midi track.
        
        cumulativeRealTime = Decimal(0)
        i = 0
        #this counter (i) is used to select the note event being evaluated.
        
        for tempo in midi.listOfTempos:
            #tempo[0] gives the delta time until which the tempo event is relevent.
            #tempo[1] gives the number of microseconds per quarter note
            while i < len(trackDict['allEvents']):
                
                if trackDict['allEvents'][i].cumulativeDeltaTime > tempo[0]:
                    #if the cumulative delta time of the current midi event
                    #exceeds the delta time at which the current tempo ceases
                    #to be relevant, exit the loop and move to the next tempo
                    #without incrementing to the next midi event.
                    break
                    
                cumulativeRealTime += (
                                (Decimal(trackDict['allEvents'][i].deltaTime) /
                                Decimal(midi.header.ticksPerQuarterNote)) * 
                                (Decimal(tempo[1])/Decimal(1000000)) )
                #Delta Time/(ticks/QN) * Seconds/QN
                #
                #        nQN           * Seconds/QN
                #
                #      nSeconds 
                #add this to the times of all the previous events and you have
                #the absolute time at which every event should occur.
                                
                trackDict['allEvents'][i].realTime = cumulativeRealTime
                i += 1
                
    return midi
    
def note_timings(allNoteEvents):
    def velocityTracking(velocities):
        intVelList = []
        i = 0
        for vel in velocities:
            intVelList.append(int(vel, 16))
            if int(vel, 16) == 127:
                i+=1
            
        #intVelList.sort(key=int)
        print intVelList
        print i
        
        
        
    timings = []
    velocities = []
    for event in allNoteEvents:
        note = []
        
        if event.eventType[0] == '8':
            note.append(False)
        elif event.eventType[0] == '9' and event.velocity == '00':
            note.append(False)
        elif event.eventType[0] == '9':
            note.append(True)
            #note tracking through velocity
            velocities.append(event.velocity)
            
            
        note.append(event.realTime)
        note.append(event.noteNumber)
        note.append(int(event.velocity, 16))
        
        timings.append(note)
        
    velocityTracking(velocities)
    #print timings
    return timings
    
def image_notes(note_timings):

    stack = []
    imageNotes = []
    for timing in note_timings:
        stack.append(timing)
        holder = []
        holder.append(timing)
        for item in stack:
            if item[2] == timing[2] and item[0] == (not timing[0]):
                holder.append(item)
                noteVal = holder[0][2]
                noteTimes = [holder[0][1], holder[1][1]]
                noteVel = holder[1][3]
                imageNotes.append([noteVal, noteTimes, noteVel])
                
                
                for a in holder:
                    for b in stack:
                        if b == a:
                            stack.remove(b)
                break
                
    #print imageNotes
    return imageNotes
    
def polyphon_tracks(trackNotes, imageNotes):
    #Builds the list of polyphon tracks.
    #Each list item (track) has the structure:
    # a[0, 1, 2, 3, 4[0[0, 1, 2], ... n[0, 1, 2]], 5[0, 1, 2, ... n]]
    #a[0] == Track number (1 to 120).
    #a[1] == Track radius as a Decimal object.
    #a[2] == Midi note number.
    #a[3] == Note number as a hex string '0xnn'.
    #a[4] == List of note events where:
    #           a[4][0] == note number as hex '0xnn'
    #           a[4][1] == note end time (in seconds) as Decimal object
    #           a[4][2] == note start time (as above)
    ### a[5] is not added until note_angles() is called later on.
    #a[5] == List of note angles as Decimal objects
    polyphonTracks = []
    for i, note in enumerate(trackNotes):
        pTrack = []
        pTrack.append(i+1)
        pTrack.append(Decimal(40.1)+(i*Decimal(1.589)))
        if type(note) is int:
            pTrack.append(note)
            pTrack.append(hex(note)[2:])
        else:
            pTrack.append('--')
            pTrack.append('--')
        pTrack.append([])
        polyphonTracks.append(pTrack)
        
    #This part populates the actual note events into polyphonTracks[4]
    for k in imageNotes:
        for pTrack in polyphonTracks:
            if k[0] == pTrack[3]:
                pTrack[4].append(k)
                break
    #print polyphonTracks
    return polyphonTracks
    
def all_available_tracks(polyphonTracks):
    #spreads out notes among all available polyphon tracks to maximise the
    #space between temporally consecutive notes.
    tmpPolyphonTracks = copy.deepcopy(polyphonTracks)
    
    prevTrack = ''
    for i, pTrack in enumerate(tmpPolyphonTracks):
        if not pTrack[4] == []:
            noteValue = pTrack[3]
            
            #counts the number of tracks that have the same note value (pTrack[3])
            #as the current track only if the track is different from the last. If
            #not, numSameTracks remains the same.
            if not pTrack[3] == prevTrack:
                numSameTracks = 0
                for k in tmpPolyphonTracks:
                    if noteValue == k[3]:
                        numSameTracks += 1
                    
                    
            poppedTrack = polyphonTracks[i][4]
            polyphonTracks[i][4] = []
            
            #cycles through all the tracks that have the same note value
            #distributing notes alternately amongst them:
            #Track 42 n n n n n n n n n
            #Track 42
            #Track 42
            #Becomes:
            #Track 42 n     n     n 
            #Track 42   n     n     n
            #Track 42     n     n     n
            trackCycler = 0
            for note in poppedTrack:
                polyphonTracks[i + trackCycler][4].append(note)
                trackCycler += 1
                if trackCycler == numSameTracks:
                    trackCycler = 0
                    
            prevTrack = pTrack[3]
    
    return polyphonTracks
    
def note_angles(polyphonTracks):
    #converts the start time of each note to an angle using the constant
    #degreesPerSecond where 360 degrees = 105 seconds.
    #The above mentioned a[5] of polyphonTracks.
    degreesPerSecond = (Decimal(360)/Decimal(105))
    for pTrack in polyphonTracks:
        pTrack.append([])
        if not pTrack[4] == []:
            for note in pTrack[4]:
                #print "note: ", note
                upper, lower = note[1]
                #changed from: pTrack[5].append(lower*degreesPerSecond)
                pTrack[5].append([lower*degreesPerSecond, note[2]])
                
    return polyphonTracks

