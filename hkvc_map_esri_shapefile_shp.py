#!/usr/bin/env python3
#
# ESRI Map/GIS Shapefile SHP parser and plotter
# HanishKVC, 2014
# GPL
#

import struct
import sys
import random
import hkvc_plotter
import hkvc_map_esri_shapefile_dbf

DO_COLOR_RANDOM=True

SHAPEFILE_CODE = 9994
SHAPETYPES = { 0: "NullShape", 1: "Point", 3: "PolyLine", 5: "Polygon", 8: "MultiPoint", 11: "PointZ", 13: "PolyLineZ", 15: "PolygonZ", 
		18: "MultiPointZ", 21: "PointM", 23: "PolyLineM", 25: "PolygonM", 28: "MultiPointM", 31: "MultiPatch" }

gFileLength = 0

gTr = None
gDbf = None

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
	recIndex = 0
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
			shp_read_polygon(recIndex, rContentData)
		if (rShapeType == 1):
			shp_read_point(recIndex, rContentData)
		recIndex += 1


def shp_read_point(recIndex, data):
	pRec = struct.unpack("<i2d",data)
	(pShapeType, pX, pY) = pRec
	cPoint = (pX, pY)
	print("pRec={}, cPointAdjusted={}".format(pRec,cPoint))
	gTr.dot(cPoint[0],cPoint[1])
	txt=gDbf.dbf_read_record_field_str(recIndex,"NAME")
	gTr.text(pX, pY, txt)


def shp_read_polygon(recIndex, data):
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
		#print(cPoint)
		if (i == cPointStart):
			clrR = random.randint(0,255)
			clrG = random.randint(0,255)
			clrB = random.randint(0,255)
			print(clrR,clrG,clrB)
			if (DO_COLOR_RANDOM):
				gTr.color(clrR,clrG,clrB)
			gTr.move_to(cPoint[0],cPoint[1])
		elif (i == cPointEnd):
			gTr.line_to(cPoint[0],cPoint[1])
			if (DO_COLOR_RANDOM):
				gTr.fill()
			else:
				gTr.stroke()
			cPoly = cPoly+1
			(cPointStart, cPointEnd) = shp_poly_startend(polyStartPointIndexesArray, cPoly, pNumParts, pNumPoints)
		else:
			gTr.line_to(cPoint[0],cPoint[1])


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


def main():
	global gTr
	global gDbf
	if (sys.argv[1] == "turtle"):
		#gTr = hkvc_plotter.PlotterTurtle("/tmp/t100.dummy",360,180,3,3)
		gTr = hkvc_plotter.PlotterTurtle("/tmp/t100.dummy",(-180,90,180,-90),plotArea=(-540,270,540,-270))
	elif (sys.argv[1] == "tk"):
		#gTr = hkvc_plotter.PlotterTk("/tmp/t100.dummy",360,180,3,3)
		gTr = hkvc_plotter.PlotterTk("/tmp/t100.dummy",(-180,90,180,-90),plotArea=(0,0,1080,540))
	else:
		#gTr = hkvc_plotter.PlotterCairo("/tmp/t100.svg",360,180,20,20)
		gTr = hkvc_plotter.PlotterCairo("/tmp/t100.svg",(-180,90,180,-90),plotArea=(0,0,360*10,180*10))
	#gTr.textfont("Courier 10 Pitch", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD,20)
	gDbf = hkvc_map_esri_shapefile_dbf.DbfParser()

	for i in range(2,len(sys.argv)):
		f=open(sys.argv[i]+".shp","rb")
		shp_read_fileheader(f)
		gDbf.dbf_load(sys.argv[i]+".dbf")
		try:
			shp_read_records(f)
		except:
			print(sys.exc_info())
			if (gFileLength == f.tell()):
				print("INFO: Seems like End of File![{}]".format(f.tell()))
			else:
				print("WARN: Unexpected FileLocation?[{}]".format(f.tell()))
				input("CHECK: Hope above is fine...")

		f.close()
		gDbf.dbf_close()
		#input("INFO: Shapefile[{}] processed...".format(sys.argv[i]))
	gTr.flush()

main()
input("Hope the shapefile was plotted well...")

