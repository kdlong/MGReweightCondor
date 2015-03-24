import re
import sys
# splits the LHE file inputFile into numFiles individual files of the form
# outFileNameBase_XXX.lhe
# For numFiles > 1000, the number of open IO files in python will cause
# the program to exit with an error.
def split(inputFile, outFileNameBase, numFiles):
    fin = ""
    try:
      fin = open(inputFile)
    except:
      print("Error: Input file: %s could not be opened, exiting." % inputFile)
      sys.exit(1)

    eventNum = 0
    init = False
    inFooter = False
    footLines = []
    for line in fin:
      if re.match(r"[^#]*</LesHouchesEvents>",line):
        inFooter = True
        footLines.append(line)
      elif inFooter:
        footLines.append(line)
      elif init:  
        if re.match(r"[^#]*</event>",line):
          eventNum += 1
      elif re.match(r"[^#]*</init>",line):
        init = True

    eventsTotal = eventNum
    print "N Events Total: %i" % eventsTotal

    files = []
    maxEventsFile = []
    for i in range(numFiles):
      splitFileName = outFileNameBase
      if(i < 100):
        splitFileName += "0"
      if(i < 10):
        splitFileName += "0"
      tmp = open(splitFileName+str(i)+".lhe",'w')
      files.append(tmp)
      maxEventsFile.append(eventsTotal/numFiles)
    maxEventsFile[len(maxEventsFile)-1] += eventsTotal % numFiles

    eventNum = 0
    eventNumThisFile = 0
    init = False
    headLines = []
    iFile = 0
    fin.seek(0)
    for line in fin:
      if init:  
        files[iFile].write(line)
        if re.match(r"[^#]*</event>",line):
          eventNum += 1
          eventNumThisFile += 1
          if eventNumThisFile >= maxEventsFile[iFile]:
            files[iFile].writelines(footLines)
            iFile += 1
            eventNumThisFile = 0
            if iFile == numFiles:
              break
            files[iFile].writelines(headLines)
      elif re.match(r"[^#]*</init>",line):
        init = True
        headLines.append(line)
        files[iFile].writelines(headLines)
      else:
        headLines.append(line)

    for f in files:
      f.close()
 
