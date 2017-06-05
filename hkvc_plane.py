#!/usr/bin/env python3
#
# Helper to draw a plane using given plotter
# HanishKVC, 2014
# GPL
#
#

PLANE_POS_DUMMY = 0x55AA55AA
PLANE_PATH_FORCESAVEMOD = 8

class Plane():

	def __init__(self, plotter, x=0, y=0):
		self.x = 0
		self.y = 0
		self.heading = 0
		self.path = []
		self.polygonId = None
		self.pltr = plotter
		self.movedToCnt = 0
		# First point of polygon must be 0,0
		#self.polygon = [[0,0],[5,5],[0,10]]
		#self.polygon = [[0,0],[-5,5],[-5,-5]]
		#self.polygon = [[0,0],[-5,-5],[-5,5]]
		#self.polygon = [[0,0],[-5,-5],[5,-5]]
		self.polygon = [[0,0],[-3,-10],[3,-10]]

	def draw_plane(self, x=PLANE_POS_DUMMY, y=PLANE_POS_DUMMY, heading=PLANE_POS_DUMMY):
		if ((x == PLANE_POS_DUMMY) or (y == PLANE_POS_DUMMY)):
			x = self.x
			y = self.y
		if (heading == PLANE_POS_DUMMY):
			heading = self.heading
		points = self.pltr.rotateAndTranslateBy(self.polygon,-1*heading,x,y)
		if (self.polygonId == None):
			self.pltr.color(250, 0, 0)
			self.polygonId = self.pltr.polygon_noscale(points)
		else:
			self.pltr.cnvs.delete(self.polygonId)
			self.pltr.color(250, 0, 0)
			self.polygonId = self.pltr.polygon_noscale(points)

	def draw_path(self):
		self.pltr.color(10, 10, 10)
		[cX, cY] = self.path[0]
		self.pltr.move_to(cX, cY)
		bShouldStroke=False
		for i in range(1,len(self.path)):
			[cX, cY] = self.path[i]
			#print("PlaneDrawPath:{}: {},{}".format(i, cX, cY))
			self.pltr.line_to(cX, cY)
			bShouldStroke=True
		if (bShouldStroke):
			self.pltr.stroke()

	def moved_to(self, x, y, heading=0):
		self.movedToCnt += 1
		cntMod = self.movedToCnt % PLANE_PATH_FORCESAVEMOD
		self.x = x
		self.y = y
		self.heading = heading
		try:
			[prevX, prevY] = self.path[-1]
		except IndexError:
			prevX = PLANE_POS_DUMMY
			prevY = PLANE_POS_DUMMY
		if (((abs(prevX-x) < 0.02) and (abs(prevY-y) < 0.02)) and (cntMod != 0) and (self.movedToCnt != 2)):
			print("PLANE: Skipping Prev path loc")
			self.path[-1] = [x,y]
		else:
			print("PLANE: Saving Prev path loc")
			self.path.append([x,y])

