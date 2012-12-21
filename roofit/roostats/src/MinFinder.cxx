// @(#)root/roostats:$Id$
// Authors: Sven Kreiss, Kyle Cranmer
/*************************************************************************
 * Copyright (C) 1995-2008, Rene Brun and Fons Rademakers.               *
 * All rights reserved.                                                  *
 *                                                                       *
 * For the licensing terms see $ROOTSYS/LICENSE.                         *
 * For the list of contributors see $ROOTSYS/README/CREDITS.             *
 *************************************************************************/

#include "RooStats/MinFinder.h"
#include "RooStats/RooStatsUtils.h"
#include "RooMinimizer.h"


ClassImp(RooStats::MinFinder);

using namespace RooFit;
using namespace RooStats;
using namespace std;


MinFinder* MinFinder::defaultMinFinder = new MinFinderStandard;


void MinFinderStandard::Minimize( RooAbsReal& f ) {
   // f can be your nll
   
   RooMinimizer minim(f);
   minim.setStrategy(fStrategy);
   //LM: RooMinimizer.setPrintLevel has +1 offset - so subtruct  here -1 + an extra -1 
   int level = (fPrintLevel == 0) ? -1 : fPrintLevel -2;
   minim.setPrintLevel(level);
   minim.setEps(fTolerance);
   // this cayses a memory leak
   minim.optimizeConst( fOptimizeConst ); 
   TString minimizer = fMinimizer;
   TString algorithm = fAlgorithm;
   //if (algorithm == "Migrad") algorithm = "Minimize"; // prefer to use Minimize instead of Migrad
   int status;


   for (int tries = 1, maxtries = 4; tries <= maxtries; ++tries) {
      status = minim.minimize(minimizer,algorithm);
      if (status%1000 == 0) {  // ignore erros from Improve 
         break;
      } else if (tries < maxtries) {
         cout << "    ----> Doing a re-scan first" << endl;
         minim.minimize(minimizer,"Scan");
         if (tries == 2) {
            if (fStrategy == 0 ) { 
               cout << "    ----> trying with strategy = 1" << endl;;
               minim.setStrategy(1);
            }
            else 
               tries++; // skip this trial if stratehy is already 1 
         }
         if (tries == 3) {
            cout << "    ----> trying with improve" << endl;;
            minimizer = "Minuit";
            algorithm = "migradimproved";
         }
      }
   }
   
   //how to get cov quality faster?
   //return minim.save();
   return;
   //minim.optimizeConst(false);    
}


void MinFinderScan::Minimize( RooAbsReal& f ) {

   vector<double> minF;
   vector<const RooAbsCollection*> minConfig;
   
   RooArgSet* vars = f.getVariables();
   RemoveConstantParameters( vars );
   
   // "kick"
   ((RooRealVar*)vars->first())->setVal( ((RooRealVar*)vars->first())->getVal() + 0.01 );
   
   MinFinderStandard::Minimize( f );
   minF.push_back( f.getVal() );
   minConfig.push_back( vars->snapshot() );
   
   for( unsigned int i=0; i < fScanVars.size(); i++ ) {
      // in the PLTS conditional fit with the POI also being in this list of scanvars:
      //   do not scan while this variable is set constant.
      if( fScanVars[i]->isConstant() ) continue;
      
      double center = fScanVars[ i ]->getVal();
      
      // search up
      for( unsigned int j=1; j < 20; j++ ) {
         *vars = *(RooArgSet*)minConfig[0];

         double x = center + j*(fScanVars[ i ]->getMax() - center)/20.0;
         fScanVars[ i ]->setVal( x );
         
         MinFinderStandard::Minimize( f );
         minF.push_back( f.getVal() );
         minConfig.push_back( vars->snapshot() );      
         if( fPrintLevel >= 10 ) cout << "Scanning "<<fScanVars[i]->GetName()<<" for min at "<<x<<": Deltaf="<<f.getVal()-minF[0]<< endl;

         if( fScanLimit  &&  f.getVal() > minF[0]+fScanLimit ) break;     
      }
      if( fPrintLevel >= 10 ) cout << endl;
      // search down
      for( unsigned int j=1; j < 20; j++ ) {
         *vars = *(RooArgSet*)minConfig[0];

         double x = center - j*(center - fScanVars[ i ]->getMin())/20.0;
         fScanVars[ i ]->setVal( x );
         
         MinFinderStandard::Minimize( f );
         minF.push_back( f.getVal() );
         minConfig.push_back( vars->snapshot() );
         if( fPrintLevel >= 10 ) cout << "Scanning "<<fScanVars[i]->GetName()<<" for min at "<<x<<": Deltaf="<<f.getVal()-minF[0]<< endl;
         
         if( fScanLimit  &&  f.getVal() > minF[0]+fScanLimit ) break;     
      }
      if( fPrintLevel >= 10 ) cout << endl;
      
      // restore variables
      *vars = *(RooArgSet*)minConfig[0];
   }
   
   
   // find min of mins
   double finalMinF = minF[0];
   const RooAbsCollection* finalMinConfig = minConfig[0];
   for( unsigned int i=1; i < minF.size(); i++ ) {
      if( minF[i] >= finalMinF ) continue;
      
      finalMinF = minF[i];
      finalMinConfig = minConfig[i];
   }

   // apply   
   *vars = *(RooArgSet*)finalMinConfig;
   delete vars;

   // cleanup
   for( unsigned int i=1; i < minConfig.size(); i++ ) delete minConfig[i];   
}
