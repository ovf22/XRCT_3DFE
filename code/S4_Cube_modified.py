########################################################
## Run without GUI with following command 
#     abaqus cae noGUI=AbaRun.py
#########################################################

## Default ABAQUS inputs
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *


## Model in names
ModelCase='InputModelCase'
NameCAE=ModelCase+'_CubeModel.cae'
NameModelin=ModelCase+'_CubeModel'
NameModel='Out-'+ModelCase
freq = 10
## Other run parameters
Ncpus=16
UserRoutine=ModelCase+'_orient.f'

## Import model from other cae-file
mdb.openAuxMdb(pathName=NameCAE)
mdb.copyAuxMdbModel(fromName=NameModelin, toName=NameModel)
mdb.closeAuxMdb()

## Delete default model
del mdb.models['Model-1']

mdb.models[NameModel].fieldOutputRequests['F-Output-1'].setValues(frequency=freq)

mdb.saveAs(pathName=NameModel+'.cae') 

## Generate job
modelJob=mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
	explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
	memory=90, memoryUnits=PERCENTAGE, model=NameModel, modelPrint=OFF, 
	multiprocessingMode=MPI, name=NameModel, nodalOutputPrecision=SINGLE, 
	numCpus=Ncpus, numDomains=Ncpus, numGPUs=0, queue=None, scratch='',
    type=ANALYSIS, userSubroutine=UserRoutine, waitHours=0, waitMinutes=0)

## The following lines submit the job, and wait for completion before continue
modelJob.submit(consistencyChecking=OFF)
modelJob.waitForCompletion()
	
## Eventually Post-processing
# Function Definition
import numpy as np
from odbAccess import *
from abaqusConstants import *

def BCout(Nset,step1,BCstr):
    Ndisp = 0.0
    Nlen = len(Nset.nodes)
    for i in range(Nlen):
        histPointN=HistoryPoint(node=Nset.nodes[i])
        NHistory=step1.getHistoryRegion(point=histPointN)
        Ndisp=Ndisp+np.array(NHistory.historyOutputs[BCstr].data)[:,1]
    return Ndisp

################# Postprocessing ODB ##########################
odbObj = session.openOdb(name=NameModel+'.odb', readOnly=False)
step1 = odbObj.steps['Step-1']
vps = session.viewports['Viewport: 1'] 
vps.setValues(displayedObject=odbObj)

### Calculate u1 and rf1 along x1 and from this the Emod
x1set = odbObj.rootAssembly.instances['PART-1-1'].nodeSets['X1']
x1len = len(x1set.nodes)
x1U1=BCout(x1set,step1,BCstr='U1')/x1len
x1RF1=BCout(x1set,step1,BCstr='RF1')

### Save full history output
histData = np.vstack((x1U1,x1RF1)).T
np.savetxt(NameModel+'_load-disp.out',histData)

### Save Field output
session.writeFieldReport(fileName=NameModel+'_S_local.out', append=ON, 
    sortItem='Element Label', odb=odbObj, step=0, frame=vps.odbDisplay.fieldFrame[-1], 
    outputPosition=INTEGRATION_POINT, variable=(('S', INTEGRATION_POINT, ((
    COMPONENT, 'S11'), (COMPONENT, 'S22'), (COMPONENT, 'S12'), )), ), 
    stepFrame=SPECIFY)

scratchOdb = session.ScratchOdb(odbObj)
scratchOdb.rootAssembly.DatumCsysByThreePoints(name='CSYS-1', 
    coordSysType=CARTESIAN, origin=(0.0, 0.0, 0.0), point1=(1.0, 0.0, 0.0), 
    point2=(0.0, 1.0, 0.0))
dtm = scratchOdb.rootAssembly.datumCsyses['CSYS-1']
session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(
    transformationType=USER_SPECIFIED, datumCsys=dtm)

session.writeFieldReport(fileName=NameModel+'_S_global.out', append=ON, 
    sortItem='Element Label', odb=odbObj, step=0, frame=vps.odbDisplay.fieldFrame[-1], 
    outputPosition=INTEGRATION_POINT, variable=(('S', INTEGRATION_POINT, ((
    COMPONENT, 'S11'), (COMPONENT, 'S22'), (COMPONENT, 'S12'), )), ), 
    stepFrame=SPECIFY)
    
odbObj.save()