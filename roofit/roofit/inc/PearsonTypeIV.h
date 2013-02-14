/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef PEARSONTYPEIV
#define PEARSONTYPEIV

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class PearsonTypeIV : public RooAbsPdf {
public:
  PearsonTypeIV() {} ; 
  PearsonTypeIV(const char *name, const char *title,
	      RooAbsReal& _x,
	      RooAbsReal& _m,
	      RooAbsReal& _nu,
	      RooAbsReal& _a,
	      RooAbsReal& _lambda);
  PearsonTypeIV(const PearsonTypeIV& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new PearsonTypeIV(*this,newname); }
  inline virtual ~PearsonTypeIV() { }

protected:

  RooRealProxy x ;
  RooRealProxy m ;
  RooRealProxy nu ;
  RooRealProxy a ;
  RooRealProxy lambda ;
  
  Double_t evaluate() const ;

private:

  ClassDef(PearsonTypeIV,1) // Your description goes here...
};
 
#endif
