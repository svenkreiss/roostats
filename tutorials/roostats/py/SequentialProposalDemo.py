#!/usr/bin/env python

#  Created on: February 5, 2013

__author__ = "Sven Kreiss, Kyle Cranmer"
__version__ = "0.1"


import optparse
parser = optparse.OptionParser(version="0.1")
parser.add_option("-i", "--input", help="root file", type="string", dest="input", default="results/example_combined_GaussExample_model.root")
parser.add_option("-o", "--output", help="output location", type="string", dest="output", default="docImages/")

parser.add_option("-w", "--wsName", help="Workspace name", type="string", dest="wsName", default="combined")
parser.add_option("-m", "--mcName", help="ModelConfig name", type="string", dest="mcName", default="ModelConfig")
parser.add_option("-d", "--dataName", help="data name", type="string", dest="dataName", default="obsData")

parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True, help="Quiet output.")
options,args = parser.parse_args()


import ROOT
import PyROOTUtils
import math





def main():
   
   ROOT.RooRandom.randomGenerator().SetSeed( 0 )
   
   file = ROOT.TFile.Open(options.input)
   if not file:
      # Normally this would be run on the command line
      print( "will run standard hist2workspace example" )
      ROOT.gROOT.ProcessLine(".! prepareHistFactory .")
      ROOT.gROOT.ProcessLine(".! hist2workspace config/example.xml")
      print( "\n\n---------------------" )
      print( "Done creating example input" )
      print( "---------------------\n\n" )
      file = ROOT.TFile.Open("results/example_combined_GaussExample_model.root")
      
   if not file:
      # if it is still not there, then we can't continue
      print( "Not able to run hist2workspace to create example input" )

  
   # /////////////////////////////////////////////////////////////
   # // Tutorial starts here
   # ////////////////////////////////////////////////////////////
   
   w = file.Get( options.wsName )
   if not w:
      print( "ERROR: Workspace "+options.wsName+" not found." )
      return
   mc = w.obj( options.mcName )
   if not mc:
      print( "ERROR: ModelConfig "+options.mcName+" not found." )
      return
   data = w.data( options.dataName )
   if not data:
      print( "ERROR: Data "+options.dataName+" not found." )
      return


   firstPOI = mc.GetParametersOfInterest().first()
   firstPOI.setMax(10.)


   # this proposal function seems fairly robust
   #SequentialProposal sp(0.1);
   # [#1] INFO:Eval -- Proposal acceptance rate: 20.0123%
   # [#1] INFO:Eval -- Number of steps in chain: 200123
   # 
   # 95% interval on SigXsecOverSM is : [0, 2.15359] 
   #
   # Use factor 10 oversampling on parametersOfInterest
   #SequentialProposal sp(0.1, *mc->GetParametersOfInterest(), 3);
   # Factor 3:
   # [#1] INFO:Eval -- Proposal acceptance rate: 18.0398%
   # [#1] INFO:Eval -- Number of steps in chain: 180398
   # 
   # 95% interval on SigXsecOverSM is : [0, 2.15503] 
   #SequentialProposal sp(10, *mc->GetParametersOfInterest(), 3);
   
   # We want to create an overview using the following proposal functions
   proposalFunctions = [
      { "proposal": ROOT.RooStats.SequentialProposal(10, mc.GetParametersOfInterest(), 3), 
        "id"      : "SequentialProposal_10_03",
        "title"   : "Divisor = 10, Oversampling of POI = 3" }
   ]
   
   
   mcmc = ROOT.RooStats.MCMCCalculator(data,mc)
   mcmc.SetConfidenceLevel(0.95) # 95% interval
   #mcmc.SetProposalFunction(sp)
   mcmc.SetNumIters(10000)         # Metropolis-Hastings algorithm iterations
   mcmc.SetNumBurnInSteps(2000)     # first N steps to be ignored as burn-in

   # default is the shortest interval.  here use central
   mcmc.SetLeftSideTailFraction(0); # for one-sided Bayesian interval

   for pF in proposalFunctions:
      mcmc.SetProposalFunction( pF["proposal"] )
      interval = mcmc.GetInterval()

      # print out the iterval on the first Parameter of Interest
      print( "\n95%% interval on %s is [%f,%f]" % (
         firstPOI.GetName(),
         interval.LowerLimit(firstPOI),
         interval.UpperLimit(firstPOI)
      ) )

      c1 = ROOT.TCanvas(pF["id"]+"_intervalPlot")
      plot = ROOT.RooStats.MCMCIntervalPlot(interval)
      plot.Draw()
      c1.SaveAs( options.output+pF["id"]+"_interval.jpg" )
      
      c2 = ROOT.TCanvas(pF["id"]+"_extraPlots", pF["id"]+"_extraPlots", 1200, 800)
      list = ROOT.RooArgList( mc.GetNuisanceParameters() )
      if list.getSize() > 1:
         ny = ROOT.TMath.CeilNint( math.sqrt(list.getSize()) )
         nx = ROOT.TMath.CeilNint( float(list.getSize())/ny )
         c2.Divide( nx,ny )
      # draw a scatter plot of chain results for poi vs each nuisance parameters
      for i in range( list.getSize() ):
         c2.cd(i+1)
         plot.DrawChainScatter( firstPOI, list.at(i) )
      c2.SaveAs( options.output+pF["id"]+"_extras.jpg" )


if __name__ == "__main__":
   main()
