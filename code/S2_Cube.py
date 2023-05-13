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
########################################################
import numpy as np
import M3_AbqFunctions as M3AF   
########################################################

### Parameters
### Load parameters from Tomogram
sample_name = 'shell_sample_name'
dim = np.loadtxt(sample_name+'_TomoDim.txt')
LENGTH = dim[0]*1e-3
THICKNESS = dim[1]*1e-3
WIDTH = dim[2]*1e-3
ElemSize = 70*1e-3

NameModel = sample_name+'_CubeModel'
JobName = 'Job-'+NameModel
x0 = -LENGTH/2.0; x1 = LENGTH/2.0; y0 = -THICKNESS/2.0 ; y1 = THICKNESS/2.0
Disp = 0.01

########################################################
### Define Model Object
modelObj = mdb.Model(name=NameModel)
### Square box part
modelObj=M3AF.AbqCube(modelObj, x0, x1, y0, y1, WIDTH)
### Delete obselete Model-1
del mdb.models['Model-1']
### Define set-names
partObj=modelObj.parts['Part-1']
partObj=M3AF.AbqCubeSet(partObj, x0, x1, y0, y1, WIDTH)

### Material Definition
E11, E22, E33 = 134353, 15062, 15062
nu12, nu13, nu23 = 0.313, 0.313, 0.4
G12, G13, G23 = 2555, 2555, 3617

modelObj.Material(name='Material-1')
modelObj.materials['Material-1'].Elastic(table=((E11, E22, 
    E33, nu12, nu13, nu23, G12, G13, G23), ), type=ENGINEERING_CONSTANTS)

### Section
modelObj.HomogeneousSolidSection(material='Material-1', name='Section-1')
### Section assignment
partObj.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, 
                          region=partObj.sets['Cube'], sectionName='Section-1',
                          thicknessAssignment=FROM_SECTION)
### Material Orientation
partObj.MaterialOrientation(additionalRotationType=ROTATION_NONE, fieldName='', 
                            localCsys=None, orientationType=USER, 
                            region=partObj.sets['Cube'], stackDirection=STACK_3)
### Meshing
partObj=M3AF.AbqCubeMesh(partObj, x0, x1, y0, y1, WIDTH, ElemSize)
### Assemply
modelObj.rootAssembly.DatumCsysByDefault(CARTESIAN)
modelObj.rootAssembly.Instance(dependent=ON, name='Part-1-1',part=partObj)
modelObj.rootAssembly.translate(instanceList=('Part-1-1', ),
                                vector=(0.0, 0.0, -WIDTH/2.0))
### Step definition
instanceObj=modelObj.rootAssembly.instances['Part-1-1']

modelObj.StaticStep(initialInc=0.01, maxInc=0.01, 
                    name='Step-1',previous='Initial')
### BC
modelObj.DisplacementBC(amplitude=UNSET, createStepName='Initial', 
	distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-1', 
    region=instanceObj.sets['x0'], u1=SET, u2=UNSET, u3=UNSET,
    ur1=UNSET, ur2=UNSET, ur3=UNSET)
modelObj.DisplacementBC(amplitude=UNSET, createStepName='Initial', 
	distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-2', 
    region=instanceObj.sets['xz0'], u1=UNSET, u2=UNSET, u3=SET,
    ur1=UNSET, ur2=UNSET, ur3=UNSET)
modelObj.DisplacementBC(amplitude=UNSET, createStepName='Initial', 
	distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-3', 
    region=instanceObj.sets['xy0'], u1=UNSET, u2=SET, u3=UNSET,
    ur1=UNSET, ur2=UNSET, ur3=UNSET)

modelObj.DisplacementBC(amplitude=UNSET, createStepName='Step-1', 
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-5', 
	region=instanceObj.sets['x1'], u1=Disp, u2=UNSET, u3=UNSET,
    ur1=UNSET, ur2=UNSET, ur3=UNSET)

### Field Output
modelObj.FieldOutputRequest(createStepName='Step-1', name=
    'F-Output-1', variables=('S', 'U'))

### History output
modelObj.HistoryOutputRequest(createStepName='Step-1', name=
    'H-Output-1', rebar=EXCLUDE, region=instanceObj.sets['x1'], 
    sectionPoints=DEFAULT, variables=('RF1', 'U1'))
    
##################### Job definition ###########################
mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
	explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
	memory=90, memoryUnits=PERCENTAGE, model=NameModel, modelPrint=OFF, 
	multiprocessingMode=MPI, name=NameModel, nodalOutputPrecision=SINGLE, 
	numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
	ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
######################## Save the CAE file #######################

mdb.jobs[NameModel].writeInput(consistencyChecking=OFF) 
mdb.saveAs(pathName=NameModel+'.cae')

with open(NameModel + '.inp') as f:
    lines = f.readlines()

def find_line(lines, word):
    for line in lines:
        if line.find(word) !=-1:
            return lines.index(line)

W_START = '*Part, name=Part-1'
I_START = find_line(lines, W_START) + 1
W_END = '*Orientation, name=Ori-1, system=user'
I_END = find_line(lines, W_END)

new_lines = lines[I_START : I_END]
new_lines.append('** Section: Section-1\n')
new_lines.append('*Solid Section, elset=Cube, material=Default MATERIAL\n')
new_lines.append(',\n')

with open(sample_name+'_IP1.inp', 'w') as f:
    for line in new_lines:
        f.write(line)
    f.close()
    
IP2 = sample_name+'_IP2'
JOB1 = mdb.JobFromInputFile(name=IP2, inputFileName=IP2+'.inp')
JOB1.submit()
JOB1.waitForCompletion()
