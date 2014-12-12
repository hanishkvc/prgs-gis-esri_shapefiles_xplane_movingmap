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
import hkvc_map_esri_shapefile_shp
import tkinter

gRoot = None
gCanvas = None
gShpHandler = None

def setup_app():
	global gRoot
	global gCanvas
	gRoot = tkinter.Tk()
	frameMain = tkinter.Frame(gRoot)
	gCanvas = tkinter.Canvas(frameMain, width=800, height=600)
	gCanvas.grid(row=0, column=0, columnspan=7)

	btnQuit = tkinter.Button(frameMain, text="Quit", command=gRoot.quit)
	btnQuit.grid(row=2, column=0)
	btnZoomIn = tkinter.Button(frameMain, text="ZoomIn", command=zoom_in)
	btnZoomIn.grid(row=2, column=1)
	btnZoomOut = tkinter.Button(frameMain, text="ZoomOut", command=zoom_out)
	btnZoomOut.grid(row=2, column=2)
	btnUpdate = tkinter.Button(frameMain, text="Update", command=load_map)
	btnUpdate.grid(row=2, column=3)

	btnMoveTop = tkinter.Button(frameMain, text="Top", command=move_top)
	btnMoveTop.grid(row=1, column=5)
	btnMoveLeft = tkinter.Button(frameMain, text="Left", command=move_left)
	btnMoveLeft.grid(row=2, column=4)
	btnMoveRight = tkinter.Button(frameMain, text="Right", command=move_right)
	btnMoveRight.grid(row=2, column=6)
	btnMoveBottom = tkinter.Button(frameMain, text="Bottom", command=move_bottom)
	btnMoveBottom.grid(row=3, column=5)

	frameMain.pack()
	return gRoot, gCanvas

def load_map():
	global gShpHandler
	gShpHandler.plotter.clear()
	for i in range(1,len(sys.argv)):
		gShpHandler.setup(sys.argv[i])
		try:
			gShpHandler.shp_read_records()
		except:
			print(sys.exc_info())
			if (gShpHandler.fileLength == gShpHandler.shpFile.tell()):
				print("INFO: Seems like End of File![{}]".format(gShpHandler.shpFile.tell()))
			else:
				print("WARN: Unexpected FileLocation?[{}]".format(gShpHandler.shpFile.tell()))
				input("CHECK: Hope above is fine...")

		gShpHandler.cleanup()
		#input("INFO: Shapefile[{}] processed...".format(sys.argv[i]))
	gShpHandler.plotter.flush()
	#input("Hope the shapefile was plotted well...")

def zoom_in():
	(dX1, dY1, dX2, dY2) = gPltr.dataArea
	dX1 = dX1*0.8
	dY1 = dY1*0.8
	dX2 = dX2*0.8
	dY2 = dY2*0.8
	gPltr.setup_data2plot((dX1,dY1,dX2,dY2), plotArea=gPltr.plotArea)
	load_map()

def zoom_out():
	(dX1, dY1, dX2, dY2) = gPltr.dataArea
	dX1 = dX1*1.2
	dY1 = dY1*1.2
	dX2 = dX2*1.2
	dY2 = dY2*1.2
	gPltr.setup_data2plot((dX1,dY1,dX2,dY2), plotArea=gPltr.plotArea)
	load_map()

def move_top():
	(dX1, dY1, dX2, dY2) = gPltr.dataArea
	dY = abs(dY2-dY1)
	dY1 += dY*0.2
	dY2 += dY*0.2
	gPltr.setup_data2plot((dX1,dY1,dX2,dY2), plotArea=gPltr.plotArea)
	load_map()

def move_bottom():
	(dX1, dY1, dX2, dY2) = gPltr.dataArea
	dY = abs(dY2-dY1)
	dY1 -= dY*0.2
	dY2 -= dY*0.2
	gPltr.setup_data2plot((dX1,dY1,dX2,dY2), plotArea=gPltr.plotArea)
	load_map()

def move_left():
	(dX1, dY1, dX2, dY2) = gPltr.dataArea
	dX = abs(dX2-dX1)
	dX1 -= dX*0.2
	dX2 -= dX*0.2
	gPltr.setup_data2plot((dX1,dY1,dX2,dY2), plotArea=gPltr.plotArea)
	load_map()

def move_right():
	(dX1, dY1, dX2, dY2) = gPltr.dataArea
	dX = abs(dX2-dX1)
	dX1 += dX*0.2
	dX2 += dX*0.2
	gPltr.setup_data2plot((dX1,dY1,dX2,dY2), plotArea=gPltr.plotArea)
	load_map()


setup_app()
#gPltr = hkvc_plotter.PlotterTk(gCanvas,(-180,90,180,-90),plotArea=(0,0,800,600))
gPltr = hkvc_plotter.PlotterTk(gCanvas,(-180,90,180,-90),scale=(2,2))
gShpHandler = hkvc_map_esri_shapefile_shp.SHPHandler(gPltr)
gRoot.mainloop()

