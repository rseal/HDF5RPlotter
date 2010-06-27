import numpy as np
import scipy.stsci as sp

class Compute:
   def __init__(self, data, file, sampleRate, bitScale=15.0):
      
      self.shape = data.shape
      self.bits = bitScale
      self.sRate = sampleRate
      self.xLabel = 'xAxis'
      self.yLabel = 'yAxis'
      self.title = 'title'
      self.origin = 'lower'

      #compute range
      dStart =data.attrs.get('DATA_WIN_START', 0)
      dSize  = data.attrs.get('DATA_WIN_SIZE',0)
      self.h0 = np.round(150e3*dStart/self.sRate);
      self.hf = np.round( self.h0 + 150e3*dSize/self.sRate);
      self.ipp = file.attrs.get('IPP',0)*1e3;

      #setup scales
      self.extent = [0,data.shape[0],self.h0,self.hf]

   def Execute(self,data):
      #override in derived classes
      pass

   def PartitionSize(self,data, dim):

      length = data.shape[dim]
      partSize = int(length/self.numProcessors)
      isEven = length%self.numProcessors

      partition = []
      for i in range(0,self.numProcessors):
         partition.append(partSize)

      if(isEven != False):
         partition[len(partition)-1] = partSize+1

      return partition

class PowerMap(Compute):

    def __init__(self, data, sampleRate, bitScale=15.0):
       Compute.__init__(self, data, sampleRate, bitScale)
       self.xLabel = 'IPP (' + str(self.ipp) + ' ms)' 
       self.yLabel = 'Range (Km)' 

    def Execute(self,data):
       
       #compute power in both components
       pReal = np.power(data['real'],2.0)
       pImag = np.power(data['imag'],2.0)

       #clip data to remove 0 values
       pReal = np.clip(pReal,1e-15,pReal.max())
       pImag = np.clip(pImag,1e-15,pImag.max())

       #convert to dB
       pMap = 10*np.log10(pReal + pImag)
       pMap = np.transpose(pMap)

       return pMap

class DopplerMap(Compute):

    def __init__(self, data, sampleRate, bitScale=15.0):
       Compute.__init__(self, data, sampleRate, bitScale)
       self.xLabel = 'Range (Km)'
       self.yLabel = 'Velocity (m/s)' 
       self.origin = 'upper'
       self.extent = [self.h0,self.hf,-6/(self.ipp*2),6/(self.ipp*2)]

    def Execute(self,data):

       #compute power in both components
       pReal = (data['real']/2.0**self.bits)
       pImag = (data['imag']/2.0**self.bits)

       # create empty complex array to combine pReal and pImag
       data = np.empty(pReal.shape, dtype=complex)
       data.real = pReal;
       data.imag = pImag;
       
       # subtract average dc from each range
       dc = np.mean(data,axis=0)
       data = np.subtract(data[:,],dc)
       data = np.clip(data,1e-15,np.max(data))

     
       coeff = np.blackman(64)
       for i in range(0,data.shape[1]):
          data[:,i] = np.convolve(data[:,i],coeff,'same')


       # compute complex 256-point for each range cell
       dMap = np.fft.fft(data,256, axis=0)
       dMap = np.fft.fftshift(dMap,axes=(0,))

       # convert values to dB
       dMap = 20*np.log10(np.abs(dMap));
    
       return dMap

