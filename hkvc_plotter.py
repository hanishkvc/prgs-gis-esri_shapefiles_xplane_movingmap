#!/usr/bin/env python3
#
# A Plotter library - which supports Turtle as well as Cairo based graphics
# HanishKVC, 2014
# GPL
#
# It follows the Cairo based syntax and semantics to a great extent
# Except for colors, where it follows the 0-255 range instead of 0-1 range
#
#

import cairo
import turtle
import tkinter
import math

#
# These PlotterClasses are setup such that by default
# * 0,0 (origin) is at the center of the image/plot area specified with
#   the width and height arguments (after scaling is applied)
# * Positive X is towards Right
#   Positive Y is towards Top
#

SCALE_DEFAULT = (0x5A5A, 0x5A5A)
PLOTAREA_DEFAULT = (-1, -1, -1, -1)
PLOTAREA_TYPE_TOPLEFT = 0
PLOTAREA_TYPE_CENTER = 1

class PlotterGeneric:

	def __init__(self, dataArea, scale=SCALE_DEFAULT, plotArea=PLOTAREA_DEFAULT, plotAreaType=PLOTAREA_TYPE_TOPLEFT):
		self.setup_data2plot(dataArea, scale, plotArea, plotAreaType)

	def setup_data2plot(self, dataArea, scale=SCALE_DEFAULT, plotArea=PLOTAREA_DEFAULT, plotAreaType=PLOTAREA_TYPE_TOPLEFT):
		self.dataArea = dataArea
		(dX1, dY1, dX2, dY2) = dataArea
		self.dXRange = dX2-dX1
		self.dYRange = dY2-dY1
		self.dXMid = dX1+self.dXRange/2
		self.dYMid = dY1+self.dYRange/2

		(scaleX, scaleY) = scale
		(pX1, pY1, pX2, pY2) = plotArea
		self.plotAreaType = plotAreaType

		bUpdatePlotArea = False
		if ((scaleX != 0x5A5A) and (scaleY != 0x5A5A)):
			#pX1 = dX1*scaleX
			#pY1 = dY1*scaleY
			#pX2 = dX2*scaleX
			#pY2 = dY2*scaleY
			bUpdatePlotArea = True
			print("INFO:plotArea: Scaling to [{}] of dataArea".format(scale))
		elif (plotArea == PLOTAREA_DEFAULT):
			#(pX1, pY1, pX2, pY2) = dataArea
			bUpdatePlotArea = True
			scaleX = 1
			scaleY = 1
			print("INFO:plotArea: Mapping 1:1 to dataArea")

		if (bUpdatePlotArea):
			if (plotAreaType == PLOTAREA_TYPE_TOPLEFT):
				pX1 = 0
				pY1 = 0
				pX2 = abs(self.dXRange)*scaleX
				pY2 = abs(self.dYRange)*scaleY
				print("INFO:plotArea: TopLeft")
			elif (plotAreaType == PLOTAREA_TYPE_CENTER):
				pX1 = (-1*abs(self.dXRange)/2)*scaleX
				pY1 = (abs(self.dYRange)/2)*scaleY
				pX2 = abs(pX1)
				pY2 = -1*pY1
				print("INFO:plotArea: Center")

		plotArea = (pX1, pY1, pX2, pY2)
		self.plotArea = plotArea
		print("dataArea:[{}]\nplotArea:[{}]\n".format(dataArea, plotArea))

		self.pXRange = pX2-pX1
		self.pYRange = pY2-pY1
		self.width = int(abs(self.pXRange))
		self.height = int(abs(self.pYRange))
		self.pXMid = pX1+self.pXRange/2
		self.pYMid = pY1+self.pYRange/2
		self.xP2DRatio = self.pXRange/self.dXRange
		self.yP2DRatio = self.pYRange/self.dYRange
		#return pXMid, pYMid, dXMid, dYMid, xP2DRatio, yP2DRatio

	def dataXY2plotXY(self, dX, dY):
		#pX = dX*xP2DRatio+(pXMid-dXMid)
		pX = self.pXMid+(dX-self.dXMid)*self.xP2DRatio
		pY = self.pYMid+(dY-self.dYMid)*self.yP2DRatio
		#print("D2P:[{},{}]=[{},{}]".format(dX,dY,pX,pY))
		return pX,pY

	def plotXY2dataXY(self, pX, pY):
		dX = self.dXMid+(pX-self.pXMid)*(1.0/self.xP2DRatio)
		dY = self.dYMid+(pY-self.pYMid)*(1.0/self.yP2DRatio)
		print("P2D:[{},{}]=[{},{}]".format(pX,pY,dX,dY))
		return dX,dY

	def oneINanother_r2lt2b(self, rect1, rect2, bCheckBothWays=True):
		(r1X1, r1Y1, r1X2, r1Y2) = rect1
		(r2X1, r2Y1, r2X2, r2Y2) = rect2
		matchCnt = 0
		if ((r1X1 > r2X1) and (r1X1 < r2X2)):
			matchCnt += 1
		if ((r1Y1 < r2Y1) and (r1Y1 > r2Y2)):
			matchCnt += 1
		if ((r1X2 > r2X1) and (r1X2 < r2X2)):
			matchCnt += 1
		if ((r1Y2 < r2Y1) and (r1Y2 > r2Y2)):
			matchCnt += 1

		if (matchCnt >= 2):
			return True
		elif (bCheckBothWays):
			return self.oneINanother_r2lt2b(rect2, rect1, False)
		elif (matchCnt >= 1):
			return True
		else:
			return False

	def rotateXYByDeg(self, x, y, deg):
		rad = math.radians(deg)
		cosT = math.cos(rad)
		sinT = math.sin(rad)
		nx = x*cosT-y*sinT
		ny = x*sinT+y*cosT
		#print("DEBUG: Rotate({},{} by {}) = {},{}".format(x,y,deg,nx,ny))
		return nx,ny

	def rotateAndTranslateBy(self, polygon, deg, x, y):
		points = list()
		for i in polygon:
			nx, ny = self.rotateXYByDeg(i[0],i[1],deg)
			nx = nx+x
			ny = ny+y
			points.append([nx,ny])
		print("DEBUG:rotAndTransBy: {} => {}".format(polygon,points))
		return points

class PlotterCairo(PlotterGeneric):

	def __init__(self, fileName, dataArea, scale=SCALE_DEFAULT, plotArea=PLOTAREA_DEFAULT, plotAreaType=PLOTAREA_TYPE_TOPLEFT):
		PlotterGeneric.__init__(self, dataArea, scale, plotArea, plotAreaType)
		#Not mirroring along X axis by making self.scaleY negative, 
		#  because the cairo transform is setup for doing the same
		self.crSurface = cairo.SVGSurface(fileName, self.width, self.height)
		self.cr = cairo.Context(self.crSurface)
		#self.cr.transform(cairo.Matrix(scaleX, 0, 0, -1*scaleY, self.width/2, self.height/2))
		self.cr.set_source_rgb(0, 0, 0)

	def scale(self, x, y):
		return x*self.scaleX, y*self.scaleY

	def transform_xy(self, x, y):
		return x*self.scaleX+self.transX, y*self.scaleY+self.transY

	def color(self, r, g, b):
		self.cr.set_source_rgb(r/255, g/255, b/255)

	def move_to(self, x, y):
		x, y = self.dataXY2plotXY(x, y)
		self.cr.move_to(x, y)

	def line_to(self, x, y):
		x, y = self.dataXY2plotXY(x, y)
		self.cr.line_to(x, y)

	def stroke(self):
		self.cr.stroke()

	def fill(self):
		self.cr.fill()

	def dot(self, x, y, size=1):
		x, y = self.dataXY2plotXY(x, y)
		self.cr.rectangle(x, y, size, size)
		self.stroke()

	def textfont(self, fontName, slant, weight, size):
		self.cr.select_font_face(fontName, slant, weight)
		self.cr.set_font_size(size)

	def text(self, x, y, sText):
		x, y = self.dataXY2plotXY(x, y)
		xBearing, yBearing, tWidth, tHeight = self.cr.text_extents(sText)[:4]
		x1 = x-(tWidth/2)-xBearing-2
		y1 = y-(tHeight)
		self.cr.save()
		self.cr.set_source_rgba(0.8,0.8,0.8,0.5)
		self.cr.rectangle(x1,y1,(tWidth+4),(tHeight+4))
		self.cr.fill()
		self.cr.move_to(x1,y)
		# Save the Plotting related Transformation matrix so that
		# Temporarily I can switch to a identity matrix for the text plotting 
		# so that Text gets drawn properly independent of the transformation
		# being used for plotting other things
		self.cr.set_source_rgb(0.02,0.02,0.02)
		self.cr.show_text(sText)
		self.cr.restore()

	def clear(self):
		self.cr.paint()

	def flush(self):
		self.crSurface.flush()


class PlotterTurtle(PlotterGeneric):

	# Note As the Turtle graphics already has the Origin at the Center
	# of the plot area, there is no need for explicit translation to
	# achieve the same. so transX, transY = 0, 0
	# Similarly no need to mirror along X axis i.e make scaleY negative
	# because the Turtle graphics already has Positve Y towards Top
	def __init__(self, fileName, dataArea, scale=SCALE_DEFAULT, plotArea=PLOTAREA_DEFAULT, plotAreaType=PLOTAREA_TYPE_CENTER):
		PlotterGeneric.__init__(self, dataArea, scale, plotArea, plotAreaType)
		self.tr = turtle
		#self.tr.speed(0)
		#self.tr.hideturtle()
		self.tr.colormode(255)
		self.tr.color((0, 0, 0), (0, 0, 0))

	def scale(self, x, y):
		return x*self.scaleX, y*self.scaleY

	def transform_xy(self, x, y):
		return x*self.scaleX+self.transX, y*self.scaleY+self.transY

	def color(self, r, g, b):
		self.tr.color((r, g, b), (r, g, b))

	def move_to(self, x, y):
		x, y = self.dataXY2plotXY(x, y)
		self.tr.begin_fill()
		self.tr.penup()
		self.tr.goto(x, y)
		self.tr.pendown()

	def line_to(self, x, y):
		x, y = self.dataXY2plotXY(x, y)
		self.tr.pendown()
		self.tr.goto(x, y)
		self.tr.penup()

	def stroke(self):
		pass

	def fill(self):
		self.tr.end_fill()
		pass

	def dot(self, x, y, size=1):
		self.move_to(x, y)
		self.tr.dot()

	def textfont(self, fontName, slant, weight, size):
		pass

	def text(self, x, y, sText):
		self.move_to(x,y)
		self.tr.write(sText)

	def clear(self):
		self.tr.clear()

	def flush(self):
		pass

class PlotterTk(PlotterGeneric):

	def __init__(self, canvas, dataArea, scale=SCALE_DEFAULT, plotArea=PLOTAREA_DEFAULT, plotAreaType=PLOTAREA_TYPE_TOPLEFT):
		PlotterGeneric.__init__(self, dataArea, scale, plotArea, plotAreaType)
		if (canvas == None):
			self.cnvs = self.test_app()
		else:
			self.cnvs = canvas
		self.sColor = "#000000"

	def test_app(self):
		self.troot = tkinter.Tk()
		self.tframe = tkinter.Frame(self.troot)
		self.tframe.pack()
		canvas = tkinter.Canvas(self.tframe,width=self.width,height=self.height)
		canvas.pack()
		return canvas

	def scale(self, x, y):
		return x*self.scaleX, y*self.scaleY

	def transform_xy(self, x, y):
		return x*self.scaleX+self.transX, y*self.scaleY+self.transY

	def color(self, r, g, b):
		#print("Color:{}-{}-{} = {:02X}{:02X}{:02X}".format(r,g,b,r,g,b))
		self.sColor = "#{:02X}{:02X}{:02X}".format(r,g,b)
		#self.cnvs.tk_setPalette(foreground=self.sColor, background="#FFFFFF")
		pass

	def move_to(self, x, y):
		x, y = self.dataXY2plotXY(x, y)
		self.path = list()
		self.path.append((x,y))

	def line_to(self, x, y):
		x, y = self.dataXY2plotXY(x, y)
		self.path.append((x,y))

	def stroke(self):
		self.cnvs.create_line(self.path, fill=self.sColor)

	def fill(self):
		self.cnvs.create_polygon(self.path, fill=self.sColor)

	def dot(self, x, y, size=2):
		x, y = self.dataXY2plotXY(x, y)
		self.cnvs.create_oval(x, y, x+size, y+size, fill=self.sColor)

	def textfont(self, fontName, slant, weight, size):
		pass

	def text(self, x, y, sText):
		x, y = self.dataXY2plotXY(x, y)
		self.cnvs.create_text(x, y, text=sText, fill=self.sColor)

	def polygon(self, points):
		for i in range(0,len(points)):
			[x, y] = points[i]
			x, y = self.dataXY2plotXY(x, y)
			points[i] = [x,y]
		return self.cnvs.create_polygon(points, fill=self.sColor)

	def polygon_noscale(self, points):
		[x1, y1] = points[0]
		nx, ny = self.dataXY2plotXY(x1, y1)
		for i in range(0,len(points)):
			[x, y] = points[i]
			dx = x1-x
			dy = y1-y
			x = nx + dx
			y = ny + dy
			points[i] = [x,y]
		print("polynoscale:{}".format(points))
		return self.cnvs.create_polygon(points, fill=self.sColor)

	def clear(self):
		self.cnvs.create_rectangle(self.plotArea, fill=self.sColor)

	def flush(self):
		pass


if __name__ == "__main__":
	import sys
	if (sys.argv[1] == "turtle"):
		PLT = PlotterTurtle("/tmp/PltTurtle.test.dummy", (-200,200,200,-200))
	elif (sys.argv[1] == "tk"):
		#BAD PLT = PlotterTk("/tmp/PltTk.test.dummy", (-200,200,200,-200))
		# Above is bad because currently in this case plotArea gets directly mapped to dataArea
		# which makes the origin of plot area at Center while TK uses a TopLeft origin
		#PLT = PlotterTk("/tmp/PltTk.test.dummy", (-200,200,200,-200), plotArea=(0,0,440,440))
		#OK PLT = PlotterTk("/tmp/PltTk.test.dummy", (-220,220,220,-220), plotArea=(0,0,800,600))
		PLT = PlotterTk(None, (0,220,220,0), plotArea=(0,0,800,600))
	else:
		#BAD PLT = PlotterCairo("/tmp/PltCairo.test.svg", (-200,200,200,-200), plotArea=(-200,200,200,-200))
		# Above fails because plotArea is setup for Origin to be at Middle of plot area, but Cairo uses a TopLeft origin
		PLT = PlotterCairo("/tmp/PltCairo.test.svg", (-200,200,200,-200), plotArea=(0,0,400,400))

	PLT.color(255, 0, 0)
	PLT.text(0, 40, "AM I CLEARED???")
	PLT.clear()

	PLT.color(0, 255, 255)
	PLT.move_to(0, 0)
	PLT.line_to(200, 0)
	PLT.line_to(200, 200)
	PLT.stroke()

	PLT.color(0,255,0)
	PLT.move_to(50, 50)
	PLT.line_to(100, 50)
	PLT.line_to(50, 100)
	PLT.fill()

	PLT.color(255, 0, 255)
	PLT.dot(-120, -120, 10)

	PLT.color(0, 0, 255)
	PLT.text(0, 0, "Hello world long long long")
	PLT.dot(0, 0, 10)

	PLT.flush()

	input("Hope the test went smoothly...")

	while True:
		mode=input("SpecifyMode[1,2,quit]:")
		if (mode == "1"):
			PLT = PlotterGeneric((0,0,1000,1000),(100,100,200,200))
		elif (mode == "2"):
			PLT = PlotterGeneric((0,0,1000,1000),(-100,100,-200,200))
		else:
			break
		try:
			while True:
				dX = int(input("Enter DataX:"))
				pX,pY = PLT.dataArea2plotArea(dX,0)
				print("DataX[{}] = PlotX[{}]".format(dX, pX))
		except:
			print(sys.exc_info())
			pass

