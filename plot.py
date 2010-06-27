#!/usr/bin/python

import matplotlib.pyplot as pp
import matplotlib.colorbar as cb
import RadarFigure as rf
import h5py
from optparse import OptionParser as op
import sys

# this lengthy function parses the input file name, ensures proper structure,
# and converts into the family driver name required by HDF5
def CreateFamilyName(file):

   # convert filename to list and reverse for parsing
   rfile = list(file)
   rfile.reverse()
   
   #find file extension separator
   idx1=None
   for i in rfile:
      if i == '.':
         idx1 = rfile.index(i)
         break

   #if file doesn't contain extension - throw error and exit 
   if(idx1 == None):
      print '\n\nERROR: Filename must be the first file in a set (e.g. /home/foo/data_bar0000.h5)'
      sys.exit(2)

   #save file extension for later use
   extList = rfile[0:idx1+1]
   extList.reverse()
   ext = ''.join(extList)

   #find first nondigit character before file separator and mark
   for i in rfile[idx1+1:]: 
      if i.isdigit()==False:
         idx2 = rfile.index(i)
         break

   #determine how many zeros are contained in the file name
   padding = idx2 - idx1 - 1

   #strip index, ext. separator, and index number from file (i.e. base filename)
   del rfile[0:idx2]

   #re-reverse list and save as file
   rfile.reverse()
   fileName = ''.join(rfile)#.reverse()
   #create family-friendly filename
   fileName = fileName + '%0' + str(padding) + 'd' + ext
   return fileName

if __name__ == "__main__":

# Main function begins here
   parser = op()
   parser.add_option("-f", "--file", dest="fileName", help="base filename to open")

   (options, args) = parser.parse_args()
   fileName = options.fileName

   if(fileName == None):
      print '\n\nERROR: no filename found'
      print 'usage: plot.py -f filename0000.h5'
      sys.exit(2)

   fileName = CreateFamilyName(fileName)
   print fileName

   fapl = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
   fapl.set_fapl_family(1<<30)
   file = h5py.File(fileName, mode='r', driver='family', memb_size=1<<30);

   #retrieve sample rate
   pImage = rf.PlotImage(file);
   pImage.Update(ds);

   #display image
   pp.show();
