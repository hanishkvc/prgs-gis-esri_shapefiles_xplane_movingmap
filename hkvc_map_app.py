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
	gCanvas.grid(row=0, column=0, columnspan=4)
	btnQuit = tkinter.Button(frameMain, text="Quit", command=gRoot.quit)
	btnQuit.grid(row=1, column=0)
	btnZoomIn = tkinter.Button(frameMain, text="ZoomIn")
	btnZoomIn.grid(row=1, column=1)
	btnZoomOut = tkinter.Button(frameMain, text="ZoomOut")
	btnZoomOut.grid(row=1, column=2)
	btnUpdate = tkinter.Button(frameMain, text="Update", command=load_map)
	btnUpdate.grid(row=1, column=3)
	frameMain.pack()
	return gRoot, gCanvas

def load_map():
	global gShpHandler
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


setup_app()
gPltr = hkvc_plotter.PlotterTk(gCanvas,(-180,90,180,-90),plotArea=(0,0,800,600))
gShpHandler = hkvc_map_esri_shapefile_shp.SHPHandler(gPltr)
gRoot.mainloop()

