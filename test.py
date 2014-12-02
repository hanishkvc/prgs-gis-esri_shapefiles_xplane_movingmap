#!/usr/bin/env python3

import struct
import sys
import turtle
import random

DO_COLOR_RANDOM=False

SHAPEFILE_CODE = 9994
SHAPETYPES = { 0: "NullShape", 1: "Point", 3: "PolyLine", 5: "Polygon", 8: "MultiPoint", 11: "PointZ", 13: "PolyLineZ", 15: "PolygonZ", 
		18: "MultiPointZ", 21: "PointM", 23: "PolyLineM", 25: "PolygonM", 28: "MultiPointM", 31: "MultiPatch" }

gFileLength = 0

gTr = None


def plot_adjust_xy(x,y):
	return (x*6, y*6)


def shp_read_fileheader(f):
	global gFileLength

	#7 BigEndian Integers
	#2 LittleEndian Integers
	#8 LittleEndian Double
	hdrDataBE=f.read(28)
	hdrP1=struct.unpack(">7i",hdrDataBE)
	hdrDataLE=f.read(72)
	hdrP2=struct.unpack("<2i8d",hdrDataLE)
	print(hdrP1,hdrP2)

	tFileCode=hdrP1[0]
	if (tFileCode != SHAPEFILE_CODE):
		print("ERROR: Not a ShapeFile, Quiting...")
		exit()
	else:
		print("INFO: This is a ShapeFile, Continuing...")

	tFileLength=hdrP1[6]*2	# Because size is mentioned in 16bit word  units
	gFileLength = tFileLength
	tVersion=hdrP2[0]
	tShapeType=hdrP2[1]
	tShapeTypeStr=SHAPETYPES[tShapeType]
	gXMin = hdrP2[2]
	gYMin = hdrP2[3]
	gXMax = hdrP2[4]
	gYMax = hdrP2[5]
	gZMin = hdrP2[6]
	gZMax = hdrP2[7]
	gMMin = hdrP2[8]
	gMMax = hdrP2[9]

	print("FileCode[{}]\nFileLength[{}]\nVersion[{}]".format(tFileCode, tFileLength, tVersion))
	print("ShapeType used in this ShapeFile is [{}]".format(tShapeTypeStr))
	print("BoundingBox:\n\tXMin[{}],YMin[{}],XMax[{}],YMax[{}]".format(gXMin,gYMin,gXMax,gYMax))
	print("\tZMin[{}],ZMax[{}],MMin[{}],MMax[{}]".format(gZMin,gZMax,gMMin,gMMax))


def shp_read_records(f):
	while True:
		rHdrData = f.read(8)
		(recNum, recContentLength) = struct.unpack(">2i",rHdrData)
		recContentLength = recContentLength*2 # Convert for 16bit word size to 8bit byte size
		print("Processing Record[{}] of size[{}]".format(recNum,recContentLength))
		rContentData = f.read(recContentLength)
		rShapeType = rContentData[0:4]
		rShapeType = int.from_bytes(rShapeType,'little')
		print(SHAPETYPES[rShapeType])
		if (rShapeType == 5):
			shp_read_polygon(rContentData)
		if (rShapeType == 1):
			shp_read_point(rContentData)


def shp_read_point(data):
	pRec = struct.unpack("<i2d",data)
	(pShapeType, pX, pY) = pRec
	cPoint = plot_adjust_xy(pX,pY)
	print("pRec={}, cPointAdjusted={}".format(pRec,cPoint))
	gTr.goto(cPoint[0],cPoint[1])
	gTr.dot()


def shp_read_polygon(data):
	# Each polygon shape record contains multiple polygons whose vertices are stored serially one after the other
	hdrPolygonData = data[0:44]
	hdrPolygon = struct.unpack("<i4d2i",hdrPolygonData)
	(pShapeType, pBBXMin, pBBYMin, pBBXMax, pBBYMax, pNumParts, pNumPoints) = hdrPolygon
	print(hdrPolygon)

	polyStartPointIndexesArrayStart = 44
	polyStartPointIndexesArrayEnd = polyStartPointIndexesArrayStart + 4*pNumParts
	polyStartPointIndexesArrayData = data[polyStartPointIndexesArrayStart:polyStartPointIndexesArrayEnd]
	# This array contains indexes to the polyPointsArray, which specifies the 1st point of the given/current polygon
	# The 1st point of the next polygon automatically means that the corresponding previous point is the end of the current polygon
	polyStartPointIndexesArray = struct.unpack("<{}i".format(pNumParts), polyStartPointIndexesArrayData) 

	polyPointsArrayStart = polyStartPointIndexesArrayEnd
	polyPointsArrayEnd = polyPointsArrayStart + (8*2)*pNumPoints
	if (polyPointsArrayEnd != len(data)):
		print("DEBUG: Something wrong with Polygon Shape record parsing, Quiting...")
		exit()
	polyPointsArrayData = data[polyPointsArrayStart:polyPointsArrayEnd]

	#NOTE: FIXED: This is a simple temp logic which ignores about multiple Polygons within a single Polygon shape record content
	cPoly = 0
	(cPointStart, cPointEnd) = shp_poly_startend(polyStartPointIndexesArray, cPoly, pNumParts, pNumPoints)
	for i in range(0,pNumPoints):
		cPoint = struct.unpack_from("<2d", polyPointsArrayData, i*16)
		print(cPoint)
		#gTr.goto(cPoint)
		cPoint = plot_adjust_xy(cPoint[0],cPoint[1])
		gTr.goto(cPoint[0],cPoint[1])
		if (i == cPointStart):
			if (DO_COLOR_RANDOM):
				gTr.color((random.randint(0,255),random.randint(0,255),random.randint(0,255)),(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
				gTr.begin_fill()
			gTr.pendown()
		if (i == cPointEnd):
			gTr.penup()
			if (DO_COLOR_RANDOM):
				gTr.end_fill()
			cPoly = cPoly+1
			(cPointStart, cPointEnd) = shp_poly_startend(polyStartPointIndexesArray, cPoly, pNumParts, pNumPoints)



def shp_poly_startend(polyStartPointIndexesArray, curPoly, numPolys, numPoints):
	if (curPoly == numPolys):
		cPointStart = -1
		cPointEnd = -1
	else:
		cPointStart = polyStartPointIndexesArray[curPoly]
		if ((curPoly+1) == numPolys):
			cPointEnd = numPoints-1
		else:
			cPointEnd = polyStartPointIndexesArray[curPoly+1]-1
	return (cPointStart, cPointEnd)


def shp_test():
	for i in range(1,len(sys.argv)):
		gTr.penup()
		f=open(sys.argv[i]+".shp","rb")
		shp_read_fileheader(f)
		try:
			shp_read_records(f)
		except:
			print(sys.exc_info())
			if (gFileLength == f.tell()):
				print("INFO: Seems like End of File![{}]".format(f.tell()))
			else:
				print("WARN: Unexpected FileLocation?[{}]".format(f.tell()))

		f.close()
		#input("INFO: Shapefile[{}] processed...".format(sys.argv[i]))
	

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
	for i in range(1,len(sys.argv)):
		f=dbf_read(sys.argv[i]+".dbf")
		try:
			print(gFields["LONGITUDE"])
			print(gFields["LATITUDE"])
			bCanPlot = True
		except:
			bCanPlot = False

		gTr.penup()
		for i in range(0,gNumRecs):
			if (bCanPlot):
				latY = float(dbf_read_record_field_str(f,i,"LATITUDE"))
				lonX = float(dbf_read_record_field_str(f,i,"LONGITUDE"))
				name = dbf_read_record_field_str(f,i,"NAME")
				scalerank = dbf_read_record_field_str(f,i,"SCALERANK")
				print(lonX,latY)
				(lonX,latY) = plot_adjust_xy(lonX,latY)
				gTr.goto(lonX,latY)
				gTr.dot()
				if (scalerank == "0") or (scalerank == "1"):
					gTr.write(name)

		f.close()

gTr = turtle
gTr.speed(0)
gTr.hideturtle()
gTr.colormode(255)
shp_test()
input("Hope everything was fine...")
gTr.color((200,0,0),(100,50,200))
dbf_test()
input("Hope everything was fine...")

