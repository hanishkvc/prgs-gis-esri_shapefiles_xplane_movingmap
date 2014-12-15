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

XPLANE_IPPORT=4567

class MMRandom():

	def __init__(self):
		self.planeX = 0
		self.planeY = 0

	def get_position(self):
		self.planeX += random.randint(-8,8)
		self.planeY += random.randint(-4,4)
		return True


class MMXPlane():

	def __init__(self):
		self.planeX = 0
		self.planeY = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(("0.0.0.0", XPLANE_IPPORT))
		self.bRun = True
		self.dataSem = threading.Semaphore()
		self.thread = threading.Thread(target=self.get_data, daemon=True)
		self.thread.start()

	def process_data_simple(self, data):
		data = data.strip().decode()
		print("Recvd:[{}]".format(data))
		self.planeX += random.randint(-8,8)
		self.planeY += random.randint(-4,4)

	def process_data_xplane(self, data):
		data = struct.unpack("=4sBIffffffff",data)
		print("Recvd:[{}]".format(data))
		self.planeX += random.randint(-8,8)
		self.planeY += random.randint(-4,4)

	def get_data(self):
		pcktCnt = 0
		print("Starting DataGathering...")
		while (self.bRun):
			data,addr = self.sock.recvfrom(1024)
			pcktCnt += 1
			dLen = len(data)
			data = self.process_data_simple(data)
			self.dataSem.release()
		print("Stopping DataGathering...")

	def get_position(self):
		if (self.dataSem.acquire(blocking=False)):
			return True
		else:
			return False

	def stop(self):
		self.bRun = False

