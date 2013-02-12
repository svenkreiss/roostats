#!/usr/bin/env python

#  BatchProfileLikelihood
# 
#  date: February 12, 2013
# 
#  This is a standard demo that can be used with any ROOT file
#  prepared in the standard way.  You specify:
#  - name for input ROOT file
#  - name of workspace inside ROOT file that holds model and data
#  - name of ModelConfig that specifies details for calculator tools
#  - name of dataset

__author__ = "Sven Kreiss, Kyle Cranmer"
__version__ = "0.1"


import helperModifyModelConfig


import optparse
parser = optparse.OptionParser(version="0.1")
parser.add_option("-o", "--output", help="output location", type="string", dest="output", default="batchOutput/")

helperModifyModelConfig.addOptionsToOptParse( parser )
parser.add_option("-c", "--counter", help="Number of this job.", dest="counter", type="int", default=1)
parser.add_option("-j", "--jobs", help="Number of jobs.", dest="jobs", type="int", default=1)

parser.add_option("-f", "--fullRun", help="Do a full run.", dest="fullRun", default=False, action="store_true")

parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True, help="Quiet output.")
options,args = parser.parse_args()


import ROOT
import helperStyle

import PyROOTUtils
import math
from array import array


def setParameterToBin( par, binNumber ):
   par.setVal( par.getMin() +  (float(binNumber)+0.5)/par.getBins()*( par.getMax()-par.getMin() ) )
   
def parametersNCube( parL, i ):
   for d in reversed( range(parL.getSize()) ):
      if d >= 1:
         lowerDim = reduce( lambda x,y: x*y, [parL.at(dd).getBins() for dd in range(d)] )
         #print( "Par %s: lowerDim=%d, i=%d, i%%lowerDim=%d" % (parL.at(d).GetName(), lowerDim, i, i%lowerDim) )
         setParameterToBin( parL.at(d), int(i/lowerDim) )
         i -= int(i/lowerDim) * lowerDim
      else:
         setParameterToBin( parL.at(d), i )


def main():
   ROOT.RooRandom.randomGenerator().SetSeed( 0 )

   f = ROOT.TFile.Open( options.input )
   w = f.Get( options.wsName )
   mc = w.obj( options.mcName )
   data = w.data( options.dataName )

   helperModifyModelConfig.apply( options, w, mc )

   firstPOI = mc.GetParametersOfInterest().first()
   poiL = ROOT.RooArgList( mc.GetParametersOfInterest() )
   listNuisPars = ROOT.RooArgList( mc.GetNuisanceParameters() )
   
   numPoints = reduce( lambda x,y: x*y, [poiL.at(d).getBins() for d in range(poiL.getSize())] )
   print( "Total grid points: "+str(numPoints) )

   if options.fullRun:
      # visualize bin enumeration
      if poiL.getSize() != 2:
         print( "ERROR: This is a 2D test." )
         return
      
      numbers = ROOT.TH2F( "binsVis", "visualize bin enumeration;"+poiL.at(0).GetTitle()+";"+poiL.at(1).GetTitle(), 
         poiL.at(0).getBins(), poiL.at(0).getMin(), poiL.at(0).getMax(),
         poiL.at(1).getBins(), poiL.at(1).getMin(), poiL.at(1).getMax(),
      )
      jobs = ROOT.TH2F( "jobsVis", "visualize jobs;"+poiL.at(0).GetTitle()+";"+poiL.at(1).GetTitle(), 
         poiL.at(0).getBins(), poiL.at(0).getMin(), poiL.at(0).getMax(),
         poiL.at(1).getBins(), poiL.at(1).getMin(), poiL.at(1).getMax(),
      )
      for i in range( poiL.at(0).getBins()*poiL.at(1).getBins() ):
         parametersNCube( poiL, i )
         numbers.SetBinContent( numbers.FindBin( poiL.at(0).getVal(), poiL.at(1).getVal() ), i+1 )
         jobs.SetBinContent( jobs.FindBin( poiL.at(0).getVal(), poiL.at(1).getVal() ), int(float(i)/numPoints*options.jobs)+1 )

      canvas = ROOT.TCanvas( "binEnumeration", "binEnumeration", 800, 400 )
      canvas.SetGrid()
      canvas.Divide(2)
      canvas.cd(1)
      numbers.Draw("COL")
      numbers.Draw("TEXT,SAME")
      canvas.cd(2)
      jobs.Draw("COL")
      jobs.Draw("TEXT,SAME")
      canvas.SaveAs( "docImages/binEnumeration2D.png" )
      canvas.Update()
      raw_input( "finished bin enum plot. Press enter ..." )

   
   


if __name__ == "__main__":
   main()
