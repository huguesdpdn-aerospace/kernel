//  SALOME SALOMEDS : data structure of SALOME and sources of Salome data server 
//
//  Copyright (C) 2003  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
//  CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS 
// 
//  This library is free software; you can redistribute it and/or 
//  modify it under the terms of the GNU Lesser General Public 
//  License as published by the Free Software Foundation; either 
//  version 2.1 of the License. 
// 
//  This library is distributed in the hope that it will be useful, 
//  but WITHOUT ANY WARRANTY; without even the implied warranty of 
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
//  Lesser General Public License for more details. 
// 
//  You should have received a copy of the GNU Lesser General Public 
//  License along with this library; if not, write to the Free Software 
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA 
// 
//  See http://www.opencascade.org/SALOME/ or email : webmaster.salome@opencascade.org 
//
//
//
//  File   : SALOMEDS_AttributeSequenceOfSequenceOfReal_i.hxx
//  Author : Yves FRICAUD
//  Module : SALOME
//  $Header$

#ifndef SALOMEDS_AttributeSequenceOfSequenceOfReal_i_HeaderFile
#define SALOMEDS_AttributeSequenceOfSequenceOfReal_i_HeaderFile

// IDL headers
#include "SALOMEDS_SequenceOfRealAttribute.hxx"
#include <SALOMEconfig.h>
#include CORBA_SERVER_HEADER(SALOMEDS_Attributes)
#include "SALOMEDS_GenericAttribute_i.hxx"

class SALOMEDS_AttributeSequenceOfReal_i: public virtual POA_SALOMEDS::AttributeSequenceOfReal,
					  public virtual SALOMEDS_GenericAttribute_i {
public:
  
  SALOMEDS_AttributeSequenceOfReal_i(const Handle(SALOMEDS_SequenceOfRealAttribute)& theSequenceOfRealAttr, 
				     CORBA::ORB_ptr orb) 
  {
    _myOrb = CORBA::ORB::_duplicate(orb);
    _myAttr = theSequenceOfRealAttr;
  };
  ~SALOMEDS_AttributeSequenceOfReal_i() {};

  void Assign(const SALOMEDS::DoubleSeq& other);
  SALOMEDS::DoubleSeq* CorbaSequence();
  void Add(CORBA::Double value);
  void Remove(CORBA::Long index);
  void ChangeValue(CORBA::Long index, CORBA::Double value);
  CORBA::Double Value(CORBA::Short index);
  CORBA::Long Length();

  char* Store();
  void Restore(const char*);
};



#endif
