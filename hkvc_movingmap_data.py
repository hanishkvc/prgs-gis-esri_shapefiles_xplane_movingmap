#!/usr/bin/env python3
#
# MovingMap Data sources
# HanishKVC, 2014
# GPL
#

import random

import socket
import struct
import threading
from hkvc_debug import *

XPLANE_IPPORT=4567

class MMRandom():

	def __init__(self):
		self.planeX = 0
		self.planeY = 0
		self.planeHeading = 0
		self.planeAlt = 0

	def get_position(self):
		self.planeX += random.randint(-8,8)
		self.planeY += random.randint(-4,4)
		return True


class MMXPlane():

	def __init__(self):
		self.planeX = 0
		self.planeY = 0
		self.planeHeading = 0
		self.planeAlt = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(("0.0.0.0", XPLANE_IPPORT))
		self.bRun = True
		self.dataSem = threading.Semaphore(value=0)
		self.thread = threading.Thread(target=self.get_data, daemon=True)
		self.thread.start()

	def process_data_simple(self, data):
		data = data.strip().decode()
		dprint(DBGLVL_MISC, "MMXPlane:Recvd:[{}]".format(data))
		self.planeX += random.randint(-8,8)
		self.planeY += random.randint(-4,4)

	def process_data_xplane(self, data):
		dLen = len(data)
		iOff = 0
		dataHdr = struct.unpack("=4sB",data[iOff:5])
		iOff += 5
		dprint(DBGLVL_MISC, "MMXPlane:RecvdHdr:[{}]".format(dataHdr))
		while(iOff < dLen):
			dataGrp = struct.unpack("=Iffffffff",data[iOff:iOff+36])
			iOff += 36
			(iID,f1,f2,f3,f4,f5,f6,f7,f8) = dataGrp
			dprint(DBGLVL_MISC, "MMXPlane:RecvdGrp:[{}]".format(dataGrp))
			if (iID == 20):
				self.planeY = f1
				self.planeX = f2
				self.planeAlt = f3
			elif (iID == 17):
				self.planeHeading = f4
			else:
				dprint(DBGLVL_CRITICAL, "MMXPlane:WARN: UnKnown Data Fields Group [{}] recieved".format(iID))

	def get_data(self):
		pcktCnt = 0
		dprint(DBGLVL_CRITICAL, "MMXPlane:Starting DataGathering...")
		while (self.bRun):
			data,addr = self.sock.recvfrom(1024)
			pcktCnt += 1
			dLen = len(data)
			self.process_data_xplane(data)
			self.dataSem.release()
		dprint(DBGLVL_CRITICAL, "MMXPlane:Stopping DataGathering...")

	def get_position(self):
		if (self.dataSem.acquire(blocking=False)):
			return True
		else:
			return False

	def stop(self):
		self.bRun = False

