from abaqus import *
from abaqusConstants import *
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
import numpy as np

def AbqBox(modelObj,x0,x1,y0,y1,PartName='Part-1'):
    modelObj.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    modelObj.sketches['__profile__'].rectangle(point1=(x0,y0), point2=(x1,y1))
    modelObj.Part(dimensionality=TWO_D_PLANAR, name=PartName, type=DEFORMABLE_BODY)
    modelObj.parts[PartName].BaseShell(sketch= modelObj.sketches['__profile__'])
    del modelObj.sketches['__profile__']
    return modelObj

def AbqCube(modelObj,x0,x1,y0,y1,w,PartName='Part-1'):
    modelObj.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    modelObj.sketches['__profile__'].rectangle(point1=(x0,y0), point2=(x1,y1))
    modelObj.Part(dimensionality=THREE_D, name=PartName, type=DEFORMABLE_BODY)
    modelObj.parts[PartName].BaseSolidExtrude(depth=w, sketch=modelObj.sketches['__profile__'])
    del modelObj.sketches['__profile__']
    return modelObj

def AbqBoxSet(partObj,x0,x1,y0,y1):
    partObj.Set(edges=partObj.edges.findAt(((x0, (y0+y1)/2.0, 0.0), )),name='x0')
    partObj.Set(edges=partObj.edges.findAt(((x1, (y0+y1)/2.0, 0.0), )),name='x1')
    partObj.Set(edges=partObj.edges.findAt((((x0+x1)/2.0, y0, 0.0), )),name='y0')
    partObj.Set(edges=partObj.edges.findAt((((x0+x1)/2.0, y1, 0.0), )),name='y1')
    partObj.Set(name='xy0', vertices=partObj.vertices.findAt(((x0,y0, 0.0), )))
    partObj.Set(faces=partObj.faces.findAt((((x0+x1)/2.0, (y0+y1)/2.0, 0.0), )), name='Box')
    return partObj

def AbqCubeSet(partObj,x0,x1,y0,y1,w):
    partObj.Set(faces=partObj.faces.findAt(((x0, (y0+y1)/2.0, w/2.0), )),name='x0')
    partObj.Set(faces=partObj.faces.findAt(((x1, (y0+y1)/2.0, w/2.0), )),name='x1')
    partObj.Set(faces=partObj.faces.findAt((((x0+x1)/2.0, y0, w/2.0), )),name='y0')
    partObj.Set(faces=partObj.faces.findAt((((x0+x1)/2.0, y1, w/2.0), )),name='y1')
    partObj.Set(faces=partObj.faces.findAt((((x0+x1)/2.0, (y0+y1)/2.0, 0.0), )),name='z0')
    partObj.Set(faces=partObj.faces.findAt((((x0+x1)/2.0, (y0+y1)/2.0, w ), )),name='z1')
    # z coordinate changed from 0 to w
    partObj.Set(edges=partObj.edges.findAt(((x0, 0.0, w), )),name='xz0')
    partObj.Set(edges=partObj.edges.findAt(((x0, y0, w/2.0), )),name='xy0')
    partObj.Set(name='xyz0', vertices=partObj.vertices.findAt(((x0,y0, 0.0), )))
    partObj.Set(cells=partObj.cells.findAt((((x0+x1)/2.0, (y0+y1)/2.0, w/2.0),)), name='Cube')
    partObj.Set(name='corner_node', vertices=partObj.vertices.findAt(((x1,y1, w), )))
    
    return partObj

def AbqBoxMesh(partObj,x0,x1,y0,y1,NelEdge):
    # Seed along edges
    partObj.seedEdgeByNumber(constraint=FINER,edges=partObj.edges.findAt(((x0, (y0+y1)/2.0, 0.0), )), number=NelEdge)
    partObj.seedEdgeByNumber(constraint=FINER,edges=partObj.edges.findAt(((x1, (y0+y1)/2.0, 0.0), )), number=NelEdge)
    partObj.seedEdgeByNumber(constraint=FINER,edges=partObj.edges.findAt((((x0+x1)/2.0, y0, 0.0), )), number=NelEdge)
    partObj.seedEdgeByNumber(constraint=FINER,edges=partObj.edges.findAt((((x0+x1)/2.0, y1, 0.0), )), number=NelEdge)
    # Structured mesh
    partObj.setMeshControls(elemShape=QUAD, regions=partObj.faces.findAt((((x0+x1)/2.0, (y0+y1)/2.0, 0.0), )), technique=STRUCTURED)
    # Element type
    partObj.setElementType(elemTypes=(ElemType(elemCode=CPS4R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT), ElemType(elemCode=CPS3, elemLibrary=STANDARD)), regions=(
        partObj.faces.findAt((((x0+x1)/2.0, (y0+y1)/2.0, 0.0), )), ))
    # Mesh part
    partObj.generateMesh()
    return partObj

def AbqCubeMesh(partObj,x0,x1,y0,y1,w,ElSize):
    # Seed along edges
    partObj.seedPart(deviationFactor=0.1, 
    minSizeFactor=0.1, size=ElSize)
    # Structured mesh
    partObj.setMeshControls(elemShape=QUAD, regions=partObj.cells.findAt((((x0+x1)/2.0, (y0+y1)/2.0, w/2.0), )), technique=STRUCTURED)
    # Element type
    partObj.setElementType(elemTypes=(ElemType(elemCode=C3D20, elemLibrary=STANDARD), ElemType(elemCode=C3D15, 
        elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)), regions=partObj.sets['Cube'])
    # Mesh part
    partObj.generateMesh()
    return partObj

def BCout(Nset,step1,BCstr):
    Ndisp = 0.0
    Nlen = len(Nset.nodes)
    for i in range(Nlen):
        histPointN=HistoryPoint(node=Nset.nodes[i])
        NHistory=step1.getHistoryRegion(point=histPointN)
        Ndisp=Ndisp+np.array(NHistory.historyOutputs[BCstr].data)[:,1]
    return Ndisp

############
def VfCir(x0,x1,y0,y1,cx,cy,cr):
	Amodel=(x1-x0)*(y1-y0)	
	AFibers=0.0
	for i in range(len(cr)):
		AFibers=AFibers + 3.14159265359*pow(cr[i],2)
		VfCir=AFibers/Amodel
	return VfCir
	
