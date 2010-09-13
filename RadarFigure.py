import matplotlib as mp
import numpy as np
import fltk as Fltk
import RadarTools as rt
import matplotlib.cm as cm
import matplotlib.pyplot as pp

class TableIndexer:
   def __init__(self, items):
      self.items = items
      self.numItems = len(items)
      self.idx = 0000

   def Forward(self):
      if( self.idx < len(self.items)-1):
         self.idx += 1
      return self.items[self.idx]

   def Reverse(self):
      if( self.idx > 0):
         self.idx -= 1
      return self.items[self.idx]

   def Current(self):
      return self.items[self.idx]

   def Set(self,value):
      count =0
      for idx in self.items:
         if idx == value:
            break
         count += 1
      self.idx = count
      print self.idx

class CustomAxisMenu:
    def __init__(self, toolbar):
        self.toolbar=toolbar
        self._naxes = toolbar.naxes

    def adjust(self, naxes):
        return

    def widget(self):
        return self.mbutton

    def get_indices(self):
        return 0

# callback from menu button 'Power'
def PowerCallBack(ptr,amenu):
    amenu.map = amenu.powerMap 
    amenu.Update()

# callback from menu button 'Doppler'
def DopplerCallBack(ptr,amenu):
    amenu.map = amenu.dopplerMap
    amenu.Update()

class PlotImage:

   def   __init__(self,file):


      # flag to initialize data on first run
      self.firstCall = True

      #create figure
      self.fig = pp.figure();

      #add plot to figure
      self.ax  = self.fig.add_subplot(111);
      self.ipp = file.attrs.get('IPP',0)*1e3;
      self.file = file;

      self.keys = file.keys();

      self.tIndex = TableIndexer(self.keys);

      #access toolbar callbacks and reassign with custom functionality
      manager = pp.get_current_fig_manager();
      toolbar = manager.toolbar
      fButton = toolbar.bForward.widget()
      rButton = toolbar.bBack.widget()
      fButton.callback(self.forward)
      rButton.callback(self.reverse)
      
      #get access to existing menu button widget on toolbar
      menuButton = toolbar.omenu.widget()

      #get rid of default buttons
      menuButton.clear()
      toolbar.omenu = CustomAxisMenu(toolbar)

      #add our custom buttons and callbacks
      menuButton.add('Power Map',0,PowerCallBack,self)
      menuButton.add('Doppler Map',0,DopplerCallBack,self)
      menuButton.resize(0,0,70,10)
      menuButton.label('Plot Type')

      t1,t2,w,h = toolbar.canvas.figure.bbox.bounds
      toolbar.message.resize(0,0,int(w/3),8)
      self.input = Fltk.Fl_Input(0,0,int(90),8)
      self.searchButton = Fltk.Fl_Button(0,0,int(70),8,'&Search')
      self.searchButton.callback(Search,self)
      toolbar._group.add(self.input)
      toolbar._group.add(self.searchButton)
      toolbar.update()
      self.ds = self.file[self.tIndex.Current()]
      time = self.ds.attrs.get('START_TIME','00:00:00')
      fs = self.file.attrs.get('OUTPUT_RATE',0)
      winStart = self.file.attrs.get('RxWin_START',0)
      winStop = self.file.attrs.get('RxWin_STOP',0)

      # initialize instances of PowerMap and DopplerMap
      # this will be referenced later when the user chooses
      # the desired plot type
      self.powerMap = rt.PowerMap(self.ds, file, fs, winStart, winStop)
      self.dopplerMap = rt.DopplerMap(self.ds, file, fs, winStart, winStop)

      #default to power map computation
      self.map = self.powerMap

      self.Update()
      pp.show()

   #callback for right arrow on toolbar
   def forward(self,ptr,args):
      table = self.tIndex.Forward();
      self.ds = self.file[table];
      self.Update();
      print table

   #callback for left arrow on toolbar
   def reverse(self,ptr,args):
      table = self.tIndex.Reverse()
      self.ds = self.file[table];
      self.Update();
      print table

   #updates the image with new data
   def Update(self):
      
      dSet = self.ds

      #read table's time attribute
      time = dSet.attrs.get('START_TIME','00:00:00')

      #trim data samples to remove FIR garbage
      dSet = dSet[:,20:dSet.shape[1]] 
      
      #perform computation that user has chosen
      pMap = self.map.Execute(dSet)
      pMean = pMap.mean();
      pMap = np.clip(pMap, pMean, pMap.max());

      # on the first call to imshow, we set things up - subsequent calls
      # change only necessary variables for efficiency
      if(self.firstCall == True):
         #produce image
         self.cax = self.ax.imshow(pMap, cmap=cm.jet, origin=self.map.origin, 
               interpolation='gaussian', aspect='auto',extent=self.map.extent)
         #setup colorbar
         self.cbar = self.fig.colorbar(self.cax, orientation='vertical', shrink=0.7)
         self.cbar.set_label('dB')
         self.firstCall = False
      else:
         self.cax.set_extent(self.map.extent)
         self.cax.origin = self.map.origin
         self.cax.set_clim([pMean,pMap.max()])
         self.cax.set_data(pMap)
         self.cax.changed

      #set labels
      self.ax.set_xlabel(self.map.xLabel)
      self.ax.set_ylabel(self.map.yLabel)
      self.ax.set_title('02/Jan/2010 Time: '+ time + ' EST')

      #update figure
      pp.draw();

def Search(self,args):
   value = args.input.value()

   for idx in args.keys:
      time = args.file[idx].attrs.get('START_TIME','00:00:00')
      if time == value:
         break

   if(idx == None):
     args.input.value('Not Found')
   else:
     args.ds = args.file[idx]
     args.tIndex.Set(idx)
     args.Update()
  
   
