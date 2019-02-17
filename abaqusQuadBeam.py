#=============================================================================
# Script to solve for a quadrilateral beam balanced on three T-beams.
#=============================================================================

from abaqus import *                # from the main library
from caeModules import *            # import the modules
from abaqusConstants import *       # constants we need
from math import fabs

# setup the logger
from Base import Base

# forced reload for the developer step
import InputData                    # bind module to the symbol
reload(InputData)                   # reload in any case
from InputData import InputData     # standard import
data = InputData()

# project name
prjname = data.name

# create the logger
logname = prjname + ".log"
Logger  = Base(logname)

# create the database
Logger.AppendLog("create database '%s'..." % prjname)
try:
    if mdb.models[prjname]:
        print "Model: \"%s\" is already available. Deleting it and creating again..." % mdb.models[prjname].name
        del mdb.models[prjname]
        myModel = mdb.Model(name=prjname)
except KeyError:
    myModel = mdb.Model(name=prjname)

# create the sketch
Logger.AppendLog("create sketch...")
mySketch = myModel.ConstrainedSketch(name = prjname, sheetSize=2*(data.b_q+data.h_t))

# point array
xyPoints = ((+data.qs, data.quad_y),(-data.qs, data.quad_y),(-data.qs, -data.quad_y),(+data.qs, -data.quad_y),(+data.qs, data.quad_y),(-data.qs, -data.lower_y),(-(data.qs + (data.b_t / 2.)), -data.lower_y),(-(data.qs - (data.b_t / 2.)), -data.lower_y),(0., -data.quad_y),(0., -data.lower_y),(-(data.b_t / 2.), -data.lower_y),(+(data.b_t / 2.), -data.lower_y),(+data.qs, -data.lower_y),(+(data.qs - (data.b_t / 2.)), -data.lower_y),(+(data.qs + (data.b_t / 2.)), -data.lower_y))

# create the lines
mySketch.Line(point1=(+data.qs, data.quad_y),point2=(-data.qs, data.quad_y))
mySketch.Line(point1=(-data.qs, data.quad_y),point2=(-data.qs, -data.quad_y))
mySketch.Line(point1=(-data.qs, -data.quad_y),point2=(+data.qs, -data.quad_y))
mySketch.Line(point1=(+data.qs, -data.quad_y),point2=(+data.qs, data.quad_y))
mySketch.Line(point1=(-data.qs, -data.quad_y),point2=(-data.qs, -data.lower_y))
mySketch.Line(point1=(-(data.qs + (data.b_t / 2.)), -data.lower_y),point2=(-(data.qs - (data.b_t / 2.)), -data.lower_y))
mySketch.Line(point1=(0., -data.quad_y),point2=(0., -data.lower_y))
mySketch.Line(point1=(-(data.b_t / 2.), -data.lower_y),point2=(+(data.b_t / 2.), -data.lower_y))
mySketch.Line(point1=(+data.qs, -data.quad_y),point2=(+data.qs, -data.lower_y))
mySketch.Line(point1=(+(data.qs - (data.b_t / 2.)), -data.lower_y),point2=(+(data.qs + (data.b_t / 2.)), -data.lower_y))

# Create Part
Logger.AppendLog("create part...")
myPart = myModel.Part(name = prjname, dimensionality = THREE_D,
                      type = DEFORMABLE_BODY)

# Extrusion
myPart.BaseShellExtrude(sketch=mySketch, depth=data.l)

# create the material
Logger.AppendLog("create material...")
myMaterial = myModel.Material(name = "Steel")
myMaterial.Elastic(table = ( (data.EMod,data.nue), ))

# create the section data
Logger.AppendLog("create section data...")
myModel.HomogeneousShellSection(name = prjname+"-Quad-Section-Flange",
                                material = "Steel", thickness = data.s_q)
myModel.HomogeneousShellSection(name = prjname+"-T-Section-Flange",
                                material = "Steel", thickness = data.s_t)

# assign the section data to the face of the model
Logger.AppendLog("assign section data...")

# Quadrilateral Section
facesQuad = myPart.faces.findAt( ( (data.qs / 2., -data.quad_y, data.l/2.), ),
                                   ( (-data.qs / 2., -data.quad_y, data.l/2.), ),
                                   ( (data.qs / 2., +data.quad_y, data.l/2.), ),
                                   ( (-data.qs, 0., data.l/2.), ),
                                   ( (+data.qs, 0., data.l/2.), ))
quadSet = myPart.Set(faces = facesQuad, name = "QuadSet")
myPart.SectionAssignment(region = quadSet, sectionName = prjname + "-Quad-Section-Flange")

# T Section
facesT = myPart.faces.findAt( ( (-data.qs, -(data.lower_y + data.quad_y) / 2., data.l/2.), ),       # nodes 4 to 2
                                   ( (-(data.qs + (data.b_t / 2.)), -data.lower_y, data.l/2.), ),   # nodes 1 to 2
                                   ( (-(data.qs - (data.b_t / 2.)), -data.lower_y, data.l/2.), ),   # nodes 2 to 3
                                   ( (0., -(data.lower_y + data.quad_y) / 2., data.l/2.), ),        # nodes 8 to 6
                                   ( (-(data.b_t / 2.), -data.lower_y, data.l/2.), ),               # nodes 5 to 6
                                   ( (+(data.b_t / 2.), -data.lower_y, data.l/2.), ),               # nodes 6 to 7
                                   ( (+data.qs, -(data.lower_y + data.quad_y) / 2., data.l/2.), ),  # nodes 12 to 10
                                   ( (+(data.qs - (data.b_t / 2.)), -data.lower_y, data.l/2.), ),   # nodes 9 to 10
                                   ( (+(data.qs + (data.b_t / 2.)), -data.lower_y, data.l/2.), ))   # nodes 10 to 11
tSet = myPart.Set(faces = facesT, name = "TSet")
myPart.SectionAssignment(region = tSet, sectionName = prjname + "-Quad-Section-Flange")

# create the mesh
Logger.AppendLog("create mesh...")
# select the element type
elemType1 = mesh.ElemType(elemCode=S4R)
elemType2 = mesh.ElemType(elemCode=S3)

# assign the element type
facesQuad = myPart.faces.findAt( ( (data.qs / 2., -data.quad_y, data.l/2.), ),
                                   ( (-data.qs / 2., -data.quad_y, data.l/2.), ),
                                   ( (data.qs / 2., +data.quad_y, data.l/2.), ),
                                   ( (-data.qs, 0., data.l/2.), ),
                                   ( (+data.qs, 0., data.l/2.), ))
regionAll = (facesQuad,)
myPart.setElementType(regions=regionAll, elemTypes=(elemType1,elemType2))

facesT = myPart.faces.findAt( ( (-data.qs, -(data.lower_y + data.quad_y) / 2., data.l/2.), ),       # nodes 4 to 2
                                   ( (-(data.qs + (data.b_t / 2.)), -data.lower_y, data.l/2.), ),   # nodes 1 to 2
                                   ( (-(data.qs - (data.b_t / 2.)), -data.lower_y, data.l/2.), ),   # nodes 2 to 3
                                   ( (0., -(data.lower_y + data.quad_y) / 2., data.l/2.), ),        # nodes 8 to 6
                                   ( (-(data.b_t / 2.), -data.lower_y, data.l/2.), ),               # nodes 5 to 6
                                   ( (+(data.b_t / 2.), -data.lower_y, data.l/2.), ),               # nodes 6 to 7
                                   ( (+data.qs, -(data.lower_y + data.quad_y) / 2., data.l/2.), ),  # nodes 12 to 10
                                   ( (+(data.qs - (data.b_t / 2.)), -data.lower_y, data.l/2.), ),   # nodes 9 to 10
                                   ( (+(data.qs + (data.b_t / 2.)), -data.lower_y, data.l/2.), ))   # nodes 10 to 11
regionAll = (facesT,)
myPart.setElementType(regions=regionAll, elemTypes=(elemType1,elemType2))

# set of edges for seeding
seedEdges = myPart.edges.findAt( ( (-data.qs, -data.quad_y, data.l/2.), ),          # nodes 4 to 2
                                   ( (-data.qs, +data.quad_y, data.l/2.), ),        # nodes 1 to 2
                                   ( (+data.qs, -data.quad_y, data.l/2.), ),        # nodes 2 to 3
                                   ( (+data.qs, +data.quad_y, data.l/2.), ))        # nodes 8 to 6
myPart.seedEdgeByNumber(edges=seedEdges, number=data.lengthSeed, constraint=FIXED)
seedEdges = myPart.edges.findAt( ( (-data.qs, 0., 0.), ),          # nodes 4 to 2
                                   ( (+data.qs, 0., 0.), ),        # nodes 1 to 2
                                   ( (+data.qs, 0., data.l), ),    # nodes 2 to 3
                                   ( (+data.qs, 0., data.l), ))    # nodes 8 to 6
myPart.seedEdgeByNumber(edges=seedEdges, number=data.quadHeightSeed, constraint=FIXED)
seedEdges = myPart.edges.findAt( ( (-data.qs/4., data.quad_y, 0.), ),          # nodes 4 to 2
                                   ( (-data.qs/4., data.quad_y, data.l), ))    # nodes 2 to 3
myPart.seedEdgeByNumber(edges=seedEdges, number=data.quadWidthSeed, constraint=FIXED)
seedEdges = myPart.edges.findAt( ( (+data.qs/4., -data.quad_y, 0.), ),         # nodes 1 to 2
                                   ( (-data.qs/4., -data.quad_y, 0.), ),       # nodes 1 to 2
                                   ( (+data.qs/4., -data.quad_y, data.l), ),   # nodes 8 to 6
                                   ( (-data.qs/4., -data.quad_y, data.l), ))   # nodes 8 to 6
myPart.seedEdgeByNumber(edges=seedEdges, number=(data.quadWidthSeed/2), constraint=FIXED)
seedEdges = myPart.edges.findAt( ( (-(data.qs+data.b_t/4.), -data.lower_y, 0.), ),
                                   ( (-(data.qs-data.b_t/4.), -data.lower_y, 0.), ),
                                   ( (+data.b_t/4., -data.lower_y, 0.), ),
                                   ( (+data.qs+data.b_t/4., -data.lower_y, 0.), ),
                                   ( (+data.qs-data.b_t/4., -data.lower_y, 0.), ),
                                   ( (-(data.qs+data.b_t/4.), -data.lower_y, data.l), ),
                                   ( (-(data.qs-data.b_t/4.), -data.lower_y, data.l), ),
                                   ( (+data.b_t/4., -data.lower_y, data.l), ),
                                   ( (+data.qs+data.b_t/4., -data.lower_y, data.l), ),
                                   ( (+data.qs-data.b_t/4., -data.lower_y, data.l), ))
myPart.seedEdgeByNumber(edges=seedEdges, number=data.tWebSeed, constraint=FIXED)
seedEdges = myPart.edges.findAt( ( (-data.qs, -(data.lower_y-data.h_t/2.), 0.), ),
                                   ( (0., -(data.lower_y-data.h_t/2.), 0.), ),
                                   ( (+data.qs, -(data.lower_y-data.h_t/2.), 0.), ),
                                   ( (-data.qs, -(data.lower_y-data.h_t/2.), data.l), ),
                                   ( (0., -(data.lower_y-data.h_t/2.), data.l), ),
                                   ( (+data.qs, -(data.lower_y-data.h_t/2.), data.l), ))
myPart.seedEdgeByNumber(edges=seedEdges, number=data.tFlangeSeed, constraint=FIXED)

Logger.AppendLog("  quadrilateral section height seed: %d" % data.quadHeightSeed)
Logger.AppendLog("  quadrilateral section width seed: %d" % data.quadWidthSeed)
Logger.AppendLog("  T section web seed   : %d" % data.tWebSeed)
Logger.AppendLog("  T section flange seed   : %d" % data.tFlangeSeed)
Logger.AppendLog("  length seed: %d" % data.lengthSeed)

# Meshing
myMesh = myPart.generateMesh()
elemArr = mdb.models[data.name].parts[data.name].elements;
nodeArr = mdb.models[data.name].parts[data.name].nodes;
Logger.AppendLog("  total number of nodes: %d" % len(nodeArr))

# nodes: container for meshnodes
webNodes = {}
eps = 1.e-10

nodes = myPart.nodes
Logger.AppendLog("--no -----x---- -----y---- -----z----")
for node in nodes:
    if fabs(node.coordinates[0]) < eps and fabs(node.coordinates[1] - data.quad_y) < eps:
        Logger.AppendLog("%4d %10.3f %10.3f %10.3f" % (node.label,
                    node.coordinates[0],node.coordinates[1],node.coordinates[2]))
        webNodes[node.label] = (node.coordinates[0],node.coordinates[1],node.coordinates[2])
Logger.AppendLog("  %d web nodes found" % len(webNodes))

# create the instance from the part
Logger.AppendLog("create instance...")
rootAssm = myModel.rootAssembly
myInstance = rootAssm.Instance(name='INSTANCE', part=myPart, dependent=ON)

# create a linear static step
if data.steptype == data.LINEAR:
    Logger.AppendLog("create a linear static step...")
    myModel.StaticStep(name = data.stepname,
                       previous = 'Initial',
                       description = 'static analysis')

# create a buckling step
else:
    pass  # next lecture

# create the loads
pressureFaces = myInstance.faces.findAt(((0., +data.quad_y, data.l/2.),),
                                        ( (-(data.qs + (data.b_t / 4.)), -data.lower_y, data.l / 2.), ),
                                        ( (+(data.qs + (data.b_t / 4.)), -data.lower_y, data.l / 2.), ))
# surface on which the pressure is applied
pressureSurface = rootAssm.Surface(name = "pressureSurface", side2Faces = myInstance.faces.findAt(((0., +data.quad_y, data.l/2.),)))

# sets containing edges & vertices on which boundary conditions are applied
bcFixedAllVertices = myInstance.vertices.findAt( ( ( -(data.qs + (data.b_t / 2.)), -data.lower_y, 0.), ),   # node 1
                                                ( (-(data.qs - (data.b_t / 2.)), -data.lower_y, 0.), ),     # node 3
                                                ( (-(data.b_t / 2.), -data.lower_y, 0.), ),                 # node 5
                                                ( (+(data.b_t / 2.), -data.lower_y, 0.), ),                 # node 7
                                                ( (+(data.qs - (data.b_t / 2.)), -data.lower_y, 0.), ),     # node 9
                                                ( (+(data.qs + (data.b_t / 2.)), -data.lower_y, 0.), ))     # node 11
bcFixedAllSet = rootAssm.Set(name = "bcFixedAll", vertices = bcFixedAllVertices)
bcFixedYVertices = myInstance.vertices.findAt( ( ( -(data.qs + (data.b_t / 2.)), -data.lower_y, data.l), ),     # node 1
                                                ( (-(data.qs - (data.b_t / 2.)), -data.lower_y, data.l), ),     # node 3
                                                ( (-(data.b_t / 2.), -data.lower_y, data.l), ),                 # node 5
                                                ( (+(data.b_t / 2.), -data.lower_y, data.l), ),                 # node 7
                                                ( (+(data.qs - (data.b_t / 2.)), -data.lower_y, data.l), ),     # node 9
                                                ( (+(data.qs + (data.b_t / 2.)), -data.lower_y, data.l), ))     # node 11
bcFixedYSet = rootAssm.Set(name = "bcFixedY", vertices = bcFixedYVertices)
bcFixedXZVertices = myInstance.vertices.findAt( ( ( -(data.qs + (data.b_t / 2.)), -data.lower_y, 0.), ),    # node 1
                                                ( (-data.qs, -data.lower_y, 0.), ),                         # node 2
                                                ( (-(data.qs - (data.b_t / 2.)), -data.lower_y, 0.), ),     # node 3
                                                ( (-(data.b_t / 2.), -data.lower_y, 0.), ),                 # node 5
                                                ( (0., -data.lower_y, 0.), ),                               # node 6
                                                ( (+(data.b_t / 2.), -data.lower_y, 0.), ),                 # node 7
                                                ( (+(data.qs - (data.b_t / 2.)), -data.lower_y, 0.), ),     # node 9
                                                ( (+data.qs, -data.lower_y, 0.), ),                         # node 10
                                                ( (+(data.qs + (data.b_t / 2.)), -data.lower_y, 0.), ))     # node 11
bcFixedXZSet = rootAssm.Set(name = "bcFixedXZ", vertices = bcFixedXZVertices)

#SET for finding maximum displacement
vertice_Set1 = myPart.faces.findAt(((0., +data.quad_y, data.l/2.),))    # top face
myPart.Set(faces=vertice_Set1, name='S')

# create the loads
Logger.AppendLog("create loads...")
myModel.Pressure(name='Load1',
                 createStepName = data.stepname,
                 region = pressureSurface,
                 distributionType = UNIFORM,
                 magnitude = -data.p1,
                 amplitude = UNSET)

# create boundary conditons
Logger.AppendLog("create BCs...")
myModel.DisplacementBC(name = 'fixed all',
                       createStepName = 'Initial',
                       region = bcFixedAllSet,
                       u1 = 0.0,
                       u2 = 0.0,
                       u3 = 0.0,
                       ur1 = 0.0,
                       ur2 = 0.0,
                       ur3 = 0.0)
myModel.DisplacementBC(name = 'fixed y',
                       createStepName = 'Initial',
                       region = bcFixedYSet,
                       u1 = 0.0,
                       u2 = 0.0,
                       ur2 = 0.0,
                       ur3 = 0.0)

# create the job
Logger.AppendLog("create the job...")
myJob = mdb.Job(name=data.jobname,model=prjname,description='Quadrilateral tube and triple T sections analysis')

# submit and execute
Logger.AppendLog("submit and execute the job...")
myJob.submit()
myJob.waitForCompletion()

#==============================================================================
# Postprocessing
#==============================================================================
# analyse the linear case
if data.steptype == data.LINEAR:
    # Setting the odb
    odbname = data.jobname + ".odb"
    Logger.AppendLog("open database '%s'..." % odbname)
    mySession  = session.openOdb(name=odbname)
    myViewport = session.viewports["Viewport: 1"]

    # Maximum Displacement value
    myViewport.setValues(displayedObject=mySession)
    myViewport.odbDisplay.setPrimaryVariable(variableLabel='U',outputPosition=NODAL,refinement=(COMPONENT,'U2'))
    myViewport.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))
    myViewport.view.fitView()
    max_disp = 0.
    frame = mySession.steps["Linear"].frames[-1]
    dis = frame.fieldOutputs['U']
    nodes = mySession.rootAssembly.instances["INSTANCE"].nodeSets['S']
    disp_at_nodes = dis.getSubset(region=nodes)
    dispSubField = disp_at_nodes.getSubset(region=nodes)
    max_disp = [0.]*1500
    i = 0
    for v in dispSubField.values:
        max_disp[i] = v.data[1]
        i += 1
Logger.AppendLog("Maximum Deflection is '%s'..." % min(max_disp))

# export U2 displacement as .png file
session.pngOptions.setValues(imageSize = SIZE_ON_SCREEN)
session.defaultViewportAnnotationOptions.setValues(title = OFF, state = OFF)
session.printToFile(fileName = data.jobname, format = PNG)