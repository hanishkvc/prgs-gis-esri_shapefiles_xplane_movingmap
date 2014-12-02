#!/usr/bin/env python3
#
# ESRI Map/GIS Shapefile DBF parser and plotter
# HanishKVC, 2014
# GPL
#


import sys
import struct
import turtle

gNumRecs = 0
gRecStartOffset = 0
gRecLen = 0
FIELD_OFFSET = 0
FIELD_TYPE = 1
FIELD_LEN = 2
gFields = {}

def dbf_read_fileheader(f):
	global gNumRecs
	global gRecStartOffset, gRecLen
	global gFields

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
	iFOffset = 1 # This is to take care of the 1 byte record deleted or not flag at beginning of each record
	while True:
		fdHdrData = f.read(32)
		if (fdHdrData[0] == 0x0d):
			break
		fdHdr = struct.unpack("<11sciBB14x",fdHdrData)
		#print(fdHdr)
		(sFieldName, cFieldType,iFieldDataAddr,bFieldLength,bNumOfDeciPlaces) = fdHdr
		sFieldName = sFieldName.decode().strip()
		sFieldName = sFieldName.split('\x00')[0]
		gFields[sFieldName] = (iFOffset, cFieldType, bFieldLength)
		iFOffset = iFOffset + bFieldLength
		#print("INFO:FieldDescriptor\n\tsFieldName[{}]\n\tcFiledType[{}]\n\tbFieldLength[{}]".format(sFieldName,cFieldType,bFieldLength))
	gRecStartOffset = lenHdr
	gRecLen = lenRec
	fsizeCalc = lenHdr+numRecs*lenRec
	fsize = f.seek(0,2)
	if (fsizeCalc == fsize):
		print("INFO: FileSize [{}] checks out wrt Header".format(fsize))
	else:
		print("ERROR: FileSize [{}] DOESNOT checks out wrt Header [{}]".format(fsize,fsizeCalc))
	f.seek(lenHdr)
	print(gFields)

def dbf_read_record_field_bytes(f,iRecIndex,sFieldName):
	f.seek(gRecStartOffset+iRecIndex*gRecLen)
	recData = f.read(gRecLen)
	tOffset = gFields[sFieldName][FIELD_OFFSET]
	tLen = gFields[sFieldName][FIELD_LEN]
	fieldData = recData[tOffset:(tOffset+tLen)]
	return fieldData

def dbf_read_record_field_str(f,iRecIndex,sFieldName):
	fieldData = dbf_read_record_field_bytes(f,iRecIndex,sFieldName)
	try:
		fieldData = fieldData.decode('ascii').strip()
	except:
		fieldData = "ERRORERRORERROR"
	return fieldData


def dbf_read(sFile):
	f=open(sFile,"rb")
	dbf_read_fileheader(f)
	return f

def dbf_test():
	f=dbf_read(sys.argv[1])
	try:
		print(gFields["LONGITUDE"])
		print(gFields["LATITUDE"])
		bCanPlot = True
	except:
		bCanPlot = False

	bModeQueryField = False
	bModePlot = False
	if (len(sys.argv) == 3):
		bModeQueryField = True
	else:
		if (bCanPlot):
			bModePlot = True

	if (bModePlot):
		gTr = turtle
		gTr.penup()

	for i in range(0,gNumRecs):
		if (bModeQueryField):
			fdByte = dbf_read_record_field_bytes(f,i,sys.argv[2])
			fdStr  = dbf_read_record_field_str(f,i,sys.argv[2])
			print(i,fdByte,fdStr)
		if (bModePlot):
			latY = float(dbf_read_record_field_str(f,i,"LATITUDE"))
			lonX = float(dbf_read_record_field_str(f,i,"LONGITUDE"))
			gTr.goto(lonX*3,latY*3)
			gTr.dot()

	f.close()

dbf_test()
input("Hope everything was fine...")

