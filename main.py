import os,sys
import re
import csv
import autoeditorpairs


path = "raw_minpair_stimuli/male/stops/"
gender = "m"

def scanDir(minpairdata):
	files = os.listdir(path) #lists all files
	saveas = ""

	for f in files:
		if ".wav" in f:
			print "\n==[accessing: "+f+"]============="
			matchinfo = match(f, minpairdata)
			saveas = makeString(matchinfo)
			print "found match"
			p0name = os.path.join(path,saveas[0])
			p1name = os.path.join(path,saveas[1])
			if(matchinfo[4] == "OOO"):
				print "caught out of order recording!"
				print "    >swapping: "+saveas[0]+" <--> "+saveas[1]
				print "processing: \n    > "+saveas[1]+" \n    > "+saveas[0]
				autoeditorpairs.process_wave(os.path.join(path, f), p1name, p0name)
			else:
				print "processing: \n    > "+saveas[0]+" \n    > "+saveas[1]
				autoeditorpairs.process_wave(os.path.join(path, f), p0name, p1name)
	print("finished processing folder: "+str(path))
	print "have a good day! :)"


def populateDict():
	minpairdata = []

	with open('minimalpairs.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			minpairdata.append(row)
		return minpairdata

def match(filename, minpairdata):
	m = re.search('\d{1,3}', filename)
	fid = m.group(0)

	for r in minpairdata:
		if r["ID"] == fid:
			return [r["ID"], r["p0"], r["p1"], r["contrast"], r["notes"]]

def makeString(infoList):
	s0 = infoList[0]+"_"+infoList[1]+"_"+infoList[3]+"_"+gender+".wav"
	s1 = infoList[0]+"_"+infoList[2]+"_"+infoList[3]+"_"+gender+".wav"

	return [s0, s1]

def main():
	minpairs = populateDict()
	scanDir(minpairs)

main()
