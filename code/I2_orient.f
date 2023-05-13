**********************************************************************************************
**                                 USER SUBROUTINE ORIENT                                   **
**********************************************************************************************

      SUBROUTINE ORIENT(T,NOEL,NPT,LAYER,KSPT,COORDS,BASIS,
     1 ORNAME,NNODES,CNODES,JNNUM)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 ORNAME
      CHARACTER*256	 JOBNAME, OUTDIR, FILENAME
C
      DIMENSION T(3,3),COORDS(3),BASIS(3,3),CNODES(3,NNODES)
      DIMENSION JNNUM(NNODES)

C       INCLUDE 'InputOrientFortran.f'
      INCLUDE 'InputOrientFortran1.f'
      INCLUDE 'InputOrientFortran2.f'
      
      T(1,1) =  DCOS(PHI0(NPT,NOEL))
      T(1,2) = -DSIN(PHI0(NPT,NOEL))
      T(1,3) =  0.
      T(2,1) =  DCOS(THETA0(NPT,NOEL))*DSIN(PHI0(NPT,NOEL))
      T(2,2) =  DCOS(THETA0(NPT,NOEL))*DCOS(PHI0(NPT,NOEL))
      T(2,3) = -DSIN(THETA0(NPT,NOEL))
      T(3,1) =  DSIN(THETA0(NPT,NOEL))*DSIN(PHI0(NPT,NOEL))
      T(3,2) =  DSIN(THETA0(NPT,NOEL))*DCOS(PHI0(NPT,NOEL))
      T(3,3) =  DCOS(THETA0(NPT,NOEL))

      RETURN
      END    