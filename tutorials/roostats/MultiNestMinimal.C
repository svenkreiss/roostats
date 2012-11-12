/*
 * minimal.C
 *
 *  Created on: Nov 4, 2009
 *      Author: Sven Kreiss, Kyle Cranmer
 */

#include "RooWorkspace.h"

#include "RooStats/MultiNestCalculator.h"

using namespace RooStats;

void MultiNestMinimal(void) {

   RooWorkspace w;
   w.factory( "RooGaussian::g(x[-10,10],m[-10,10],s[2])" );
   w.defineSet( "poi", "m" );
   w.defineSet( "obs", "x" );
   
   RooDataSet data( "data", "data", *w.set("obs") );
   data.add( *w.set("obs") );
   

   MultiNestCalculator m;
   m.SetData( data );
   m.SetPdf( *w.pdf("g") );
   m.SetParametersOfInterest( *w.set("poi") );
   MultiNestInterval* interval = m.GetInterval();
   cout << "interval = [" << interval->LowerLimit(*w.var("m")) << ", " << interval->UpperLimit(*w.var("m")) << "]" << endl;
   
}

