from pyx import *
from decimal import *
import math

#text.set(mode="latex")
#text.preamble(r'\usepackage{lmodern}')

def create_overlay(orderedProjections):

    projections = []
    for proj in reversed(orderedProjections):
        projections.append(proj[1])
    
    canv = canvas.canvas()
    unit.set(uscale=1,vscale=1,wscale=1,xscale=1,defaultunit="cm")
    
    angles = []
    for proj in projections:
        angle = ((Decimal(160000) - proj)/Decimal(160000))*Decimal(360)
        #print angle
        angles.append(float(angle))
    
    radiusCoords = []
    chordCoords = []
    sensorCoords = []
    barLineCoords = []
    barTextCoords = []
    
    discChoice = 4
    
    #Information for setting bar markers.
    
    if discChoice == 1:
        #p1d2
        numOfBars =   [ 2,  5, 1,  8,  1,  8, 1,  8,  1, 1]
        beatsPerBar = [16, 16, 8, 20, 24, 16, 4, 20, 24, 4]
        introBars = 2
        
    elif discChoice == 2:
        #p2d2
        introBars = 4
        numOfBars =   [ 4, 16]
        beatsPerBar = [16, 16]
        
    elif discChoice == 3:
        #p3d1
        introBars = 0
        numOfBars =   [ 8, 15, 1,  4, 1,  5,  4]
        beatsPerBar = [16, 12, 8, 12, 4, 12, 20]
        
    elif discChoice == 4:
        #p3d2
        introBars = 1
        numOfBars =   [ 1, 11, 1,  1, 11, 1, 14, 2]
        beatsPerBar = [12, 12, 4, 16, 12, 4, 16, 8]
    
    b = 0.6
    r = 24.5
    lWidth = 0.11
    c = math.sqrt((r - math.sqrt(r**2 - b**2))**2 + b**2)
    
    #x = 0.35
    x = 0.4
    d = 1.5
    y = 0
    z = 5
    
    alphaR = (math.acos((r**2 - b**2)/(r*math.sqrt(r**2 - b**2))))/2
    centreX = 49.0
    centreY = 49.0
    
    canv.stroke(path.circle(49.0, 49.0, 24.5))
    
    for theta in angles:
        thetaR = math.radians(theta)
        betaR = math.radians(270.0) + thetaR - alphaR
        epsilonR = math.radians(180.0) + thetaR
        
        radiusCoords.append([centreX, centreY, (centreX + r*math.sin(thetaR)), (centreY + r*math.cos(thetaR)), betaR, epsilonR])
            
    for p in radiusCoords:
        
        newPath = path.line(p[0], p[1], p[2], p[3])
        #canv.stroke(newPath, [style.linewidth(0.1), style.linestyle.solid, color.rgb.blue])
        
        chordCoords.append([p[2], p[3], (p[2] + c*math.sin(p[4])), (p[3] + c*math.cos(p[4])), p[4], p[5]])
        
    noteCount = 1
    barCount = 1
    sectionCount = 0
    
    for p in chordCoords:
        
        newPath = path.line(p[0], p[1], p[2], p[3])
        #canv.stroke(newPath, [style.linewidth(0.1), style.linestyle.solid, color.rgb.red])
        
        offsetX = math.sin(p[4])*(lWidth/float(2))
        offsetY = math.cos(p[4])*(lWidth/float(2))
        sensorCoords.append([p[2]-offsetX + d*math.sin(p[5]), p[3]-offsetY + d*math.cos(p[5]), (p[2] + (x+d)*math.sin(p[5]) - offsetX), (p[3] + (x+d)*math.cos(p[5]) - offsetY)])
        
        barLineStartX = y*math.sin(p[5]) - offsetX
        barLineStartY = y*math.cos(p[5]) - offsetY
        barLineStopX = z*math.sin(p[5]) - offsetX
        barLineStopY = z*math.cos(p[5]) - offsetY

        
        if noteCount == 1:
        
            barLineCoords.append([p[2] + barLineStartX, p[3] + barLineStartY, p[2] + barLineStopX, p[3] + barLineStopY])
            
        noteCount += 1
        
        if sectionCount <= (len(beatsPerBar) - 1):
            
            if noteCount == (beatsPerBar[sectionCount] + 1):
                noteCount = 1
                barCount += 1
                
            
            if barCount == (numOfBars[sectionCount] + 1):
                sectionCount += 1
                barCount = 1
        
    for p in sensorCoords:
    
        newPath = path.line(p[0], p[1], p[2], p[3])
        canv.stroke(newPath, [style.linewidth(lWidth), style.linestyle.solid, color.rgb.black])
    
    """    
    barNumCount = -introBars
    for p in barLineCoords:
        newPath = path.line(p[0], p[1], p[2], p[3])
        if barNumCount == 0:
            barNumCount = 1
        txt = "Bar %s" % str(barNumCount)
        textArg = r'\fontsize{20}{20}\selectfont %s' % txt
        canv.stroke(newPath, [deco.curvedtext(textArg, 
                                textattrs=[text.halign.right, text.vshift.mathaxis], 
                                arclenfromend=1, 
                                exclude=0.1), 
                                style.linewidth(0.04), 
                                style.linestyle.solid, 
                                color.rgb.black])
                                
        #canv.draw(newPath, [deco.curvedtext(textArg)])
        barNumCount += 1       
    """
    
    canv.writePDFfile("overlay")
