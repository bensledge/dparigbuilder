import pymel.core as pm

import utils as u
reload(u)

import defines as d
reload(d)

class Ctrl(object):
    CIRCLE = 'circle'
    BOX = 'box'
    ARROWS4 = 'arrows4'
    
    CRIMSON = 4
    NAVY = 5
    BLUE = 6
    BRICK = 12
    RED = 13
    GREEN = 14
    YELLOW = 17
    AQUA = CYAN = 18


    # shapes
    def circle(name, radius, normal, color):
        circ =  pm.circle(
                object=True,
                name=name,
                normal=normal,
                radius=radius,
                constructionHistory = False)[0]
        circ.getShape().overrideEnabled.set(True)
        circ.getShape().overrideColor.set(color)
        return circ

    def box(name, radius, normal, color):
        r = radius
        points = [(-1*r, -1*r,-1*r),
                  (-1*r, -1*r, 1*r),
                  ( 1*r, -1*r, 1*r),
                  ( 1*r, -1*r,-1*r),
                  (-1*r, -1*r,-1*r),
                  (-1*r,  1*r,-1*r),
                  (-1*r,  1*r, 1*r),
                  (-1*r, -1*r, 1*r),
                  (-1*r,  1*r, 1*r),
                  ( 1*r,  1*r, 1*r),
                  ( 1*r, -1*r, 1*r),
                  ( 1*r,  1*r, 1*r),
                  ( 1*r,  1*r,-1*r),
                  ( 1*r, -1*r,-1*r),
                  ( 1*r,  1*r,-1*r),
                  (-1*r,  1*r,-1*r)]

        b = pm.curve(
                point=points,
                name=name,
                degree=1,
                worldSpace=True)
        u.aimNormal(b, normal=normal)
        pm.makeIdentity(b,apply=True)
        b.getShape().overrideEnabled.set(True)
        b.getShape().overrideColor.set(color)
        return b

    def arrows4(name, radius, normal, color):
        r = radius
        points = [(0.25*r, 0*r, 0.75*r),
                  (0*r, 0*r, 1*r),
                  (-.25*r, 0*r, 0.75*r),
                  (0.25*r, 0*r, 0.75*r),
                  (0*r, 0*r, 1*r),
                  (0*r, 0*r, -1*r),
                  (0.25*r, 0*r, -.75*r),
                  (-.25*r, 0*r, -.75*r),
                  (0*r, 0*r, -1*r),
                  (0*r, 0*r, 0*r),
                  (-1*r, 0*r, 0*r),
                  (-.75*r, 0*r, 0.25*r),
                  (-.75*r, 0*r, -.25*r),
                  (-1*r, 0*r, 0*r),
                  (1*r, 0*r, 0*r),
                  (0.75*r, 0*r, -.25*r),
                  (0.75*r, 0*r, 0.25*r),
                  (1*r, 0*r, 0)]

        a = pm.curve(point=points, name=name, degree=1, worldSpace=True)
        u.aimNormal(a, normal=normal)
        pm.makeIdentity(a,apply=True)
        a.getShape().overrideEnabled.set(True)
        a.getShape().overrideColor.set(color)
        return a
    
    build_shape = {
        CIRCLE: circle,
        BOX: box,
        ARROWS4: arrows4,
    }
    def __init__(self,xform=None, name=d.CTRL, shape=CIRCLE, radius=1.0,
                 normal=[1,0,0], group=True, color=0, lock=None):
        self.name = name
        self.shape = shape
        self.radius = radius
        self.normal = normal
        self.xform = xform
        self.group = group
        self.color = color
        self.lock = lock

        self.ctrl = None

        self.build()

    def build(self):
        self.ctrl = Ctrl.build_shape[self.shape](self.name, self.radius, 
                                                 self.normal, self.color)
        
        posObj = self.ctrl
        if self.group:
            pos_obj = pm.group(self.ctrl, world=True, 
                               name=self.ctrl.name() + 'Grp')
        if self.xform:
            pm.delete(pm.orientConstraint(self.xform,posObj))
            pm.delete(pm.pointConstraint(self.xform,posObj))

        pm.makeIdentity(self.ctrl,apply=True)
        
        if type(self.lock) != list:
            self.lock = []
        for attr in self.lock:
            pm.Attribute(self.ctrl.name() + '.%s' % attr).lock()

        return self.ctrl



# blocks

class Block(object):
    '''Abstract Block base class'''
    def __init__(self, name, controlRadius=1.0, controlColor=1, 
                 controlShape=Ctrl.CIRCLE, jointPostfix=d.BIND, parent=None,
                 **kwargs):
        self.name = name
        self.controlRadius = controlRadius
        self.controlColor = controlColor
        self.controlShape = controlShape
        self.jointPostfix = jointPostfix
        self.parent = parent

        self.bindJoints = []
        self.controls = []

    def build(self):
        raise NotImplementedError

class RibbonIk(Block):
    '''Joints equily positioned along the middle of a NURBS plane.

    Useful for tails, tentacles and spines.
    '''

    def __init__(self, startLoc, endLoc, numSpans, numJoints,
                 name='ribbonIk', **kwargs):
        super(RibbonIk, self).__init__(name=name, **kwargs)
        self.startLoc = u.toPmNodes(startLoc)[0]
        self.endLoc = u.toPmNodes(endLoc)[0]
        self.numSpans = numSpans
        self.numJoints = numJoints
        self.ribbonIkPlane = None
        self.follicleGrp = None

        self.build()

    def createFollicle(self,shape, posU=0.5, posV=0.5, name=d.FOLLICLE):
        follicle = pm.createNode('follicle', name=name+'Shape')
        shape.local.connect(follicle.inputSurface)
        shape.worldMatrix[0].connect(follicle.inputWorldMatrix)
        
        follicle.outRotate.connect(follicle.getParent().rotate)
        follicle.outTranslate.connect(follicle.getParent().translate)
        follicle.parameterU.set(posU)
        follicle.parameterV.set(posV)
        follicle.getParent().t.lock()
        follicle.getParent().r.lock()
        
        follicle.getParent().rename(name)


        return follicle.getParent()

    def build(self):
        # make the nurbs plane
        self.ribbonIkPlane = pm.nurbsPlane(
                axis = (0,0,1),
                degree = 3,    #cubic
                constructionHistory = False,
                name = self.name +'_'+d.PLANE,
                patchesU = 1,
                patchesV = self.numSpans,
                lengthRatio = self.numSpans)[0]
        pm.rebuildSurface(self.ribbonIkPlane, degreeU=1,
                          spansU=1, direction=0)
        u.makeNonRendering(self.ribbonIkPlane)
        pm.setAttr('%s.%s'% (self.ribbonIkPlane.name(),'visibility'), 0)
        pm.setAttr('%s.%s'% (self.ribbonIkPlane.name(),
                             'inheritsTransform'), 0)

        # move the pivots to the top of the plane
        self.ribbonIkPlane.setPivots((0,(self.numSpans/2.0),0))

        # place and scale the plane in 3d space
        pm.delete(pm.pointConstraint(self.startLoc,self.ribbonIkPlane))
        pm.delete(pm.orientConstraint(self.startLoc,self.ribbonIkPlane))
        #pm.delete(pm.aimConstraint(self.endLoc,self.ribbonIkPlane, 
        #            aimVector=(0,-1,0)))
                    #skip     =('x','z'))) 
        height = u.distance(self.startLoc, self.endLoc)
        scale  = (height / self.numSpans)
        self.ribbonIkPlane.scaleBy((scale,scale,scale))
        
        # create and attach follicles
        follicles = []
        for i in range(1,(self.numJoints+1)):
            follicle = self.createFollicle(
                    shape = self.ribbonIkPlane.getShape(),
                    posV = (i-1.0)/float(self.numJoints-1.0),
                    posU = 0.5, 
                    name = self.name + "_%s%02d" % (d.FOLLICLE,i))
            pm.setAttr(follicle.visibility, False)
            follicles.append(follicle)

        self.follicleGrp = pm.group(follicles, name='%s_%s_grp' % \
                                    (self.name,d.FOLLICLE))
        pm.setAttr('%s.%s'% (self.follicleGrp,'inheritsTransform'),0)
        
        # create the bind joints
        for i,f in enumerate(follicles):
            self.bindJoints.append(u.placeJoint(
                position = u.getWsLocation(f),
                name = '%s%s%02d_%s'%(self.name, d.JOINT.title(),
                                      i+1, self.jointPostfix),
                parent = f))

        # parent
        self.ribbonIkPlane.setParent(self.parent)

class InlineOffset(Block):
    '''Inserts control shapes into the scene hierarchy above the give jnts.
    '''

    def __init__(self, joints, name='offset', controlShape=Ctrl.ARROWS4,
                 **kwargs):
        super(InlineOffset,self).__init__(name=name,controlShape=controlShape,
                                          **kwargs)
        if type(joints) != list:
            joints  = [joints]

        self.joints = joints

        self.build()

    def build(self):
        for joint in self.joints:
            joint = pm.PyNode(joint)
            parent = joint.getParent()
            ctrl   = Ctrl(xform = joint,
                          name = joint.name() + '_' + d.CTRL,
                          shape = self.controlShape,
                          radius = self.controlRadius,
                          normal = [0,1,0],
                          color = self.controlColor,
                          group = False).ctrl
            ctrl.setParent(parent)
            pm.makeIdentity(ctrl, apply=True)
            joint.setParent(ctrl)
            self.controls.append(ctrl)

class LinearSkin(Block):
    '''Places a joint chain in the scene and skins the given mesh to it. 
    '''
    def __init__(self, mesh, startLoc, endLoc, numControls=3, name="ls",
                 controlShape=Ctrl.CIRCLE, jointPostfix=d.DRVR, **kwargs):
        super(LinearSkin,self).__init__(name=name, controlShape=controlShape,
                                        jointPostfix=jointPostfix, **kwargs)
        self.meshIn = mesh
        self.startLoc = startLoc
        self.endLoc = endLoc
        self.numControls = numControls

        self.controls = []
        self.drivers = []
        self.skin = None

        self.build()

    def build(self):
        # place joints in the scene
        self.drivers = u.placeJointChain(
                self.startLoc,
                self.endLoc,
                numJoints = self.numControls,
                parent = None,
                name = '%s_%s' % (self.name, self.jointPostfix))
        pm.delete(pm.orientConstraint(self.startLoc, self.drivers[0]))

        self.skin = pm.skinCluster(
                self.drivers, self.meshIn,
                toSelectedBones = True,
                maximumInfluences = 2)

        self.controls = InlineOffset(
                self.drivers, controlRadius=self.controlRadius, 
                controlColor=self.controlColor, 
                controlShape=self.controlShape).controls

        self.controls[0].setParent(self.parent)

class IkSC(Block):
    '''Makes an IK system (using Maya's SC solver).
    '''
    def __init__(self, startJoint, endJoint, name=d.IK, controlShape=Ctrl.BOX,
                 **kwargs):
        super(IkSC, self).__init__(name=name, controlShape=controlShape,
                                   **kwargs)
        self.startJoint = pm.PyNode(startJoint)
        self.endJoint = pm.PyNode(endJoint)

        self.ikHandle = None
        
        self.build()

    def build(self):
        self.ikHandle = pm.ikHandle(
                startJoint = self.startJoint,
                endEffector = self.endJoint,
                name = self.name + '_%s' % d.IK_HANDLE,
                sticky = 'sticky',
                solver = 'ikSCsolver')[0]
        self.ikHandle = pm.PyNode(self.ikHandle)
        ctrl = Ctrl(xform = self.endJoint, normal=[0,1,0],
                    name=self.name+'_%s'% d.CTRL, shape=self.controlShape, 
                    radius=self.controlRadius, group=True, 
                    color=self.controlColor, lock=['rx','ry','rz']).ctrl
        self.ikHandle.setParent(ctrl)
        self.controls.append(ctrl)




class IkSpline(Block):
    '''Places a joint chain in the scene and applies an IK spline system.
    '''
    def __init__(self, startLoc, endLoc, numSpans, numJoints,
                 name='ikSpline', **kwargs):
        super(IkSpline, self).__init__(name=name, **kwargs)
        self.startLoc = startLoc
        self.endLoc = endLoc
        self.numSpans = numSpans
        self.numJoints = numJoints
        self.name = name

        self.joints = []
        self.ikCrv = None
        self.ikHandle = None
        self.ikEffector = None

        self.build()

    def build(self):
        self.joints = u.placeJointChain(
                startLoc = self.startLoc,
                endLoc = self.endLoc,
                numJoints = self.numJoints,
                parent = None, 
                name = self.name)
        self.joints[0].setAttr('visibility', False)
        
        self.ikHandle, self.ikEffector, self.ikCrv = pm.ikHandle(
                startJoint = self.joints[0],
                endEffector = self.joints[-1],
                name = self.name + '_' + d.IK_HANDLE,
                solver = 'ikSplineSolver')
        self.ikCrv = pm.PyNode(self.ikCrv)
        self.ikHandle = pm.PyNode(self.ikHandle)

        self.ikHandle.inheritsTranform = False
        self.ikHandle.setAttr('visibility',False)

        self.ikCrv.rename(self.name + '_' + d.CURVE)
        self.ikCrv.setAttr('visibility',False)

        pm.rebuildCurve(self.ikCrv,
                degree = 3,
                spans = self.numSpans,
                keepRange = 0,
                constructionHistory = False)

class ManDynHair(Block):
    '''Creates a system to blend between manual and dynamic ctrl of a crv.
    '''
    def __init__(self, curve, startLoc, endLoc, numControls=3,
                 name='manDynHair', hairSystem=None, 
                 controlRadius=2, **kwargs):
        super(ManDynHair, self).__init__(name=name, controlRadius=controlRadius,
                                         **kwargs)
        self.curveIn = pm.PyNode(curve)
        self.startLoc = pm.PyNode(startLoc)
        self.endLoc = pm.PyNode(endLoc)
        self.numControls = numControls

        self.manCrv = None
        self.dynInCrv = None
        self.dynOutCrv = None
        self.manDynBs = None
        self.shapeBs = None
        self.driverJoints = []
        self.hairSystem = hairSystem
        self.follicle = None

        self.build()

    def build(self):
        self.curveIn.setAttr('inheritsTransform',False)
        # create a crv and ctrls to act as a manual driver for the sys
        self.manCrv = pm.duplicate(self.curveIn, returnRootsOnly=True, 
                                    name = '%s_man_%s' % (self.name,d.CURVE))
        self.manCrv[0].inheritsTransform = False
        self.manCrv[0].setAttr('visibility',False)

        linearSkin = LinearSkin(
                mesh = self.manCrv, 
                startLoc = self.startLoc,
                endLoc = self.endLoc,
                numControls = self.numControls,
                name = self.name,
                controlColor = self.controlColor,
                controlRadius = self.controlRadius,
                controlShape = self.controlShape)

        self.driverJoints = linearSkin.drivers
        self.controls = linearSkin.controls

        self.dynInCrv = pm.duplicate(self.manCrv,returnRootsOnly=1,
                                     name = '%s_dynIn_%s' % (self.name,
                                                             d.CURVE))[0]
        self.dynInCrv.setAttr('visibility',False)
        # drive the dynmanic input curve with the manual curve
        self.shapeBs = pm.blendShape(self.manCrv, self.dynInCrv,
                                     name = '%s_shape_%s' % (self.name,
                                                             d.BLENDSHAPE))
        pm.blendShape(self.shapeBs, edit=True, weight=[(0,1)])
        
        # make a dynamic curve that is driven by a hairSystem
        self.dynOutCrv = pm.duplicate(
                self.dynInCrv, returnRootsOnly=1,
                name = '%s_dynOut_%s' % (self.name, d.CURVE))[0]
        self.dynOutCrv.inheritsTransform = False
        self.dynOutCrv.setAttr('visibility',False)
        self.follicle = pm.createNode('follicle', skipSelect=1, 
                                      name = '%s_%sShape' % (
                                          self.name,d.FOLLICLE))
        self.follicle = pm.rename(self.follicle.getParent(),
                                  '%s_%s' % (self.name,d.FOLLICLE))
        self.follicle.setAttr('visibility',False)
        self.follicle.restPose.set(1)
        
        if self.hairSystem == None or not pm.objExists(self.hairSystem):
            self.hairSystem = pm.createNode(
                    'hairSystem', skipSelect=1,
                    name='%s_%sShape' % (self.name,d.HAIR_SYS))
            self.hairSystem = pm.rename(self.hairSystem.getParent(),
                                         '%s_%s' % (self.name,d.HAIR_SYS))
            pm.PyNode('time1').outTime >> \
                    self.hairSystem.getShape().currentTime
            self.hairSystem.setAttr('visibility',False)

        hairSystem = pm.PyNode(self.hairSystem)
        hairIndex=len(hairSystem.getShape().inputHair.listConnections())

        pm.parent(self.dynInCrv, self.follicle)
        self.dynInCrv.getShape().worldSpace[0] >> \
                self.follicle.getShape().startPosition
        self.follicle.getShape().outCurve >> \
                self.dynOutCrv.getShape().create
        self.follicle.getShape().outHair >> \
                hairSystem.getShape().inputHair[hairIndex]
        hairSystem.getShape().outputHair[hairIndex] >> \
                self.follicle.getShape().currentPosition


        # drive the input curve with a blendshape to blend btwn 
        # the manual and dynmanic curves
        self.manDynBs = pm.blendShape(
                self.manCrv, self.dynOutCrv, self.curveIn, 
                name='%s_manDyn_%s' % (self.name, d.BLENDSHAPE))[0]

        pm.addAttr(self.controls[0],
                longName='manDynBlend', attributeType='float',
                minValue = 0.0, maxValue = 1.0, keyable=True)

        pma = pm.createNode('plusMinusAverage', skipSelect=1,
                            name = '%s_%s' % (self.name, d.PMA))
        pma.setAttr('operation','Subtract')
        pma.setAttr('input1D[0]',1)

        self.controls[0].manDynBlend >> self.manDynBs.weight[1]
        self.controls[0].manDynBlend >> pma.input1D[1]
        pma.output1D >> self.manDynBs.weight[0]


class Lattice(Block):
    '''Creates a lattice around a given vertices.
    '''

    def __init__(self, geometry, latticeDivisions=[5,5,5], name='lattice', 
                 **kwargs):
        super(Lattice,self).__init__(name=name, **kwargs)
        self.geometry = geometry
        self.latticeDivisions = latticeDivisions

        self.lattice = None

        self.build()

        
    def build(self):
        pm.select(clear=True)
        pm.select(self.geometry)
        self.lattice = pm.nt.Lattice(objectCentered = True, 
                                     divisions = self.latticeDivisions,
                                     frontOfChain = True,
                                     name = self.name)
        self.lattice.getParent().setParent(self.parent)
