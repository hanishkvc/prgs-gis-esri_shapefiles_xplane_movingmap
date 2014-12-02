#!/usr/bin/env python3
#
# ESRI Map/GIS Shapefile DBF parser and plotter
# HanishKVC, 2014
# GPL
#


import sys
import struct

gNumRecs = 0
gRecStartOffset = 0
gRecLen = 0
gFieldOffsets = {}
gFieldLens = {}

def dbf_read_fileheader(f):
	global gNumRecs
	global gRecStartOffset, gRecLen
	global gFieldOffsets, gFieldLens

	hdrData = f.read(32)
	hdr = struct.unpack("<4Bi3h2B3i2Bh",hdrData)
	#print(hdr)
	(dbVer,uYY,uMM,uDD,numRecs,lenHdr,lenRec,hRsvd1,bDirty,bEncrypted,iFreeRecThread,iRsvd2,iRsvd3,bMdx,langDrvr,hRsvd4) = hdr
	if (dbVer != 3):
		print("ERROR: Dont understand the dBase dbf file format version...")
		exit()
	else:
		print("INFO: dBase III w/o memo file, File without DBT")
	print("INFO:FileHeader\n\tnumRecs[{}]\n\tlenHdr[{}]\n\tlenRec[{}]".format(numRecs,lenHdr,lenRec))
	gNumRecs = numRecs
	iFOffset = 0
	while True:
		fdHdrData = f.read(32)
		if (fdHdrData[0] == 0x0d):
			break
		fdHdr = struct.unpack("<11sciBB14x",fdHdrData)
		#print(fdHdr)
		(sFieldName, cFieldType,iFieldDataAddr,bFieldLength,bNumOfDeciPlaces) = fdHdr
		sFieldName = sFieldName.decode().strip()
		sFieldName = sFieldName.split('\x00')[0]
		gFieldOffsets[sFieldName] = iFOffset
		gFieldLens[sFieldName] = bFieldLength
		iFOffset = iFOffset + bFieldLength
		print("INFO:FieldDescriptor\n\tsFieldName[{}]\n\tcFiledType[{}]\n\tbFieldLength[{}]".format(sFieldName,cFieldType,bFieldLength))
	gRecStartOffset = lenHdr
	gRecLen = lenRec
	fsizeCalc = lenHdr+numRecs*lenRec
	fsize = f.seek(0,2)
	if (fsizeCalc == fsize):
		print("INFO: FileSize [{}] checks out wrt Header".format(fsize))
	else:
		print("ERROR: FileSize [{}] DOESNOT checks out wrt Header [{}]".format(fsize,fsizeCalc))
	f.seek(lenHdr)
	print(gFieldOffsets)

def dbf_read_record(f,iRecIndex,sFieldName):
	f.seek(gRecStartOffset+iRecIndex*gRecLen)
	recData = f.read(gRecLen)
	tOffset = gFieldOffsets[sFieldName]
	tLen = gFieldLens[sFieldName]
	fieldData = recData[tOffset:(tOffset+tLen)]
	return fieldData

def dbf_read(sFile):
	f=open(sFile,"rb")
	dbf_read_fileheader(f)
	return f
def main():
	f=dbf_read(sys.argv[1])
	for i in range(0,gNumRecs):
		print(dbf_read_record(f,i,sys.argv[2]))
	f.close()


main()

