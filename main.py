import os,sys
import re
import csv
import autoeditorpairs


path = "raw_minpair_stimuli/male/fricatives"
gender = "f"

def scanDir(minpairdata):
	files = os.listdir(path) #lists all files
	saveas = ""

	for f in files:
		if ".wav" in f:
			print "accessing: "+f
			matchinfo = match(f, minpairdata)
			saveas = makeString(matchinfo)
			print "found match"
			print "processing: \n    > "+saveas[0]+" \n    > "+saveas[1]
			autoeditorpairs.process_wave(os.path.join(path, f), saveas[0], saveas[1])
	print("finished processing folder: ",path)
	print "have a good day! :)"


def populateDict():
	minpairdata = []

	with open('minimalpairs.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			minpairdata.append(row)
		return minpairdata

def match(filename, minpairdata):
	m = re.search('\d{1,2}', filename)
	fid = m.group(0)

	for r in minpairdata:
		if r["ID"] == fid:
			return [r["ID"], r["p0"], r["p1"], r["Contrast"]]

def makeString(infoList):
	s0 = infoList[0]+"_"+infoList[1]+"_"+infoList[3]+"_"+gender+".wav"
	s1 = infoList[0]+"_"+infoList[2]+"_"+infoList[3]+"_"+gender+".wav"

	return [s0, s1]

def main():
	minpairs = populateDict()
	scanDir(minpairs)

main()
