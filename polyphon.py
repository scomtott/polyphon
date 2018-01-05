from sys import argv
from decimal import *
from pyx import *
from operator import itemgetter
import binascii
import populate
import eventslistpopulator
import functions
import overlay
import tracknotes
import itertools
import copy
import math

class Midi(object):
    #object that contains midi header data, a list of the tracks
    #contained within the midi and various lists required to create
    #the polyphon coordinates.
    
    def __init__(self):
        
        self.listOfTracks = populate.track_list(midiHex)
        self.tracksOneToEnd = self.listOfTracks[1:]
        
        self.header = populate.header_info(self.listOfTracks[0])
        
        self.listOfTrackDicts = []
        for i, track in enumerate(self.tracksOneToEnd):
            self.listOfTrackDicts.append(eventslistpopulator.populate(i+1, track))
            
        self.listOfAllEvents = populate.all_events(self.listOfTrackDicts)
        
        self.listOfTempos = populate.midi_tempos(self.listOfTrackDicts)       
        self = populate.real_times(self)
        
        
    def collapse(self):
        #a method to check whether any bugs are introduced during the splitting
        #up of the midi into events.
        """ NEEDS FIXING """
        self.collapsed = []
        for j in range(0,len(self.listOfTrackDicts)):
            self.collapsed.append(functions.collapse_events(
                                        self.tracksOneToEnd[j],
                                        self.listOfTrackDicts[j]['allEvents']))
                                        
            if self.collapsed[j] == self.tracksOneToEnd[j]:
                print "HOORAY!"
            else:
                print "BOOOOO!"
                
class Polyphon(object):
    
    def __init__(self):

        self.allNoteEvents = []
        for k in sorted(midi.listOfAllEvents):
            if k.eventType[0] == '8' or k.eventType[0] == '9':
                self.allNoteEvents.append(k)
                
        self.noteTimings = populate.note_timings(self.allNoteEvents)
        self.imageNotes = populate.image_notes(self.noteTimings)
        self.trackNotes = tracknotes.return_notes()
        self.polyphonTracks = populate.polyphon_tracks(self.trackNotes, self.imageNotes)
        self.polyphonTracks = populate.all_available_tracks(self.polyphonTracks)
        self.polyphonTracks = populate.note_angles(self.polyphonTracks)
     
        
    def evaluate_7mm_rule(self):
        #Checks whether all notes obey the 7mm rule. i.e. if the minimum
        #linear distance between any two consecutive notes on the same track
        #falls below 7mm.
        
        tooCloseCount = 0
        sevenMmRule = Decimal(7)
        textFileOutput = filename + ".txt"
        f = open(textFileOutput, 'w')
        fileLines = []
        for k in self.polyphonTracks:
            minAngle = ((sevenMmRule / k[1]) / (2 * Decimal(math.pi))) * 360
            secondsPerDegree = Decimal(105)/Decimal(360)
            
            
            for i, angle in enumerate(k[5]):
                if i == 0:
                    angleBuff = angle[0]
                    continue
                    
                if angle[0] - angleBuff < minAngle:
                    fileLines.append("too close on track: " + str(k[0]))
                    fileLines.append("\n")

                    fileLines.append("(difference between notes " + \
                        str((angle[0] - angleBuff)*secondsPerDegree) + ") < " + \
                        "(minimum time " + str(minAngle*secondsPerDegree) + ")")
                    fileLines.append("\n")
                          
                    
                    if (angle[0] - angleBuff) == Decimal(0):
                        fileLines.append("two notes cannot occur on this " + \
                        "track at the same time")
                    else:
                        fileLines.append("note separation needs to be " + \
                            str(int((minAngle/(angle[0] - angleBuff))*100) - 100) + \
                            "% larger")
                            
                    fileLines.append("\n")
                    
                    fileLines.append("\n")
                    
                    tooCloseCount += 1
                    angleBuff = angle[0]
                    continue
                    
            
                angleBuff = angle[0]
        fileLines.append("too close count: " + str(tooCloseCount))
        for line in fileLines:
            f.write(line)
        f.close()
        
    def create360Warnings(self, warningTracks):
        warningFile = filename + "_360warnings.txt"
        with open(warningFile, 'w') as f:
            for track in warningTracks:
                for note in track:
                    line = "Track: " + str(note[0]) + \
                           " Start: " + str(round(note[1]*100.0, 1)) + \
                           "%" + " End: " + str(round(note[2]*100.0, 1)) + "%" +"\n"
                    f.write(line)
        
    def create_visualisation(self):
    
        text.set(mode="latex")
        text.preamble(r'\usepackage{lmodern}')
        canv = canvas.canvas()
        #changed offset from 10 to 0
        offset = 0
        
        for i in range (1, 121):
            #Creates the guiding line for each track and the "Track x" text
            #at the beginning of each line.
            p = path.line(0, i*2, 360, i*2)
            canv.stroke(p, [style.linewidth(0.05), style.linestyle.solid])
            txt = "Track " + str(i)
            textArg = r'\fontsize{60}{20}\selectfont %s' % txt
            canv.text(0,i*2,textArg)
        
        sevenMmRule = Decimal(7)
        warningTracks = []
        for pTrack in self.polyphonTracks:
            minAngle = ((sevenMmRule / pTrack[1]) / (2 * Decimal(math.pi))) * 360
            angleBuff = 0
        
            if not pTrack[5] == []:
                notesPast360 = []
                notesWithin5pc = []
                for c, note in enumerate(pTrack[5]):
                
                    if note == []:
                        continue
                        
                    position = note[0] + offset
                    fPosition = float(position)
        
                    p = path.line(fPosition, pTrack[0]*2, fPosition + 0.5, pTrack[0]*2)
                    minP = path.line(fPosition, pTrack[0]*2, fPosition + float(minAngle), pTrack[0]*2)
                    
                    if (note[0] - angleBuff) < minAngle and (note[0] - angleBuff) >= 0.000001 and not (c == 0):
                        canv.stroke(minP, [style.linewidth(0.25), style.linestyle.solid, color.rgb.blue])
                        canv.stroke(p, [style.linewidth(0.5), style.linestyle.solid, color.rgb.red])
                    elif (note[0] - angleBuff) < minAngle and (note[0] - angleBuff) < 0.000001 and not (c == 0):
                        canv.stroke(minP, [style.linewidth(0.25), style.linestyle.solid, color.rgb.blue])
                        canv.stroke(p, [style.linewidth(0.5), style.linestyle.solid, color.rgb.green])
                    #added the below elif to check if notes go on past 360 degrees
                    elif (fPosition + float(minAngle)) >= 360:
                        notesPast360.append([pTrack[0], fPosition/360.0, (fPosition + float(minAngle))/360.0])
                        canv.stroke(minP, [style.linewidth(0.25), style.linestyle.solid, color.rgb.green])
                        canv.stroke(p, [style.linewidth(0.5), style.linestyle.solid])
                    else:
                        if (fPosition + float(minAngle)) >= 360.0*0.95:
                            notesWithin5pc.append([pTrack[0], fPosition/360.0, (fPosition + float(minAngle))/360.0])
                        canv.stroke(minP, [style.linewidth(0.25), style.linestyle.solid, color.rgb.blue])
                        canv.stroke(p, [style.linewidth(0.5), style.linestyle.solid])
                    angleBuff = note[0]
                if notesPast360:
                    warningTracks.append(notesPast360)
                #print notesWithin5pc
        self.create360Warnings(warningTracks)
        canv.writePDFfile(filename)
        
    def create_projections(self):
        trackProjections = []
        highlightedProjections = []
        for i, pTrack in enumerate(self.polyphonTracks):
            trackProjections.append([])
            #print pTrack
            for note in pTrack[5]:
                noteProjection = (Decimal(160000) / Decimal(360)) * note[0]
                trackProjections[i].append(Decimal(160000) - noteProjection)
                print note[1]
                if note[1] == 127:
                    highlightedProjections.append(int(Decimal(160000) - noteProjection))
                
        tempMin = Decimal(160000)
        tempMax = Decimal(0)
        
        for track in trackProjections:
            for proj in track:
                if proj > tempMax:
                    tempMax = proj
                if proj < tempMin:
                    tempMin = proj
        
        projBuffer = (((tempMax - Decimal(160000)) + tempMin)/Decimal(2))
        
        tempTrackProjections = copy.deepcopy(trackProjections)
        for i, track in enumerate(tempTrackProjections):
            for j, proj in enumerate(track):
                trackProjections[i][j] = (proj - projBuffer).quantize(0)
               
         
        if True:
        
            textFileOutput = filename + "_projections" + ".txt"
            orderedTextFile = filename + "_ordered" + ".txt"
            textFileProjections = []
            orderableProjections = []
            
            for i, track in enumerate(trackProjections):            
                if track == []:
                    textFileProjections.append("te\n")
                    continue
                else:
                    for j, note in enumerate(track):
                        textFileProjections.append("t" + str(i + 1) + \
                                                   "p" + str(j + 1) + \
                                                   "-" + str(note) + "\n")
                        proj = []
                        proj.append("t" + str(i + 1) + "p" + str(j + 1))
                        proj.append(note)
                        orderableProjections.append(proj)
                        
                textFileProjections.append("te\n")
            orderedProjections = sorted(orderableProjections, key=itemgetter(1))
            
            #print orderedProjections
            
            overlay.create_overlay(orderedProjections)
                       
            with open(textFileOutput, 'w') as projFile:
                for item in textFileProjections:
                    projFile.write(item)
                    
            with open(orderedTextFile, 'w') as ordFile:
                for item in list(reversed(orderedProjections)):
                    ordFile.write(item[0] + " " + str(item[1]) + "\n")
        highlightedProjections.sort()
        print highlightedProjections            
#Set Decimal type precision to 12
getcontext().prec = 12
getcontext().rounding = "ROUND_HALF_UP"

script, midiFile = argv
filename = functions.extract_filename(midiFile)

#read midi file specified by 'filename'
midiHex = functions.read_file(midiFile)

midi = Midi()

polyphon = Polyphon()        
            
polyphon.evaluate_7mm_rule()

polyphon.create_visualisation()

polyphon.create_projections()
