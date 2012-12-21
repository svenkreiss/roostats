#!/usr/bin/env python

#  StandardFrequentistTestTwoSided
# 
#  date: Nov 1, 2012
# 
#  This is a standard demo that can be used with any ROOT file
#  prepared in the standard way.  You specify:
#  - name for input ROOT file
#  - name of workspace inside ROOT file that holds model and data
#  - name of ModelConfig that specifies details for calculator tools
#  - name of dataset

__author__ = "Sven Kreiss, Kyle Cranmer"
__version__ = "0.1"



import optparse

parser = optparse.OptionParser(version="0.1")
parser.add_option("-i", "--inputFile", help="root file", type="string", dest="fileName", default="")
parser.add_option("-w", "--wsName", help="ws name", type="string", dest="wsName", default="combined")
parser.add_option("-m", "--mcName", help="mc name", type="string", dest="mcName", default="ModelConfig")
parser.add_option("-d", "--dataName", help="data name", type="string", dest="dataName", default="obsData")
parser.add_option("-n", "--nToys", help="number of toys", type="int", dest="nToys", default=1)
parser.add_option(      "--overwritePOI", help="Force to take comma separated list of parameters with value for poi. Example: \"mu=1,mH=125\" will make these two the poi.", dest="overwritePOI", default=False )
parser.add_option(      "--overwriteRange", help="Overwrite range. Example: \"mu=[-5:10],mH=[120:130]\".", dest="overwriteRange", default=False )
parser.add_option(      "--proof", help="enable parallel proof processing: use \"\" for local proof-lite", dest="proof", default=None )
parser.add_option(      "--detailedOutput", help="enable detailed output", dest="detailedOutput", default=False, action="store_true" )
parser.add_option(      "--addSimpleLikelihoodRatioTestStat", help="add SLRTS with defined POIs for the alt hypothesis. Example: \"mu=1,mH=126\"", dest="addSimpleLikelihoodRatioTestStat", default=False )


parser.add_option("-o", "--output", dest="output", type="string", default="standard_frequentist_toys.root")
parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=True, 
                  help="Quiet output.")
(options, args) = parser.parse_args()


import ROOT
import math



def main():
   ROOT.RooRandom.randomGenerator().SetSeed( 0 )


   f = ROOT.TFile.Open( options.fileName )
   w = f.Get( options.wsName )
   mc = w.obj( options.mcName )
   data = w.data( options.dataName )
   
   #ROOT.RooAbsReal.defaultIntegratorConfig().method1D().setLabel("RooAdaptiveGaussKronrodIntegrator1D")
   ROOT.Math.MinimizerOptions.SetDefaultMinimizer("Minuit2")
   #ROOT.RooMinimizer.SetMaxFunctionCalls(10000)
   #ROOT.Math.MinimizerOptions.SetDefaultStrategy( 0 )

   mf = ROOT.RooStats.MinFinderScan()
   #mf.AddScanVar( w.var("mu") )
   mf.AddScanVar( w.var("mH") )
   #mf.AddScanVar( w.var("ess") )
   mf.ScanLimit( 2.0 )
   mf.OptimizeConst( 0 )
   ROOT.RooStats.MinFinder.defaultMinFinder = mf

   if options.overwriteRange:
      parAndRange = options.overwriteRange.split(",")
      for pr in parAndRange:
         p,r = pr.split("=")
         r = r.split(":")
         rMin = float( r[0][1:] )
         rMax = float( r[1][:-1] )
         
         print( "Setting range for "+p+"=["+str(rMin)+","+str(rMax)+"]" )
         w.var( p ).setRange( rMin, rMax )

   if options.overwritePOI:
      print( "" )
      print( "=== Using given set for POI ===" )
      poiAndValue = {}
      pvs = options.overwritePOI.split(",")
      for pv in pvs:
         name,value = pv.split("=")
         poiAndValue[ name ] = float( value )
      
      remove = []
      poiL = ROOT.RooArgList( mc.GetParametersOfInterest() )
      for p in range( poiL.getSize() ):
         name = poiL.at(p).GetName()
         if name not in poiAndValue.keys():
            print( "Adding "+name+"["+str(poiL.at(p).getMin())+","+str(poiL.at(p).getMax())+"] to nuisance parameters." )
            w.set( mc.GetName()+"_NuisParams" ).add( poiL.at(p) )
            remove.append( name )
#          else:
#             print( "Setting value of POI "+name+"="+str(poiAndValue[name])+"." )

      for r in remove: poiL.remove( w.var(r) )
            
      for p,v in poiAndValue.iteritems():
         if not poiL.contains( w.var(p) ):
            print( "Adding "+p+"="+str(v)+" to POI." )
            poiL.add( w.var(p) )
            w.var(p).setVal( v )
         else:
            print( "Setting value of POI "+p+"="+str(v)+"." )
            w.var(p).setVal( v )
            
      print( "Setting new POI and new snapshot for ModelConfig: " )
      mc.SetParametersOfInterest( ROOT.RooArgSet(poiL) )
      mc.SetSnapshot( ROOT.RooArgSet(poiL) )
      mc.GetSnapshot().Print("V")
      print( "" )
      print( "" )
      
      
   

   poiL = ROOT.RooArgList( mc.GetParametersOfInterest() )


   # ----------------------------------------------------
   # Configure a ProfileLikelihoodTestStat to use with ToyMCSampler
   plts = ROOT.RooStats.ProfileLikelihoodTestStat( mc.GetPdf() )
   #plts.SetOneSidedDiscovery( True )
   plts.SetVarName( "q_{"  +  ",".join([poiL.at(p).GetName()+"="+str(poiL.at(p).getVal()) for p in range( poiL.getSize() )])  +  "}/2" )
   if options.detailedOutput: plts.EnableDetailedOutput( True )
   
   slrts = None
   if options.addSimpleLikelihoodRatioTestStat:
      
      # prepare mcAlt first
      mcAlt = mc.Clone( "ModelConfigAlt" )
      print( "" )
      print( "=== Creating mcAlt ===" )
      pvs = options.addSimpleLikelihoodRatioTestStat.split(",")
      for pv in pvs:
         name,value = pv.split("=")
         print( "Setting "+name+"="+value+"." )
         w.var( name ).setVal( float(value) )
      mcAlt.SetSnapshot( mcAlt.GetParametersOfInterest() )
      mcAlt.Print()
   
      slrts = ROOT.RooStats.SimpleLikelihoodRatioTestStat( mc.GetPdf(), mc.GetPdf() )
      slrts.SetNullParameters( mc.GetSnapshot() )
      slrts.SetAltParameters( mcAlt.GetSnapshot() )
      if options.detailedOutput: slrts.EnableDetailedOutput( True )
      
   
   # ----------------------------------------------------
   # configure the ToyMCSampler
   toymcs = ROOT.RooStats.ToyMCSampler(plts, 50)
   if slrts: toymcs.AddTestStatistic( slrts )

   #    // Since this tool needs to throw toy MC the PDF needs to be
   #    // extended or the tool needs to know how many entries in a dataset
   #    // per pseudo experiment.
   #    // In the 'number counting form' where the entries in the dataset
   #    // are counts, and not values of discriminating variables, the
   #    // datasets typically only have one entry and the PDF is not
   #    // extended.
   if not mc.GetPdf().canBeExtended():
      if data.numEntries() == 1:
         toymcs.SetNEventsPerToy(1)
      else:
         print( "Not sure what to do about this model" )

   #    // We can use PROOF to speed things along in parallel
   #    // ProofConfig pc(*w, 2, "user@yourfavoriteproofcluster", false);
   if options.proof:
      pc = ROOT.RooStats.ProofConfig(w, 2, options.proof, False)
      toymcs.SetProofConfig(pc)    # enable proof


   # instantiate the calculator
   freqCalc = ROOT.RooStats.FrequentistCalculator(data, mc, mc, toymcs)
   freqCalc.SetToys( options.nToys,0 ) # null toys, alt toys

   # Run the calculator and print result
   freqCalcResult = freqCalc.GetHypoTest()
   freqCalcResult.GetNullDistribution().SetTitle( "toys" )
   #freqCalcResult->GetAltDistribution()->SetTitle( "s+b" )
   freqCalcResult.Print()
   pvalue = freqCalcResult.NullPValue()
   
   ows = ROOT.RooWorkspace( "ToysOutput" )
   getattr(ows,"import")( freqCalcResult )
   print( "Writing file: "+options.output )
   ows.writeToFile( options.output, True )
   

   # plot
   c1 = ROOT.TCanvas()
   plot = ROOT.RooStats.HypoTestPlot(freqCalcResult, 60, -0.49, 2.51 )
   plot.SetLogYaxis(True)
   
   # add chi2 to plot
#    nPOI = 1
#    f = ROOT.TF1("f", "1*ROOT::Math::chisquared_pdf(2*x,%d,0)" % nPOI, 0,20)
#    f.SetLineColor( ROOT.kBlack )
#    f.SetLineStyle( 7 )
#    plot.AddTF1( f, "#chi^{2}(2x,%d), \"half-chisquared\"" % nPOI );

   # add chi2 to plot
   nPOI = 1
   fTwoSided = ROOT.TF1("fTwoSided", "2*ROOT::Math::chisquared_pdf(2*x,%d,0)" % nPOI, 0,20)
   fTwoSided.SetLineColor( ROOT.kBlack )
   fTwoSided.SetLineStyle( 2 )
   plot.AddTF1( fTwoSided, "2#chi^{2}(2x,%d), \"chisquared\"" % nPOI );
   
   print( "Asymptotic obs significance = "+str(math.sqrt(2.0*freqCalcResult.GetTestStatisticData())) )
   print( "Two-sided obs toy significance = "+str(ROOT.RooStats.PValueToSignificance( pvalue/2 )) )

   print( "InverseCDF( 0.68 ) = "+str(freqCalcResult.GetNullDistribution().InverseCDF(0.68)) )
   print( "InverseCDF( 0.84 ) = "+str(freqCalcResult.GetNullDistribution().InverseCDF(0.84)) )
   print( "InverseCDF( 0.90 ) = "+str(freqCalcResult.GetNullDistribution().InverseCDF(0.90)) )
   print( "InverseCDF( 0.95 ) = "+str(freqCalcResult.GetNullDistribution().InverseCDF(0.95)) )
   print( "InverseCDF( 0.997 ) = "+str(freqCalcResult.GetNullDistribution().InverseCDF(0.997)) )
   
   
   plot.Draw()
   c1.SaveAs(options.output.replace(".root",".eps"))
   

   return pvalue


if __name__ == "__main__":
   main()

