from decimal import *
import binascii
import functions

def populate(trackNum, track):

    eventsDict = {'trackNum': None,
               'allEvents': [], 
               'f': [], 
               '8': [], 
               '9': [],
               'a': [],
               'b': [],
               'c': [],
               'd': [],
               'e': [],}
               
    #searches through the track string looking for meta and midi events.
    #A new object is created for each event found and stored in the dict
    #eventsDict.

#########################
#Event class definitions#
#########################

#There is a different class for each type of midi or meta event. Each class 
#has a print_properties() method which prints the properties of the event
#and a collapse() method which collapses the event object back into a string 
#and returns it.
#Midi events can be in running mode (indicated by runningMode == True,
#this will result in the event type being omitted from the collapsed string.
    
    class MetaEvent(object):
              
        def __init__(self, listLength, d, eventType, t, l, data, trackNum):
            self.id = listLength
            self.deltaTime = d
            self.type = 'meta'
            self.eventType = eventType
            self.metaType = t
            self.length = l
            self.data = data
            self.runningMode = ''
            self.cumulativeDeltaTime = cumulativeDeltaTime
            self.realTime = None
            self.trackNum = trackNum
            
        def __repr__(self):
            return "(%d) MetaEvent %d\n" % (self.trackNum, self.id) + \
                   "deltaTime: %s\n" % self.deltaTime + \
                   "cum delta time: %d\n" % self.cumulativeDeltaTime + \
                   "metaType: %s\n" % self.metaType + \
                   "length: %s\n" % self.length + \
                   "data: %s\n\n" % self.data
                   
        def __cmp__(self, other):
            if hasattr(other, 'cumulativeDeltaTime'):
                return (self.cumulativeDeltaTime).__cmp__(other.cumulativeDeltaTime)
                   
        def collapse(self):
            collapsed = (self.deltaTime + self.eventType + self.metaType +
                        self.length + self.data)
            return collapsed
            
            
    class NoteEvent(object):
        
        def __init__(self, listLength, d, eventType, noteNumber, velocity, runningMode, trackNum):
            self.id = listLength
            self.deltaTime = d
            self.type = 'note'
            self.eventType = eventType
            self.noteNumber = noteNumber
            self.velocity = velocity
            self.runningMode = runningMode
            self.cumulativeDeltaTime = cumulativeDeltaTime
            self.realTime = None
            self.trackNum = trackNum
            
        def __repr__(self):
            return "(%d) NoteEvent %d\n" % (self.trackNum, self.id) + \
                   "deltaTime: %s\n" % self.deltaTime + \
                   "cum delta time: %d\n" % self.cumulativeDeltaTime + \
                   "eventType: %s\n" % self.eventType + \
                   "noteNumber: %s\n" % self.noteNumber + \
                   "velocity: %s\n" % self.velocity + \
                   "runningMode: %s\n\n" % self.runningMode
                   
        def __cmp__(self, other):
            if hasattr(other, 'cumulativeDeltaTime'):
                return (self.cumulativeDeltaTime).__cmp__(other.cumulativeDeltaTime)                       
            
        def collapse(self):
            collapsed = self.deltaTime
            if self.runningMode == False:
                collapsed = ''.join([collapsed, self.eventType])
            collapsed = ''.join([collapsed, self.noteNumber, self.velocity])
            return collapsed
            
            
    class CcEvent(object):
    
        def __init__(self, listLength, d, eventType, contNum, newVal, runningMode, trackNum):
            self.id = listLength
            self.deltaTime = d
            self.type = 'cc'
            self.eventType = eventType
            self.contNum = contNum
            self.newVal = newVal
            self.runningMode = runningMode
            self.cumulativeDeltaTime = cumulativeDeltaTime
            self.realTime = None
            self.trackNum = trackNum
            
        def __repr__(self):
            return "(%d) CcEvent %d\n" % (self.trackNum, self.id) + \
                   "deltaTime: %s\n" % self.deltaTime + \
                   "cum delta time: %d\n" % self.cumulativeDeltaTime + \
                   "eventType: %s\n" % self.eventType + \
                   "contNumber: %s\n" % self.contNum + \
                   "new value: %s\n" % self.newVal + \
                   "runningMode: %s\n\n" % self.runningMode 
                   
        def __cmp__(self, other):
            if hasattr(other, 'cumulativeDeltaTime'):
                return (self.cumulativeDeltaTime).__cmp__(other.cumulativeDeltaTime)
            
        def collapse(self):
            collapsed = self.deltaTime
            if self.runningMode == False:
                collapsed = ''.join([collapsed, self.eventType])
            collapsed = ''.join([collapsed, self.contNum, self.newVal])
            return collapsed
            
            
    class PcEvent(object):
    
        def __init__(self, listLength, d, eventType, newProgNum, runningMode, trackNum):
            self.id = listLength
            self.deltaTime = d
            self.type = 'pc'
            self.eventType = eventType
            self.newProgNum = newProgNum
            self.runningMode = runningMode
            self.cumulativeDeltaTime = cumulativeDeltaTime
            self.realTime = None
            self.trackNum = trackNum
            
        def __repr__(self):
            return "(%d) PcEvent %d\n" % (self.trackNum, self.id) + \
                   "deltaTime: %s\n" % self.deltaTime + \
                   "cum delta time: %d\n" % self.cumulativeDeltaTime + \
                   "eventType: %s\n" % self.eventType + \
                   "new prog number: %s\n" % self.newProgNum + \
                   "runningMode: %s\n\n" % self.runningMode 
                   
        def __cmp__(self, other):
            if hasattr(other, 'cumulativeDeltaTime'):
                return (self.cumulativeDeltaTime).__cmp__(other.cumulativeDeltaTime)
             
        def collapse(self):
            collapsed = self.deltaTime
            if self.runningMode == False:
                collapsed = ''.join([collapsed, self.eventType])
            collapsed = ''.join([collapsed, self.newProgNum])
            return collapsed
            
            
    class AtEvent(object):
    
        def __init__(self, listLength, d, eventType, channelNum, runningMode, trackNum):
            self.id = listLength
            self.deltaTime = d
            self.type = 'at'
            self.eventType = eventType
            self.channelNum = channelNum
            self.runningMode = runningMode
            self.cumulativeDeltaTime = cumulativeDeltaTime
            self.realTime = None
            self.trackNum = trackNum
            
        def __repr__(self):
            return "(%d) AtEvent %d\n" % (self.trackNum, self.id) + \
                   "deltaTime: %s\n" % self.deltaTime + \
                   "cum delta time: %d\n" % self.cumulativeDeltaTime + \
                   "eventType: %s\n" % self.eventType + \
                   "channel number: %s\n" % self.channelNum + \
                   "runningMode: %s\n\n" % self.runningMode 
                   
        def __cmp__(self, other):
            if hasattr(other, 'cumulativeDeltaTime'):
                return (self.cumulativeDeltaTime).__cmp__(other.cumulativeDeltaTime)
            
        def collapse(self):
            collapsed = self.deltaTime
            if self.runningMode == False:
                collapsed = ''.join([collapsed, self.eventType])
            collapsed = ''.join([collapsed, self.channelNum])
            return collapsed
            
            
    class PwcEvent(object):
    
        def __init__(self, listLength, d, eventType, bottom, top, runningMode, trackNum):
            self.id = listLength
            self.deltaTime = d
            self.type = 'pwc'
            self.eventType = eventType
            self.bottom = bottom
            self.top = top
            self.runningMode = runningMode
            self.cumulativeDeltaTime = cumulativeDeltaTime
            self.realTime = None
            self.trackNum = trackNum
            
        def __repr__(self):
            return "(%d) PwcEvent %d\n" % (self.trackNum, self.id) + \
                   "deltaTime: %s\n" % self.deltaTime + \
                   "cum delta time: %d\n" % self.cumulativeDeltaTime + \
                   "eventType: %s\n" % self.eventType + \
                   "bottom: %s\n" % self.bottom + \
                   "top: %s\n" % self.top + \
                   "runningMode: %s\n\n" % self.runningMode 
                   
        def __cmp__(self, other):
            if hasattr(other, 'cumulativeDeltaTime'):
                return (self.cumulativeDeltaTime).__cmp__(other.cumulativeDeltaTime)
            
            
        def collapse(self):
            collapsed = self.deltaTime
            if self.runningMode == False:
                collapsed = ''.join([collapsed, self.eventType])
            collapsed = ''.join([collapsed, self.bottom + self.top])
            return collapsed         
###############################################################################

        
        
#####################################
#Event object instantiation functions#
#####################################

#These functions create a new object for every midi or meta event found.
#They return the newly created object and advance the counter (i) by the
#correct amount for that object and return it.
#If an event is in running mode, the counter will be advanced by 2 less
#than otherwise.


    def pop_meta_events(i, d, eventType, track, runningMode, trackNum):
        
        dataEnd = 6+2*int(functions.return_range(track,i,4,6), 16)        
        metaEvent = MetaEvent(len(eventsDict[eventType[0]]), d, eventType, 
                                functions.return_range(track,i,2,4),
                                functions.return_range(track,i,4,6), 
                                functions.return_range(track,i,6,dataEnd),
                                trackNum)
           
        i += dataEnd
        return (i, metaEvent)
        
        
    def pop_note_events(i, d, eventType, track, runningMode, trackNum):
        adj = functions.return_adjustment(runningMode)
        #NoteEvent(listLength, d, eventType, noteNumber, velocity, runningMode, trackNum)
        noteEvent = NoteEvent(len(eventsDict[eventType[0]]), d, eventType, 
                                functions.return_range(track,i,(2+adj),(4+adj)),
                                functions.return_range(track,i,(4+adj),(6+adj)),
                                runningMode, trackNum)                       
        i += (6 + adj)
        return (i, noteEvent)
        
        
    def pop_cc_events(i, d, eventType, track, runningMode, trackNum):
    
        adj = functions.return_adjustment(runningMode)
        ccEvent = CcEvent(len(eventsDict[eventType[0]]), d, eventType, 
                            functions.return_range(track,i,(2+adj),(4+adj)),
                            functions.return_range(track,i,(4+adj),(6+adj)),
                            runningMode, trackNum)   
        i += (6 + adj)
        return (i, ccEvent)
        
        
    def pop_pc_events(i, d, eventType, track, runningMode, trackNum):
    
        adj = functions.return_adjustment(runningMode)
        pcEvent = PcEvent(len(eventsDict[eventType[0]]), d, eventType, 
                            functions.return_range(track,i,(2+adj),(4+adj)),
                            runningMode, trackNum)
                                               
        i += (4 + adj)
        return (i, pcEvent)
        
        
    def pop_at_events(i, d, eventType, track, runningMode, trackNum):
        adj = functions.return_adjustment(runningMode)
        atEvent = AtEvent(len(eventsDict[eventType[0]]), d, eventType, 
                            functions.return_range(track,i,(2+adj),(4+adj)),
                            runningMode, trackNum)   
        i += (4 + adj)
        return (i, atEvent)
        
        
    def pop_pwc_events(i, d, eventType, track, runningMode, trackNum):
        adj = functions.return_adjustment(runningMode)
        pwcEvent = PwcEvent(len(eventsDict[eventType[0]]), d, eventType, 
                            functions.return_range(track,i,(2+adj),(4+adj)),
                            functions.return_range(track,i,(4+adj),(6+adj)),
                            runningMode, trackNum)
        i += (6 + adj)        
        return (i, pwcEvent)
###############################################################################        
    
    
    i=0
    
    def event_decider(i, d, track, eventType, eventBuffer, runningMode, trackNum):
        #This if statement decides which function to call based on eventType 
        #which is the byte (two characters) after the delta-time bytes. It also
        #decides if the event is in running mode and if so, sets the 
        #runningMode boolean to True.
     
        if int(eventType, 16) < 128:
            #if eventType is less than 0x80 (128 in base 10) then the status
            #byte of the event must have been omitted, the event is in running
            #mode and takes the value of the status byte of the event before it.
            runningMode = True
            i, d, eventBuffer = event_decider(i, d, track, eventBuffer, 
                                                    eventBuffer, runningMode, trackNum)
            
        elif eventType == 'ff':
            #meta event
            i, event = pop_meta_events(i, d, eventType, track, runningMode, trackNum)
            eventBuffer = pop_eventsDict(event, eventType)
            runningMode = False
            
        elif eventType[0] in ['8','9','a']:
            #note event
            i, event = pop_note_events(i, d, eventType, track, runningMode, trackNum)
            eventBuffer = pop_eventsDict(event, eventType)
            runningMode = False
            
        elif eventType[0] == 'b':
            #control change
            i, event = pop_cc_events(i, d, eventType, track, runningMode, trackNum)
            eventBuffer = pop_eventsDict(event, eventType)
            runningMode = False
                
        elif eventType[0] == 'c':
            #program change
            i, event = pop_pc_events(i, d, eventType, track, runningMode, trackNum)
            eventBuffer = pop_eventsDict(event, eventType)
            runningMode = False
            
        elif eventType[0] == 'd':
            #channel after-touch
            i, event = pop_at_events(i, d, eventType, track, runningMode, trackNum)
            eventBuffer = pop_eventsDict(event, eventType)
            runningMode = False
            
        elif eventType[0] == 'e':
            #pitch wheel change
            i, event = pop_pwc_events(i, d, eventType, track, runningMode, trackNum)
            eventBuffer = pop_eventsDict(event, eventType)
            runningMode = False
            
        elif eventType[0] == 'f' and eventType[1] != 'f':
            #system common events, these should not be found in midi files
            print "fx event found"
                  
        else:
            print "This shouldn't have happened."
                
        return (i, d, eventBuffer)
        
        
    def pop_eventsDict(event, eventType):
    
        eventsDict[eventType[0]].append(event)
        eventsDict['allEvents'].append(event)
        return eventType
        
    eventBuffer = ''
    runningMode = False
    eventsDict['trackNum'] = trackNum
    cumulativeDeltaTime = 0
    while i < functions.check_length(track):
        #takes account of the variable length of the delta time portion.
      
        i, d = functions.get_delta_time(i, track)
        cumulativeDeltaTime += d
        #print "Cumulative Delta Time: ", cumulativeDeltaTime, "Delta Time: "
        eventType = functions.get_event_type(i, track)
        i, d, eventBuffer = event_decider(i, d, track, eventType, eventBuffer, runningMode, trackNum)
        
    return eventsDict
