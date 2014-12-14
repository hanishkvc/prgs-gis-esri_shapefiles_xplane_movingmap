#!/usr/bin/env python3
#
#
#

PLANE_POS_DUMMY = 0x55AA55AA

class Plane():

	def __init__(self, plotter, x=0, y=0):
		self.x = 0
		self.y = 0
		self.path = []
		self.polygonId = None
		self.pltr = plotter

	def draw_plane(self, x=PLANE_POS_DUMMY, y=PLANE_POS_DUMMY):
		if ((x == PLANE_POS_DUMMY) or (y == PLANE_POS_DUMMY)):
			x = self.x
			y = self.y
		points = list()
		points.append([x,y])
		points.append([x+5,y+5])
		points.append([x,y+10])
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
			print("PlaneDrawPath:{}: {},{}".format(i, cX, cY))
			self.pltr.line_to(cX, cY)
			bShouldStroke=True
		if (bShouldStroke):
			self.pltr.stroke()

	def moved_to(self, x, y):
		self.x = x
		self.y = y
		self.path.append([x,y])

