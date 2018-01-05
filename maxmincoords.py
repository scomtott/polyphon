from sys import argv

script, inputFile = argv

with open(inputFile, 'r') as inputFile:
    lines = inputFile.readlines()
    maxCoord = 0
    maxProj = 'init'
    minCoord = 160001
    minProj = 'init'
    for line in lines:
        l = line.strip()
        if l == "te":
            continue
        else:
            a = l
            b = a.split("-")
            c = int(b[1])
            if c > maxCoord:
                maxCoord = c
                maxProj = l
            if c < minProj:
                minCoord = c
                minProj = l
                
    print maxProj, minProj
            
