// @(#)root/roostats:$Id$
// Author: Sven Kreiss, Kyle Cranmer
/*************************************************************************
 * Copyright (C) 1995-2008, Rene Brun and Fons Rademakers.               *
 * All rights reserved.                                                  *
 *                                                                       *
 * For the licensing terms see $ROOTSYS/LICENSE.                         *
 * For the list of contributors see $ROOTSYS/README/CREDITS.             *
 *************************************************************************/

#ifndef ROOSTATS_MINFINDER
#define ROOSTATS_MINFINDER

#ifndef ROOT_Math_MinimizerOptions
#include "Math/MinimizerOptions.h"
#endif


#include <sstream>
#include <vector>
#include <string>
#include "RooAbsReal.h"
#include "RooRealVar.h"


namespace RooStats {

   class MinFinder {
   public:
      virtual ~MinFinder() {}
      
      virtual void Minimize( RooAbsReal& f ) = 0;
      static MinFinder* defaultMinFinder;
      
   protected:
      ClassDef(MinFinder,1);  // Class for minimization
   };
   


   class MinFinderStandard : public MinFinder {
   public:
      MinFinderStandard() :
         fMinimizer( ::ROOT::Math::MinimizerOptions::DefaultMinimizerType().c_str() ),
         fAlgorithm( ::ROOT::Math::MinimizerOptions::DefaultMinimizerAlgo() ),
         fStrategy( ::ROOT::Math::MinimizerOptions::DefaultStrategy() ),
         fTolerance( TMath::Max(1.,::ROOT::Math::MinimizerOptions::DefaultTolerance()) ),
         fOptimizeConst( 2 ),
         fPrintLevel( ::ROOT::Math::MinimizerOptions::DefaultPrintLevel() )
      {
      }
      virtual ~MinFinderStandard() {}
   
      virtual void Minimize( RooAbsReal& f );
      
      virtual void Minimizer( const char* m ){ fMinimizer = m; }
      virtual void Algorithm( const char* a ){ fAlgorithm = a; }
      virtual void Strategy( int s ){ fStrategy = s; }
      virtual void Tolerance( double t ){ fTolerance = t; }
      virtual void OptimizeConst( int oc ){ fOptimizeConst = oc; }
      virtual void PrintLevel( int pl ){ fPrintLevel = pl; }

   protected:
      std::string fMinimizer;
      std::string fAlgorithm;
      int fStrategy;
      double fTolerance; 
      int fOptimizeConst;
      int fPrintLevel;

   protected:
      ClassDef(MinFinderStandard,1);  // Class for minimization
   };



   
   class MinFinderScan : public MinFinderStandard {
   public:   
      MinFinderScan() :
         MinFinderStandard(),
         
         fScanLimit( 0.0 )
      {
      }
      virtual ~MinFinderScan() {}

      virtual void Minimize( RooAbsReal& f );

      void AddScanVar( RooRealVar* v ){ fScanVars.push_back(v); }
      void ScanLimit( double l ){ fScanLimit = l; }
   private:
      std::vector<RooRealVar*> fScanVars;
      double fScanLimit;
   protected:
      ClassDef(MinFinderScan,1);  // Class for minimization
   };

}

#endif