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

DO_FILL=True
DO_COLOR_RANDOM=False
DO_COLOR_EARTH=True

PLOT_POINT_ALWAYS=False

SHAPEFILE_CODE = 9994
SHAPETYPES = { 0: "NullShape", 1: "Point", 3: "PolyLine", 5: "Polygon", 8: "MultiPoint", 11: "PointZ", 13: "PolyLineZ", 15: "PolygonZ", 
		18: "MultiPointZ", 21: "PointM", 23: "PolyLineM", 25: "PolygonM", 28: "MultiPointM", 31: "MultiPatch" }

class SHPHandler:

	def __init__(self, plotter):
		self.plotter = plotter
		self.dbfParser = hkvc_map_esri_shapefile_dbf.DbfParser()
		self.plotTextScaleRank = 0

	def setup(self,fileBaseName):
		self.shpFileName = fileBaseName
		self.shpFile=open(fileBaseName+".shp","rb")
		self.shp_read_fileheader()
		self.dbfParser.dbf_load(fileBaseName+".dbf")

	def cleanup(self):
		self.shpFile.close()
		self.dbfParser.dbf_close()

	def shp_read_fileheader(self):

		#7 BigEndian Integers
		#2 LittleEndian Integers
		#8 LittleEndian Double
		hdrDataBE=self.shpFile.read(28)
		hdrP1=struct.unpack(">7i",hdrDataBE)
		hdrDataLE=self.shpFile.read(72)
		hdrP2=struct.unpack("<2i8d",hdrDataLE)
		print(hdrP1,hdrP2)

		tFileCode=hdrP1[0]
		if (tFileCode != SHAPEFILE_CODE):
			print("ERROR: Not a ShapeFile, Quiting...")
			exit()
		else:
			print("INFO: [{}] is a ShapeFile, Continuing...".format(self.shpFileName))

		tFileLength=hdrP1[6]*2	# Because size is mentioned in 16bit word  units
		self.fileLength = tFileLength
		tVersion=hdrP2[0]
		tShapeType=hdrP2[1]
		tShapeTypeStr=SHAPETYPES[tShapeType]
		self.fileBB = {}
		self.fileBB['XMin'] = hdrP2[2]
		self.fileBB['YMin'] = hdrP2[3]
		self.fileBB['XMax'] = hdrP2[4]
		self.fileBB['YMax'] = hdrP2[5]
		self.fileBB['ZMin'] = hdrP2[6]
		self.fileBB['ZMax'] = hdrP2[7]
		self.fileBB['MMin'] = hdrP2[8]
		self.fileBB['MMax'] = hdrP2[9]

		print("FileCode[{}]\nFileLength[{}]\nVersion[{}]".format(tFileCode, tFileLength, tVersion))
		print("ShapeType used in this ShapeFile is [{}]".format(tShapeTypeStr))
		print("BoundingBox:[{}]".format(self.fileBB))


	def shp_read_records(self):
		recIndex = 0
		self.droppedPolygonCnt = 0
		self.droppedPointCnt = 0
		self.droppedPolylineCnt = 0
		while True:
			rHdrData = self.shpFile.read(8)
			if (len(rHdrData) == 0):
				if (self.fileLength != self.shpFile.tell()):
					print("WARN: fileLength[{}] != filePosition[{}]".format(self.fileLength, self.shpFile.tell()))
				print("INFO: LastRecNum [{}], TotalRecCnt [{}]".format(recNum, recIndex))
				break
			(recNum, recContentLength) = struct.unpack(">2i",rHdrData)
			recContentLength = recContentLength*2 # Convert for 16bit word size to 8bit byte size
			#print("Processing Record[{}] of size[{}]".format(recNum,recContentLength))
			rContentData = self.shpFile.read(recContentLength)
			rShapeType = rContentData[0:4]
			rShapeType = int.from_bytes(rShapeType,'little')
			#print(SHAPETYPES[rShapeType])
			if (rShapeType == 5):
				self.shp_read_polygon(recIndex, rContentData)
			elif (rShapeType == 1):
				self.shp_read_point(recIndex, rContentData)
			elif (rShapeType == 3):
				self.shp_read_polyline(recIndex, rContentData)
			else:
				print("DEBUG:Unhandled ShapeType[{}]".format(rShapeType))
			recIndex += 1
		print("INFO: droppedPolygonCnt [{}], droppedPointCnt [{}]".format(self.droppedPolygonCnt, self.droppedPointCnt))


	def shp_read_point(self, recIndex, data):
		pRec = struct.unpack("<i2d",data)
		(pShapeType, pX, pY) = pRec
		cPoint = (pX, pY)
		#print("pRec={}, cPointAdjusted={}".format(pRec,cPoint))
		if (PLOT_POINT_ALWAYS):
			self.plotter.dot(cPoint[0],cPoint[1])
		txt=self.dbfParser.dbf_read_record_field_str(recIndex,"NAME")
		scaleRank=int(self.dbfParser.dbf_read_record_field_str(recIndex,"SCALERANK"))
		if (self.plotTextScaleRank >= scaleRank):
			self.plotter.dot(cPoint[0],cPoint[1])
			if (DO_COLOR_EARTH):
				self.plotter.color(40,40,40)
			self.plotter.text(pX, pY, txt)
		else:
			self.droppedPointCnt += 1

	def do_color(self):
		if (DO_COLOR_EARTH):
			clrR = 200+random.randint(0,55)
			clrG = 200+random.randint(0,55)
			clrB = 40+random.randint(0,55)
			self.plotter.color(clrR,clrG,clrB)
		if (DO_COLOR_RANDOM):
			clrR = random.randint(0,255)
			clrG = random.randint(0,255)
			clrB = random.randint(0,255)
			if (((clrB-clrG) > 150) and ((clrB-clrR) > 150)):
				clrB = random.randint(0,128)
			self.plotter.color(clrR,clrG,clrB)
		#print(clrR,clrG,clrB)


	def shp_read_polygon(self, recIndex, data):
		# Each polygon shape record contains multiple polygons whose vertices are stored serially one after the other
		hdrPolygonData = data[0:44]
		hdrPolygon = struct.unpack("<i4d2i",hdrPolygonData)
		(pShapeType, pBBXMin, pBBYMin, pBBXMax, pBBYMax, pNumParts, pNumPoints) = hdrPolygon
		#print(hdrPolygon)

		if (not self.plotter.oneINanother_r2lt2b((pBBXMin, pBBYMin, pBBXMax, pBBYMax), self.plotter.dataArea)):
			print("Dropping polygon[{}] outside dataArea[{}]".format(hdrPolygon, self.plotter.dataArea))
			self.droppedPolygonCnt += 1
			return

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
		(cPointStart, cPointEnd) = self.shp_poly_startend(polyStartPointIndexesArray, cPoly, pNumParts, pNumPoints)
		for i in range(0,pNumPoints):
			cPoint = struct.unpack_from("<2d", polyPointsArrayData, i*16)
			#print(cPoint)
			if (i == cPointStart):
				self.do_color()
				self.plotter.move_to(cPoint[0],cPoint[1])
			elif (i == cPointEnd):
				self.plotter.line_to(cPoint[0],cPoint[1])
				if (DO_FILL):
					self.plotter.fill()
				else:
					self.plotter.stroke()
				cPoly = cPoly+1
				(cPointStart, cPointEnd) = self.shp_poly_startend(polyStartPointIndexesArray, cPoly, pNumParts, pNumPoints)
			else:
				self.plotter.line_to(cPoint[0],cPoint[1])


	def shp_read_polyline(self, recIndex, data):
		# Each polyline shape record contains multiple polylines whose vertices are stored serially one after the other
		hdrPolylineData = data[0:44]
		hdrPolyline = struct.unpack("<i4d2i",hdrPolylineData)
		(pShapeType, pBBXMin, pBBYMin, pBBXMax, pBBYMax, pNumParts, pNumPoints) = hdrPolyline
		#print(hdrPolyline)

		if (not self.plotter.oneINanother_r2lt2b((pBBXMin, pBBYMin, pBBXMax, pBBYMax), self.plotter.dataArea)):
			print("Dropping polyline[{}] outside dataArea[{}]".format(hdrPolyline, self.plotter.dataArea))
			self.droppedPolylineCnt += 1
			return

		polylineStartPointIndexesArrayStart = 44
		polylineStartPointIndexesArrayEnd = polylineStartPointIndexesArrayStart + 4*pNumParts
		polylineStartPointIndexesArrayData = data[polylineStartPointIndexesArrayStart:polylineStartPointIndexesArrayEnd]
		# This array contains indexes to the polylinePointsArray, which specifies the 1st point of the given/current polyline
		# The 1st point of the next polyline automatically means that the corresponding previous point is the end of the current polyline
		polylineStartPointIndexesArray = struct.unpack("<{}i".format(pNumParts), polylineStartPointIndexesArrayData)

		polylinePointsArrayStart = polylineStartPointIndexesArrayEnd
		polylinePointsArrayEnd = polylinePointsArrayStart + (8*2)*pNumPoints
		if (polylinePointsArrayEnd != len(data)):
			print("DEBUG: Something wrong with Polyline Shape record parsing, Quiting...")
			exit()
		polylinePointsArrayData = data[polylinePointsArrayStart:polylinePointsArrayEnd]

		#NOTE: FIXED: This is a simple temp logic which ignores about multiple Polylines within a single Polyline shape record content
		cPolyline = 0
		(cPointStart, cPointEnd) = self.shp_poly_startend(polylineStartPointIndexesArray, cPolyline, pNumParts, pNumPoints)
		for i in range(0,pNumPoints):
			cPoint = struct.unpack_from("<2d", polylinePointsArrayData, i*16)
			#print(cPoint)
			if (i == cPointStart):
				self.plotter.color(0,0,0)
				self.plotter.move_to(cPoint[0],cPoint[1])
			elif (i == cPointEnd):
				self.plotter.line_to(cPoint[0],cPoint[1])
				self.plotter.stroke()
				cPolyline = cPolyline+1
				(cPointStart, cPointEnd) = self.shp_poly_startend(polylineStartPointIndexesArray, cPolyline, pNumParts, pNumPoints)
			else:
				self.plotter.line_to(cPoint[0],cPoint[1])


	def shp_poly_startend(self, polyStartPointIndexesArray, curPoly, numPolys, numPoints):
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

if __name__ == "__main__":
	
	if (sys.argv[1] == "turtle"):
		#pltr = hkvc_plotter.PlotterTurtle("/tmp/t100.dummy",360,180,3,3)
		pltr = hkvc_plotter.PlotterTurtle("/tmp/t100.dummy",(-180,90,180,-90),plotArea=(-540,270,540,-270))
	elif (sys.argv[1] == "tk"):
		#pltr = hkvc_plotter.PlotterTk("/tmp/t100.dummy",360,180,3,3)
		pltr = hkvc_plotter.PlotterTk(None,(-180,90,180,-90),plotArea=(0,0,1080,540))
	else:
		#pltr = hkvc_plotter.PlotterCairo("/tmp/t100.svg",360,180,20,20)
		pltr = hkvc_plotter.PlotterCairo("/tmp/t100.svg",(-180,90,180,-90),plotArea=(0,0,360*10,180*10))
	#pltr.textfont("Courier 10 Pitch", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD,20)

	shpHandler = SHPHandler(pltr)

	for i in range(2,len(sys.argv)):
		shpHandler.setup(sys.argv[i])
		try:
			shpHandler.shp_read_records()
		except:
			print(sys.exc_info())
			if (shpHandler.fileLength == shpHandler.shpFile.tell()):
				print("INFO: Seems like End of File![{}]".format(shpHandler.shpFile.tell()))
			else:
				print("WARN: Unexpected FileLocation?[{}]".format(shpHandler.shpFile.tell()))
				input("CHECK: Hope above is fine...")

		shpHandler.cleanup()
		#input("INFO: Shapefile[{}] processed...".format(sys.argv[i]))
	shpHandler.plotter.flush()

	input("Hope the shapefile was plotted well...")

