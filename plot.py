#!/usr/bin/python

import matplotlib.pyplot as pp
import matplotlib.colorbar as cb
import RadarFigure as rf
import h5py
from optparse import OptionParser as op
import sys

if __name__ == "__main__":

# Main function begins here
   parser = op()
   parser.add_option("-f", "--file", dest="fileName", 
         help="base filename to open")

   (options, args) = parser.parse_args()
   fileName = options.fileName

   if(fileName == None):
      print '\n\nERROR: no filename found'
      print 'usage: plot.py -f filename.h5'
      sys.exit(2)

   print fileName

   fapl = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
   file = h5py.File(fileName, mode='r');

   #retrieve sample rate
   pImage = rf.PlotImage(file);
   pImage.Update(ds);

   #display image
   pp.show();
