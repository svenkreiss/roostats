#!/usr/bin/env python

#  Created on: February 12, 2013

__author__ = "Sven Kreiss, Kyle Cranmer"
__version__ = "0.1"




import optparse

parser = optparse.OptionParser(version="0.1")
parser.add_option("-i", "--inputFiles", help="glob expression for log files from BatchProfileLikelihood.py", type="string", dest="inputFiles", default="batchProfile.log")
parser.add_option("-o", "--outputFile", help="output root file", type="string", dest="outputFile", default="PL_data.root")
parser.add_option(      "--subtractMinNLL", help="subtracts the minNLL", dest="subtractMinNLL", default=False, action="store_true")
parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True, help="Quiet output.")
(options, args) = parser.parse_args()

import ROOT
import PyROOTUtils

import os, math
import glob, re
from array import array

def main():
   files = glob.glob( options.inputFiles )
   print( "Files: "+str(files) )
   
   bestFit = []
   NLL = []
   POIs = []
   for fName in files:
      print( "Opening "+fName )
      f = open( fName )
      for l in f:
         if l[:6] == "* POI ":
            #parAndValue = [(r.split("=")[0],float(r.split("=")[1])) for r in l.split(", ")]
            poiName = l[6:l.find("=")]
            poiConfig = l[l.find("=")+2:-2]
            poiConfig = [ float(p) for p in poiConfig.split(",") ]
            if poiName not in [p[0] for p in POIs]:
               POIs.append( (poiName, poiConfig) )
         if l[:4] == "nll=":
            parAndValue = [(r.split("=")[0],float(r.split("=")[1])) for r in l.split(", ")]
            NLL.append( parAndValue )
         if l[:14] == "ucmles -- nll=":
            parAndValue = [(r.split("=")[0],float(r.split("=")[1])) for r in l.split(", ")]
            bestFit.append( parAndValue )
      f.close()

   print( "\n--- POIs ---" )
   print( POIs )

   print( "\n--- Best fit ---" )
   print( bestFit )

   print( "\n--- NLL ---" )
#    print( "Cleaning NLL" )
#    NLL = [np for np in NLL if not math.isnan(np[0][1]) and not math.isinf(np[0][1])]
   print( NLL )
   minNLL = min( [np[0][1] for np in NLL] )
   maxNLL = max( [np[0][1] for np in NLL] )
   print( "(minNLL,maxNLL) = (%f,%f)" % (minNLL,maxNLL) )

   nllHist = None
   maxHist = maxNLL
   if options.subtractMinNLL: maxHist -= minNLL
   if len( POIs ) == 1:
      poi = POIs[0]
      nllHist = ROOT.TH1D( "profiledNLL", "profiled NLL;"+poi[0]+";NLL", int(poi[1][0]), poi[1][1], poi[1][2] )
      
      # initialize to maxNLL
      for i in range( nllHist.GetNbinsX()+2 ): nllHist.SetBinContent( i, maxHist )
      
   if not nllHist:
      print( "ERROR: Couldn't create nll histogram." )
      return
   
   for n in NLL:
      bin,val = (None,None)
      if len( POIs ) == 1:
         bin = nllHist.FindBin( n[1][1] )
         val = n[0][1]
         
      if options.subtractMinNLL: val -= minNLL
      if nllHist.GetBinContent( bin ) > val: nllHist.SetBinContent( bin, val )

   # create tgraphs
   nllTGraph = None
   twoNllTGraph = None
   lTGraph = None
   if len( POIs ) == 1:
      xNll = []
      xTwoNll = []
      xL = []
      for b in range(nllHist.GetNbinsX()):
         if nllHist.GetBinContent( b+1 ) != maxHist:
            xNll.append( (nllHist.GetBinCenter(b+1), nllHist.GetBinContent(b+1)) )
            xTwoNll.append( (nllHist.GetBinCenter(b+1), 2.0*nllHist.GetBinContent(b+1)) )
            xL.append( (nllHist.GetBinCenter(b+1), math.exp(-nllHist.GetBinContent(b+1))) )
      nllTGraph = PyROOTUtils.Graph( xNll )
      twoNllTGraph = PyROOTUtils.Graph( xTwoNll )
      lTGraph = PyROOTUtils.Graph( xL )


   #bestFitMarker = ROOT.TMarker( bestFit["mH"], bestFit["muHat"], 2 )
      
      
   f = ROOT.TFile( options.outputFile, "RECREATE" )
   nllHist.Write()
   if nllTGraph: nllTGraph.Write( "nllTGraph" )
   if twoNllTGraph: twoNllTGraph.Write( "twoNllTGraph" )
   if lTGraph: lTGraph.Write( "lTGraph" )
   #bestFitMarker.Write("bestFit")
   f.Close()
   
   if options.verbose:
      import helperStyle
      canvas = ROOT.TCanvas( "verboseOutput", "verbose output", 600,300 )
      canvas.Divide( 2 )
      canvas.cd(1)
      nllHist.SetLineWidth( 2 )
      nllHist.SetLineColor( ROOT.kBlue )
      nllHist.Draw("HIST")
      if nllTGraph: 
         nllTGraph.SetLineWidth( 2 )
         nllTGraph.SetLineColor( ROOT.kRed )
         nllTGraph.Draw("SAME")
      canvas.cd(2)
      if lTGraph:
         lTGraph.SetTitle( "profile Likelihood" )
         lTGraph.SetLineWidth( 2 )
         lTGraph.SetLineColor( ROOT.kRed )
         lTGraph.Draw("A,L")
      canvas.SaveAs( "docImages/batchProfileLikelihood1D.png" )
      canvas.Update()
      raw_input( "Press enter to continue ..." )
   

   
   
if __name__ == "__main__":
   main()