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
parser.add_option(      "--unconditionalFitInSeparateJob", help="Do the unconditional fit in a separate job", dest="unconditionalFitInSeparateJob", default=False, action="store_true")

parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True, help="Quiet output.")
options,args = parser.parse_args()

# to calculate unconditionalFitInSeparateJob, reduce options.jobs by one to make room for the extra job
if options.unconditionalFitInSeparateJob: options.jobs -= 1


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
         
def jobBins( numPoints ):
   if options.unconditionalFitInSeparateJob and options.counter == options.jobs:
      return (0,0)

   return (
      int(math.ceil(float(options.counter)*numPoints/options.jobs)),
      int(math.ceil(float(options.counter+1.0)*numPoints/options.jobs))
   )

def visualizeEnumeration( poiL ):
   if poiL.getSize() != 2:
      print( "ERROR: This is a 2D test." )
      return
   
   numbers = ROOT.TH2F( "binsVis", "visualize bin enumeration;"+poiL.at(0).GetTitle()+";"+poiL.at(1).GetTitle(), 
      poiL.at(0).getBins(), poiL.at(0).getMin(), poiL.at(0).getMax(),
      poiL.at(1).getBins(), poiL.at(1).getMin(), poiL.at(1).getMax(),
   )
   jobs = ROOT.TH2F( "jobsVis", "visualize jobs highlighting job "+str(options.counter)+";"+poiL.at(0).GetTitle()+";"+poiL.at(1).GetTitle(), 
      poiL.at(0).getBins(), poiL.at(0).getMin(), poiL.at(0).getMax(),
      poiL.at(1).getBins(), poiL.at(1).getMin(), poiL.at(1).getMax(),
   )
   jobsMask = ROOT.TH2F( "jobsMask", "visualize jobs highlighting job "+str(options.counter)+";"+poiL.at(0).GetTitle()+";"+poiL.at(1).GetTitle(), 
      poiL.at(0).getBins(), poiL.at(0).getMin(), poiL.at(0).getMax(),
      poiL.at(1).getBins(), poiL.at(1).getMin(), poiL.at(1).getMax(),
   )

   numPoints = reduce( lambda x,y: x*y, [poiL.at(d).getBins() for d in range(poiL.getSize())] )
   for i in range( poiL.at(0).getBins()*poiL.at(1).getBins() ):
      parametersNCube( poiL, i )
      numbers.SetBinContent( numbers.FindBin( poiL.at(0).getVal(), poiL.at(1).getVal() ), i )
      jobs.SetBinContent( jobs.FindBin( poiL.at(0).getVal(), poiL.at(1).getVal() ), int(float(i)/numPoints*options.jobs) )

   firstPoint,lastPoint = jobBins( numPoints )
   for i in range( firstPoint,lastPoint ):
      parametersNCube( poiL, i )
      jobsMask.SetBinContent(
         jobsMask.FindBin( poiL.at(0).getVal(), poiL.at(1).getVal() ),
         1000
      )

   canvas = ROOT.TCanvas( "binEnumeration", "binEnumeration", 800, 400 )
   canvas.SetGrid()
   canvas.Divide(2)
   canvas.cd(1)
   numbers.Draw("COL")
   numbers.Draw("TEXT,SAME")
   canvas.cd(2)
   jobs.Draw("COL")
   jobsMask.Draw("BOX,SAME")
   jobs.Draw("TEXT,SAME")
   canvas.SaveAs( "docImages/binEnumeration2D.png" )
   canvas.Update()
   raw_input( "Press enter to continue ..." )






def minimize( nll ):
   
   strat = ROOT.Math.MinimizerOptions.DefaultStrategy()

   msglevel = ROOT.RooMsgService.instance().globalKillBelow()
   if not options.verbose:
      ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)

   minim = ROOT.RooMinimizer( nll )
   if not options.verbose:
      minim.setPrintLevel(-1)
   else:
      minim.setPrintLevel(1)
   minim.setStrategy(strat)
   minim.optimizeConst(0)

   # Got to be very careful with SCAN. We have to allow for negative mu,
   # so large part of the space that is scanned produces log-eval errors.
   # Therefore, this is usually not feasible.
   #minim.minimize(ROOT.Math.MinimizerOptions.DefaultMinimizerType(), "Scan")
   
   status = -1
   for i in range( 3 ):
      status = minim.minimize(ROOT.Math.MinimizerOptions.DefaultMinimizerType(), 
                              ROOT.Math.MinimizerOptions.DefaultMinimizerAlgo())
      if status == 0: break

      if status != 0  and  status != 1  and  strat <= 1:
         strat += 1
         print( "Retrying with strat "+str(strat) )
         minim.setStrategy(strat)
         status = minim.minimize(ROOT.Math.MinimizerOptions.DefaultMinimizerType(), 
                                 ROOT.Math.MinimizerOptions.DefaultMinimizerAlgo())
      
      if status != 0  and  status != 1  and  strat <= 1:
         strat += 1
         print( "Retrying with strat "+str(strat) )
         minim.setStrategy(strat)
         status = minim.minimize(ROOT.Math.MinimizerOptions.DefaultMinimizerType(), 
                                 ROOT.Math.MinimizerOptions.DefaultMinimizerAlgo())
      
   if status != 0 and status != 1:
      print( "ERROR::Minimization failed!" )

   ROOT.RooMsgService.instance().setGlobalKillBelow(msglevel)
   return nll.getVal()






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

   if options.fullRun: visualizeEnumeration( poiL )



   ##### Script starts here
   

   #ROOT.RooAbsReal.defaultIntegratorConfig().method1D().setLabel("RooAdaptiveGaussKronrodIntegrator1D")

   ROOT.Math.MinimizerOptions.SetDefaultMinimizer("Minuit2")
   ROOT.Math.MinimizerOptions.SetDefaultStrategy(0)
   #ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(1)
   ROOT.Math.MinimizerOptions.SetDefaultPrintLevel(-1)
   #ROOT.Math.MinimizerOptions.SetDefaultTolerance(0.0001)

   params = mc.GetPdf().getParameters(data)
   ROOT.RooStats.RemoveConstantParameters(params)
   nll = mc.GetPdf().createNLL(data, ROOT.RooFit.CloneData(ROOT.kFALSE), ROOT.RooFit.Constrain(params))
   nll.setEvalErrorLoggingMode(ROOT.RooAbsReal.CountErrors)



      
   numPoints = reduce( lambda x,y: x*y, [poiL.at(d).getBins() for d in range(poiL.getSize())] )
   firstPoint,lastPoint = jobBins( numPoints )
   print( "" )
   print( "# Batch Job" )
   print( "" )
   print( "* Total grid points: "+str(numPoints) )
   print( "* Total number of jobs: "+str(options.jobs) )
   print( "* Calculate unconditional fit in separate job: "+str(options.unconditionalFitInSeparateJob) )
   print( "* This job number: "+str(options.counter) )
   print( "* Processing these grid points: [%d,%d)" % (firstPoint,lastPoint) )
   print( "" )
   print( "" )

   # for later plotting, print some book-keeping info
   print( "# Parameters Of Interest" )
   print( "" )
   for p in range( poiL.getSize() ):
      print( "* POI "+ ("%s=[%d,%f,%f]" % (poiL.at(p).GetName(),poiL.at(p).getBins(),poiL.at(p).getMin(),poiL.at(p).getMax())) )
   print( "" )
   print( "" )

   # unconditional fit
   if (not options.unconditionalFitInSeparateJob) or \
      (options.unconditionalFitInSeparateJob and options.counter == options.jobs):
      for p in range( poiL.getSize() ): poiL.at(p).setConstant(False)
      print( "" )
      print( "--- unconditional fit ---" )
      minimize( nll )
      print( "ucmles -- nll="+str(nll.getVal())+", "+", ".join( [poiL.at(p).GetName()+"="+str(poiL.at(p).getVal()) for p in range(poiL.getSize())] ) )

   # conditional fits
   for p in range( poiL.getSize() ): poiL.at(p).setConstant()
   for i in range( firstPoint,lastPoint ):
      parametersNCube( poiL, i )
      print( "" )
      print( "--- next point: "+str(i)+" ---" )
      print( "Parameters Of Interest: "+str([ poiL.at(p).getVal() for p in range(poiL.getSize()) ]) )
      minimize( nll )
      print( "nll="+str(nll.getVal())+", "+", ".join( [poiL.at(p).GetName()+"="+str(poiL.at(p).getVal()) for p in range(poiL.getSize())] ) )
      


if __name__ == "__main__":
   main()
