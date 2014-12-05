#!/usr/bin/env python3
#
# ESRI Map/GIS Shapefile DBF parser and plotter
# HanishKVC, 2014
# GPL
#


import sys
import struct
import turtle


class DbfParser:

	FIELD_OFFSET = 0
	FIELD_TYPE = 1
	FIELD_LEN = 2

	def __init__(self):
		self.dbNumRecs = 0
		self.dbRecStartOffset = 0
		self.dbRecLen = 0
		self.dbRecFields = {}

	def dbf_read_fileheader(self):

		hdrData = self.dbFile.read(32)
		hdr = struct.unpack("<4Bi3h2B3i2Bh",hdrData)
		#print(hdr)
		(dbVer,uYY,uMM,uDD,numRecs,lenHdr,lenRec,hRsvd1,bDirty,bEncrypted,iFreeRecThread,iRsvd2,iRsvd3,bMdx,langDrvr,hRsvd4) = hdr
		if (dbVer != 3):
			print("ERROR: Dont understand the dBase dbf file format version...")
			exit()
		else:
			print("INFO: dBase III w/o memo file, File without DBT")
		print("INFO:FileHeader\n\tnumRecs[{}]\n\tlenHdr[{}]\n\tlenRec[{}]".format(numRecs,lenHdr,lenRec))
		self.dbNumRecs = numRecs
		self.dbRecStartOffset = lenHdr
		self.dbRecLen = lenRec
		iFOffset = 1 # This is to take care of the 1 byte record deleted or not flag at beginning of each record
		while True:
			fdHdrData = self.dbFile.read(32)
			if (fdHdrData[0] == 0x0d):
				break
			fdHdr = struct.unpack("<11sciBB14x",fdHdrData)
			#print(fdHdr)
			(sFieldName, cFieldType,iFieldDataAddr,bFieldLength,bNumOfDeciPlaces) = fdHdr
			sFieldName = sFieldName.decode().strip()
			sFieldName = sFieldName.split('\x00')[0]
			self.dbRecFields[sFieldName] = (iFOffset, cFieldType, bFieldLength)
			iFOffset = iFOffset + bFieldLength
			#print("INFO:FieldDescriptor\n\tsFieldName[{}]\n\tcFiledType[{}]\n\tbFieldLength[{}]".format(sFieldName,cFieldType,bFieldLength))
		fsizeCalc = lenHdr+numRecs*lenRec
		fsize = self.dbFile.seek(0,2)
		if (fsizeCalc == fsize):
			print("INFO: FileSize [{}] checks out wrt Header".format(fsize))
		else:
			print("ERROR: FileSize [{}] DOESNOT checks out wrt Header [{}]".format(fsize,fsizeCalc))
		self.dbFile.seek(lenHdr)
		print(self.dbRecFields)

	def dbf_read_record_field_bytes(self,iRecIndex,sFieldName):
		self.dbFile.seek(self.dbRecStartOffset+iRecIndex*self.dbRecLen)
		recData = self.dbFile.read(self.dbRecLen)
		tOffset = self.dbRecFields[sFieldName][self.FIELD_OFFSET]
		tLen = self.dbRecFields[sFieldName][self.FIELD_LEN]
		fieldData = recData[tOffset:(tOffset+tLen)]
		return fieldData

	def dbf_read_record_field_str(self,iRecIndex,sFieldName):
		fieldData = self.dbf_read_record_field_bytes(iRecIndex,sFieldName)
		try:
			fieldData = fieldData.decode('ascii').strip()
		except:
			fieldData = "ERRORERRORERROR"
		return fieldData

	def dbf_check_field_exists(self,sFieldName):
		if (self.dbRecFields.get(sFieldName) == None):
			return False
		return True	

	def dbf_load(self, sFile):
		self.dbFileName = sFile
		self.dbFile=open(sFile,"rb")
		self.dbf_read_fileheader()

	def dbf_close(self):
		self.dbFile.close()
		self.__init__()


if __name__ == "__main__":

	db = DbfParser()
	db.dbf_load(sys.argv[1])

	try:
		print("INFO: Field LONGITUDE:{}".format(db.dbRecFields["LONGITUDE"]))
		print("INFO: Field LATITUDE:{}".format(db.dbRecFields["LATITUDE"]))
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

	for i in range(0,db.dbNumRecs):
		if (bModeQueryField):
			fdByte = db.dbf_read_record_field_bytes(i,sys.argv[2])
			fdStr  = db.dbf_read_record_field_str(i,sys.argv[2])
			print(i,fdByte,fdStr)
		if (bModePlot):
			latY = float(db.dbf_read_record_field_str(i,"LATITUDE"))
			lonX = float(db.dbf_read_record_field_str(i,"LONGITUDE"))
			gTr.goto(lonX*3,latY*3)
			gTr.dot()

	db.dbf_close()

	input("Hope everything was fine...")

