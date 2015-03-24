#!/usr/bin/python

#A simple python script for implementing merge.pl to merge N .lhe.gz files

file = open("merge.sh", "w")

file.write("#!/usr/bin/bash\n\n")
file.write("./merge.pl")

numFiles = 100

for i in range(0, numFiles):
    pieceFileName = " unweighted_events_"
    if(i < 10):
        pieceFileName += "00"
    elif(i < 100):
        pieceFileName += "0"
    pieceFileName += str(i)
    pieceFileName += ".lhe.gz"
    file.write(pieceFileName)   

file.write(" unweighted_events.lhe.gz banner.txt")
#file.write("\n\nrm unweighted_events_*")            
file.close()         
