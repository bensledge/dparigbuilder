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
        u.aim_normal(b, normal=normal)
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
        u.aim_normal(a, normal=normal)
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
        
        if type(self.lock) != list:
            self.lock = []
        for attr in self.lock:
            pm.Attribute(self.ctrl.name() + '.%s' % attr).lock()

        return self.ctrl



# blocks

class Block(object):
    '''Abstract Block base class'''
    def __init__(self, name, controlRadius=1.0, controlColor=1, 
                 controlShape=Ctrl.CIRCLE, jointPostfix=d.BIND):
        self.name = name
        self.controlRadius = controlRadius
        self.controlColor = controlColor
        self.controlShape = controlShape
        self.jointPostfix = jointPostfix

        self.bindJoints = []
        self.controls = []

    def build(self):
        raise NotImplementedError

class RibbonIk(Block):
    '''defines a ribbon ik object'''

    def __init__(self, startLoc, endLoc, numSpans, numJoints,
                 name='ribbonIk',**kwargs):
        super(RibbonIk,self).__init__(name=name, **kwargs)
        self.startLoc = u.toPmNodes(startLoc)[0]
        self.endLoc = u.toPmNodes(endLoc)[0]
        self.numSpans = numSpans
        self.numJoints = numJoints
        self.ribbonIkPlane = None
        self.follicleGrp = None

        self.build()

    def create_follicle(self,shape, posU=0.5, posV=0.5, name=d.FOLLICLE):
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
            follicles.append(follicle)

        self.follicleGrp = pm.group(follicles, name='%s_%s_grp' % \
                                    (self.name,d.FOLLICLE))
        pm.setAttr('%s.%s'% (self.follicleGrp,'inheritsTransform'),0)
        
        # create the bind joints
        for i,f in enumerate(follicles):
            self.bindJoints.append(u.placeJoint(
                position = u.getWsLocation(f),
                name = '%s%s%02d_%s'%(self.name,d.JOINT.title(),i+1,d.BIND),
                parent = f))

class InlineOffset(object):
    def __init__(self, joints, controlShape=Ctrl.ARROWS4, **kwargs):
        super(InlineOffset,self).__init__(controlShape=controlShape, **kwargs)
        if type(joints) != list:
            joints  = [joints]

        for i in xrange(0,len(joints)):
            joints[i] = u.toPmNodes(joints[i])

        self.joints = joints

        self.build()

    def build(self):
        for joint in self.joints:
            joint = pm.PyNode(joint)
            parent = joint.getParent()
            ctrl   = Ctrl(
                    xform = joint,
                    name    = joint.name() + '_' + d.CTRL,
                    shape   = self.ctrl_shape,
                    radius  = self.radius,
                    normal  = [0,1,0],
                    color   = self.color,
                    group   = False).ctrl
            ctrl.setParent(parent)
            #pm.makeIdentity(ctrl, apply=True)
            joint.setParent(ctrl)
            self.controls.append(ctrl)

class LinearSkin(object):
    def __init__(self, mesh, start_loc, end_loc, num_ctrls=3, name="ls",
                 color=0, radius=2,ctrl_shape=Ctrl.CIRCLE):
        #super(LinearSkin,self).__init__()
        self.mesh_in = mesh
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.num_ctrls = num_ctrls
        self.name = name
        self.color = color
        self.radius = radius
        self.ctrl_shape = ctrl_shape

        self.controls = []
        self.drivers = []
        self.skin = None

        self.build()

    def build(self):
        '''builds'''
        # place joints in the scene
        self.drivers = u.place_joint_chain(
                self.start_loc,
                self.end_loc,
                num_joints = self.num_ctrls,
                parent = None,
                name = '%s_%s' % (self.name, d.DRVR))
        pm.delete(pm.orientConstraint(self.start_loc, self.drivers[0]))

        self.skin = pm.skinCluster(
                self.drivers, self.mesh_in,
                toSelectedBones = True,
                maximumInfluences   = 2)

        self.controls = InlineOffset(
                self.drivers,radius=self.radius,color=self.color,
                ctrl_shape=self.ctrl_shape).controls

class IkSC(object):
    def __init__(self, start_joint, end_joint, name=d.IK,color=0,
                 radius=1,ctrl_shape=Ctrl.BOX):
        self.start_joint = pm.PyNode(start_joint)
        self.end_joint = pm.PyNode(end_joint)
        self.name = name
        self.color = color
        self.radius = radius
        self.ctrl_shape = ctrl_shape

        self.controls = []
        self.ik_handle = None
        
        self.build()

    def build(self):
        self.ik_handle = pm.ikHandle(
                startJoint = self.start_joint,
                endEffector = self.end_joint,
                name = self.name + '_%s' % d.IK_HANDLE,
                sticky = 'sticky',
                solver = 'ikSCsolver')[0]
        self.ik_handle = pm.PyNode(self.ik_handle)
        ctrl = Ctrl(xform = self.end_joint, normal=[0,1,0],
                    name=self.name+'_%s'% d.CTRL,shape=self.ctrl_shape,
                    radius=self.radius,group=True,color=self.color,
                    lock=['rx','ry','rz']).ctrl
        self.ik_handle.setParent(ctrl)
        self.controls.append(ctrl)




class IkSpline(object):
    def __init__(self, start_loc, end_loc, num_spans, num_joints,
                 name='ikSpline'):
        object.__init__(self)
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.num_spans = num_spans
        self.num_joints = num_joints
        self.name = name

        self.joints = []
        self.ik_crv = None
        self.ik_handle = None
        self.ik_effector = None

        self.build()

    def build(self):
        self.joints = u.place_joint_chain(
                start_loc = self.start_loc,
                end_loc = self.end_loc,
                num_joints = self.num_joints,
                parent = None, 
                name = self.name)
        self.joints[0].setAttr('visibility', False)
        
        self.ik_handle, self.ik_effector, self.ik_crv = pm.ikHandle(
                startJoint = self.joints[0],
                endEffector = self.joints[-1],
                name = self.name + '_' + d.IK_HANDLE,
                solver = 'ikSplineSolver')
        self.ik_crv = pm.PyNode(self.ik_crv)
        self.ik_handle = pm.PyNode(self.ik_handle)

        self.ik_handle.inheritsTranform = False
        self.ik_handle.setAttr('visibility',False)

        self.ik_crv.rename(self.name + '_crv')
        self.ik_crv.setAttr('visibility',False)

        pm.rebuildCurve(self.ik_crv,
                degree = 3,
                spans = self.num_spans,
                keepRange = 0,
                constructionHistory=False)

class ManDynHair(object):
    def __init__(self, curve, start_loc, end_loc, num_ctrls=3,
                 name='manDynHair', color=0, hair_system=None, 
                 ctrl_radius=2,ctrl_shape=Ctrl.CIRCLE):
        self.curve_in = pm.PyNode(curve)
        self.start_loc = pm.PyNode(start_loc)
        self.end_loc = pm.PyNode(end_loc)
        self.num_ctrls = num_ctrls
        self.name = name
        self.color = color
        self.radius = ctrl_radius
        self.ctrl_shape = ctrl_shape

        self.man_crv = None
        self.dyn_in_crv = None
        self.dyn_out_crv = None
        self.man_dyn_bs = None
        self.shape_bs = None
        self.driver_joints = []
        self.controls = []
        self.hair_system = hair_system
        self.follicle = None

        self.build()

    def build(self):
        self.curve_in.setAttr('inheritsTransform',False)
        # create a crv and ctrls to act as a manual driver for the sys
        self.man_crv = pm.duplicate(self.curve_in,returnRootsOnly=True, 
                                    name = '%s_man_%s' % (self.name,d.CURVE))
        self.man_crv[0].inheritsTransform = False
        self.man_crv[0].setAttr('visibility',False)

        linear_skin = LinearSkin(
                mesh = self.man_crv, 
                start_loc = self.start_loc,
                end_loc = self.end_loc,
                num_ctrls = self.num_ctrls,
                name = self.name,
                color = self.color,
                radius = self.radius,
                ctrl_shape = self.ctrl_shape)

        self.driver_joints = linear_skin.drivers
        self.controls = linear_skin.controls

        self.dyn_in_crv = pm.duplicate(self.man_crv,returnRootsOnly=1,
                                       name = '%s_dynIn_%s' % (self.name,
                                                               d.CURVE))[0]
        self.dyn_in_crv.setAttr('visibility',False)
        # drive the dynmanic input curve with the manual curve
        self.shape_bs = pm.blendShape(self.man_crv, self.dyn_in_crv,
                                      name = '%s_shape_%s' % (self.name,
                                                              d.BLENDSHAPE))
        pm.blendShape(self.shape_bs, edit=True, weight=[(0,1)])
        
        # make a dynamic curve that is driven by a hairSystem
        self.dyn_out_crv = pm.duplicate(
                self.dyn_in_crv, returnRootsOnly=1,
                name = '%s_dynOut_%s' % (self.name, d.CURVE))[0]
        self.dyn_out_crv.inheritsTransform = False
        self.dyn_out_crv.setAttr('visibility',False)
        self.follicle = pm.createNode('follicle', skipSelect=1, 
                                      name = '%s_%sShape' % (
                                          self.name,d.FOLLICLE))
        self.follicle = pm.rename(self.follicle.getParent(),
                                  '%s_%s' % (self.name,d.FOLLICLE))
        self.follicle.setAttr('visibility',False)
        self.follicle.restPose.set(1)
        
        if self.hair_system == None or not pm.objExists(self.hair_system):
            self.hair_system = pm.createNode(
                    'hairSystem', skipSelect=1,
                    name='%s_%sShape' % (self.name,d.HAIR_SYS))
            self.hair_system = pm.rename(self.hair_system.getParent(),
                                         '%s_%s' % (self.name,d.HAIR_SYS))
            pm.PyNode('time1').outTime >> \
                    self.hair_system.getShape().currentTime
            self.hair_system.setAttr('visibility',False)

        hair_system = pm.PyNode(self.hair_system)
        hair_index=len(hair_system.getShape().inputHair.listConnections())

        pm.parent(self.dyn_in_crv, self.follicle)
        self.dyn_in_crv.getShape().worldSpace[0] >> \
                self.follicle.getShape().startPosition
        self.follicle.getShape().outCurve >> \
                self.dyn_out_crv.getShape().create
        self.follicle.getShape().outHair >> \
                hair_system.getShape().inputHair[hair_index]
        hair_system.getShape().outputHair[hair_index] >> \
                self.follicle.getShape().currentPosition


        # drive the input curve with a blendshape to blend btwn 
        # the manual and dynmanic curves
        self.man_dyn_bs = pm.blendShape(
                self.man_crv, self.dyn_out_crv, self.curve_in, 
                name='%s_manDyn_%s' % (self.name, d.BLENDSHAPE))[0]

        pm.addAttr(self.controls[0],
                longName='manDynBlend', attributeType='float',
                minValue = 0.0, maxValue = 1.0, keyable=True)

        pma = pm.createNode('plusMinusAverage', skipSelect=1,
                            name = '%s_%s' % (self.name, d.PMA))
        pma.setAttr('operation','Subtract')
        pma.setAttr('input1D[0]',1)

        self.controls[0].manDynBlend >> self.man_dyn_bs.weight[1]
        self.controls[0].manDynBlend >> pma.input1D[1]
        pma.output1D >> self.man_dyn_bs.weight[0]
