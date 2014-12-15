#!/usr/bin/env python3
#
# MovingMap Data sources
# HanishKVC, 2014
# GPL
#

import random

class MMRandom():

	def __init__(self):
		self.planeX = 0
		self.planeY = 0

	def get_position(self):
		self.planeX += random.randint(-8,8)
		self.planeY += random.randint(-4,4)
		return True

