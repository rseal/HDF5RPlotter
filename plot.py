#!/usr/bin/env python2

import matplotlib.pyplot as pp
import matplotlib.colorbar as cb
import RadarFigure as rf
import h5py
import argparse
import sys

if __name__ == "__main__":

# Main function begins here
   parser = argparse.ArgumentParser()
   parser.add_argument('--file', dest='fname', help='filename to open')
   args = parser.parse_args()

   if not args.fname:
      parser.print_help()

   print args.fname

   fapl = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
   file = h5py.File(args.fname, mode='r');

   #retrieve sample rate
   pImage = rf.PlotImage(file);
   pImage.Update(ds);

   #display image
   pp.show();
