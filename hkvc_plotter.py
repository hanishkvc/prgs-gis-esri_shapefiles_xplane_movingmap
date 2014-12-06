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

class PlotterCairo:

	def __init__(self, fileName, width, height, scaleX=1, scaleY=1):
		self.scaleX = scaleX
		self.scaleY = scaleY
		self.width, self.height = self.scale(width, height)
		self.crSurface = cairo.SVGSurface(fileName, self.width, self.height)
		self.cr = cairo.Context(self.crSurface)
		self.cr.transform(cairo.Matrix(1, 0, 0, -1, self.width/2, self.height/2))
		self.cr.set_source_rgb(0, 0, 0)

	def scale(self, x, y):
		return x*self.scaleX, y*self.scaleY

	def color(self, r, g, b):
		self.cr.set_source_rgb(r/255, g/255, b/255)

	def move_to(self, x, y):
		x, y = self.scale(x, y)
		self.cr.move_to(x, y)

	def line_to(self, x, y):
		x, y = self.scale(x, y)
		self.cr.line_to(x, y)

	def stroke(self):
		self.cr.stroke()

	def fill(self):
		self.cr.fill()

	def dot(self, x, y):
		x, y = self.scale(x, y)
		self.cr.rectangle(x, y, 1, 1)
		self.stroke()

	def text(self, x, y, sText):
		x, y = self.scale(x, y)
		self.cr.select_font_face("Courier 10 Pitch", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		self.cr.set_font_size(20)
		xBearing, yBearing, tWidth, tHeight = self.cr.text_extents(sText)[:4]
		self.cr.move_to((x-(tWidth/2)),(y-(tHeight/2)-yBearing))
		# Save the Plotting related Transformation matrix so that
		# Temporarily I can switch to a identity matrix for the text plotting 
		# so that Text gets drawn properly independent of the transformation
		# being used for plotting other things
		savedMatrix = self.cr.get_matrix()
		#self.cr.set_matrix(cairo.Matrix())
		self.cr.identity_matrix()
		self.cr.show_text(sText)
		self.cr.set_matrix(savedMatrix)

	def flush(self):
		self.crSurface.flush()


class PlotterTurtle:

	def __init__(self, fileName, width, height, scaleX=1, scaleY=1):
		self.scaleX = scaleX
		self.scaleY = scaleY
		self.tr = turtle
		#self.tr.speed(0)
		#self.tr.hideturtle()
		self.tr.colormode(255)
		self.tr.color((0, 0, 0), (0, 0, 0))

	def scale(self, x, y):
		return x*self.scaleX, y*self.scaleY

	def color(self, r, g, b):
		self.tr.color((r, g, b), (r, g, b))

	def move_to(self, x, y):
		x, y = self.scale(x, y)
		self.tr.begin_fill()
		self.tr.penup()
		self.tr.goto(x, y)
		self.tr.pendown()

	def line_to(self, x, y):
		x, y = self.scale(x, y)
		self.tr.pendown()
		self.tr.goto(x, y)
		self.tr.penup()

	def stroke(self):
		pass

	def fill(self):
		self.tr.end_fill()
		pass

	def dot(self, x, y):
		self.move_to(x, y)
		self.tr.dot()

	def text(self, x, y, sText):
		self.move_to(x,y)
		self.tr.write(sText)

	def flush(self):
		pass


if __name__ == "__main__":
	PTr = PlotterTurtle("/tmp/turtle.test.dummy", 500, 500, 2, 2)
	PCr = PlotterCairo("/tmp/cairo.test.svg", 500, 500, 2, 2)

	PTr.move_to(0, 0)
	PCr.move_to(0, 0)
	PTr.line_to(200, 0)
	PCr.line_to(200, 0)
	PTr.line_to(200, 200)
	PCr.line_to(200, 200)
	PTr.stroke()
	PCr.stroke()

	PTr.color(255, 0, 0)
	PCr.color(255, 0, 0)
	PTr.dot(-200, -200)
	PCr.dot(-200, -200)

	PTr.text(0, 0, "Hello world long long long")
	PCr.text(0, 0, "Hello world long long long")

	PTr.flush()
	PCr.flush()

	input("Hope the test went smoothly...")

