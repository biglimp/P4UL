#!/usr/bin/env python
import sys
import argparse
import numpy as np
from mapTools import *
from footprintTools import readNumpyZFootprint
from utilities import filesFromList
from plotTools import addImagePlot, userLabels
import matplotlib.pyplot as plt
''' 
Description:


Author: Mikko Auvinen
        mikko.auvinen@helsinki.fi 
        University of Helsinki &
        Finnish Meteorological Institute
'''

#==========================================================#
parser = argparse.ArgumentParser(prog='plotRasterData.py')
parser.add_argument("-f","--filename", type=str, default=None,\
  help="Name of the raster file.")
parser.add_argument("-s", "--size", type=float, default=13.,\
  help="Size of the figure (length of the longer side). Default=13.")
parser.add_argument("--lims", help="User specified limits.", action="store_true",\
  default=False)
parser.add_argument("--grid", help="Turn on grid.", action="store_true",\
  default=False)
parser.add_argument("--labels", help="User specified labels.", action="store_true",\
  default=False)
parser.add_argument("--footprint", help="Plot footprint data.", action="store_true",\
  default=False)
parser.add_argument("--save", metavar="FORMAT" ,type=str,\
  default='', help="Save the figure in specified format. Formats available: jpg, png, pdf, ps, eps and svg")
parser.add_argument("--dpi", metavar="DPI" ,type=int,\
  default=100, help="Desired resolution in DPI for the output image. Default: 100")
args = parser.parse_args() 
#writeLog( parser, args )
#==========================================================#
# Renaming ... that's all.
rasterfile  = args.filename
size        = args.size
limsOn      = args.lims
gridOn      = args.grid
labels      = args.labels
footprintOn = args.footprint
save        = args.save

plt.rc('xtick', labelsize=14); #plt.rc('ytick.major', size=10)
plt.rc('ytick', labelsize=14); #plt.rc('ytick.minor', size=6)
plt.rc('axes', titlesize=18)

if( not footprintOn ):
  Rdict = readNumpyZTile(rasterfile)
  R = Rdict['R']
  Rdims = np.array(np.shape(R))
  ROrig = Rdict['GlobOrig']
  dPx = Rdict['dPx']
  Rdict = None
else:
  R, X, Y, Z, C = readNumpyZFootprint(rasterfile)
  Rdims = np.array(np.shape(R))
  ROrig = np.zeros(2)
  dPx   = np.array([ (X[0,1]-X[0,0]) , (Y[1,0]-Y[0,0]) ])
  X = None; Y = None; Z = None; C = None  # Clear memory
  

info = ''' Info:
 Dimensions [rows, cols] = {}
 Origin (top-left) [N,E] = {}
 Resolution        [dX,dY] = {}
'''.format(Rdims,ROrig,dPx)

print(info)

figDims = size*(Rdims[::-1].astype(float)/np.max(Rdims))
fig = plt.figure(num=1, figsize=figDims)
fig = addImagePlot( fig, R , rasterfile, gridOn, limsOn)
R = None

if(labels):
  fig = userLabels( fig )

if(not(save=='')):
  filename = rasterfile.split('/')[-1]  # Remove the path in Linux system
  filename = filename.split('\\')[-1]   # Remove the path in Windows system
  filename = filename.strip('.npz')+'.'+save
  fig.savefig( filename, format=save, dpi=args.dpi)
  
plt.show()

