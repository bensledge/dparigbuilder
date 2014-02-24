
#from pymel.core import * 
import pymel.core as pm
#from pymel import *

import utils as u
reload (u)

# defines

BIND = 'bind'
FOLLICLE = 'follicle'
JOINT = 'joint'
CURVE = 'crv'
WIRE = 'wire'
DRVR = 'drvr%s' % (JOINT.title())
CTRL = 'ctrl'
BLENDSHAPE = 'bs'
HAIR_SYS = 'hsys'
PMA = 'pma'     # plus minus average

# utils


def place_joint(position,name='joint',parent=None):
    joint = pm.joint(name=name, position=(0,0,0))
    joint.setTranslation(position, 'world')
    if parent:
        pm.delete(pm.orientConstraint(parent,joint))
    joint.setParent(parent)
    return joint

def place_joint_chain(start_loc, end_loc, num_joints=3, 
                      parent=None, name='jointChain'):
    joints = []
    start_joint = place_joint(
            u.get_ws_location(start_loc),
            name = '%s%02d' % (name, 1),
            parent = parent)
    end_joint = place_joint(
            u.get_ws_location(end_loc),
            name = '%s%02d' % (name, num_joints),
            parent = start_joint)
    dist = end_joint.getTranslation()
    dist = dist / float(num_joints-1)

    joints.append(start_joint)
    for i in range(2,num_joints-1):
        inside_joint = pm.insertJoint(joints[-1])
        inside_joint = u.to_pm_nodes(inside_joint)[0]
        inside_joint = pm.rename(inside_joint,
                                 '%s%02d' % (name, i))
        inside_joint.translateBy(dist)
        end_joint.translateBy(-dist)
        joints.append(inside_joint)
    joints.append(end_joint)

    return joints

class Ctrl(object):
    CIRCLE  = 'circle'

    RED = 13
    BLUE = 6
    GREEN = 14
    YELLOW = 17
    
    # shapes
    def circle(name, radius, normal, color):
        circ =  pm.circle(
                object=True,
                name    = name,
                normal  = normal,
                radius  = radius,
                constructionHistory = False)[0]
        circ.getShape().overrideEnabled.set(True)
        circ.getShape().overrideColor.set(color)
        return circ
    
    build_shape = {
        CIRCLE: circle,
    }
    def __init__(self,xform=None, name="ctrl", shape=CIRCLE, radius=1.0,
                 normal=[1,0,0], group=True, color = 0):
        self.name   = name
        self.shape  = shape
        self.radius = radius
        self.normal = normal
        self.xform  = xform
        self.group  = group
        self.color  = color

        self.ctrl   = None

        self.build()

    def build(self):
        self.ctrl = Ctrl.build_shape[self.shape](self.name, self.radius, 
                                                 self.normal, self.color)
        
        pos_obj = self.ctrl
        if self.group:
            pos_obj = pm.group(self.ctrl, world=True, 
                               name=self.ctrl.name() + 'Grp')
        if self.xform:
            u.snap_to(guide = self.xform, nodes = self.ctrl)
        
        return self.ctrl

def make_non_rendering(node):
    node.setAttr('castsShadows',0)
    node.setAttr('receiveShadows',0)
    node.setAttr('motionBlur',0)
    node.setAttr('primaryVisibility',0)
    node.setAttr('smoothShading',0)
    node.setAttr('visibleInReflections',0)
    node.setAttr('visibleInRefractions',0)

    return node

# blocks

class RibbonIk(object):
    '''defines a ribbon ik object'''

    def __init__(self, start_loc, end_loc, num_spans, num_joints,
                 name='ribbonIk'):
        object.__init__(self)
        self.start_loc = u.to_pm_nodes(start_loc)[0]
        self.end_loc = u.to_pm_nodes(end_loc)[0]
        self.num_spans = num_spans
        self.num_joints = num_joints
        self.name = name
        self.bind_joints = []
        self.ribbonIkPlane = None
        self.follicle_grp = None

        self.build()

    def create_follicle(self,shape, posU=0.5, posV=0.5, name='follicle'):
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
                axis    = (0,0,1),
                degree  = 3,    #cubic
                constructionHistory=False,
                name    = self.name +'_plane',
                patchesU= 1,
                patchesV= self.num_spans,
                lengthRatio=self.num_spans)[0]
        pm.rebuildSurface(self.ribbonIkPlane,degreeU=1,
                          spansU=1,direction=0)
        make_non_rendering(self.ribbonIkPlane)
        pm.setAttr('%s.%s'% (self.ribbonIkPlane.name(),'visibility'), 0)
        pm.setAttr('%s.%s'% (self.ribbonIkPlane.name(),
                             'inheritsTransform'), 0)

        # move the pivots to the top of the plane
        self.ribbonIkPlane.setPivots((0,(self.num_spans/2.0),0))

        # place and scale the plane in 3d space
        pm.delete(pm.pointConstraint(self.start_loc,self.ribbonIkPlane))
        pm.delete(pm.orientConstraint(self.start_loc,self.ribbonIkPlane))
        #pm.delete(pm.aimConstraint(self.end_loc,self.ribbonIkPlane, 
        #            aimVector=(0,-1,0)))
                    #skip     =('x','z'))) 
        height = u.distance(self.start_loc, self.end_loc)
        scale  = (height / self.num_spans)
        self.ribbonIkPlane.scaleBy((scale,scale,scale))
        #TODO: fix maya's 'makeIdentity' function to work from a script
        #pm.makeIdentity(self.ribbonIkPlane,
        #        apply       = True,
        #        translate   = True,
        #        rotate      = True,
        #        scale       = True,
        #        normal      = False)
        
        # create and attach follicles
        follicles = []
        for i in range(1,(self.num_joints+1)):
            follicle = self.create_follicle(
                    shape = self.ribbonIkPlane.getShape(),
                    posV  = (i-1.0)/float(self.num_joints-1.0),
                    posU  = 0.5, 
                    name  = self.name + "_%s%02d" % (FOLLICLE,i))
            follicles.append(follicle)

        self.follicle_grp = pm.group(follicles, name='%s_%s_grp' % \
                                (self.name,FOLLICLE))
        pm.setAttr('%s.%s'% (self.follicle_grp,'inheritsTransform'),0)
        
        # create the bind joints
        for i,f in enumerate(follicles):
            self.bind_joints.append(place_joint(
                position= u.get_ws_location(f),
                name    = '%s%s%02d_%s'%(self.name,JOINT.title(),i+1,BIND),
                parent  = f))

class WireCurve(object):
    def __init__(self, mesh, start_loc, end_loc, num_spans=9, num_ctrls=3,
                 name='wireCrv'):
        raise NotImplementedError
        super(WireCurve,self).__init__()
        self.mesh_in    = mesh
        self.start_loc  = start_loc
        self.end_loc    = end_loc
        self.num_spans  = num_spans
        self.num_ctrls  = num_ctrls
        self.name       = name
        self.wire_crv   = None

        self.build()

    def build(self):
        # create curve
        self.wire_crv = pm.curve(
                name    = "%s_%s" % (self.name, CURVE),
                degree  = 1,
                point   = [u.get_ws_location(self.start_loc),
                           u.get_ws_location(self.end_loc)])
        pm.rebuildCurve(
                self.wire_crv,
                #constructionHistory = False,
                degree  = 3,
                spans   = self.num_spans,
                keepRange=0)
        self.wire_crv.centerPivots()
        # create deformer 
        dist = u.distance(self.start_loc, self.end_loc)
        self.wire_def   = pm.wire(
                self.mesh_in,
                wire    = self.wire_crv,
                name    = "%s_%s" % (self.name, WIRE),
                dropoffDistance=(0,dist))

        # create Clusters
        num_cvs = self.num_spans + 2

        # create ctrls
        raise NotImplemented

class InlineOffset(object):
    def __init__(self,joints,radius=1.0,color=0):
        if type(joints) != list:
            joints  = [joints]
        self.joints = joints
        self.radius = radius
        self.color  = color

        self.controls  = []

        self.build()

    def build(self):
        for joint in self.joints:
            parent = joint.getParent()
            ctrl   = Ctrl(
                    xform = joint,
                    name    = joint.name() + '_ctrl',
                    shape   = Ctrl.CIRCLE,
                    radius  = self.radius,
                    normal  = [0,1,0],
                    color   = self.color,
                    group   = False).ctrl
            ctrl.setParent(parent)
            pm.makeIdentity(ctrl, apply=True)
            joint.setParent(ctrl)
            self.controls.append(ctrl)

class LinearSkin(object):
    def __init__(self, mesh, start_loc, end_loc, num_ctrls=3, name="ls",
            color=0):
        #super(LinearSkin,self).__init__()
        self.mesh_in = mesh
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.num_ctrls = num_ctrls
        self.name = name
        self.color = color

        self.controls = []
        self.drivers = []
        self.skin = None

        self.build()

    def build(self):
        '''builds'''
        # place joints in the scene
        self.drivers = place_joint_chain(
                self.start_loc,
                self.end_loc,
                num_joints = self.num_ctrls,
                parent = None,
                name = '%s_%s' % (self.name, DRVR))

        self.skin = pm.skinCluster(
                self.drivers, self.mesh_in,
                toSelectedBones = True,
                maximumInfluences   = 2)

        self.controls = InlineOffset(
                self.drivers, radius=2, color=self.color).controls

class IkSpline(object):
    def __init__(self, start_loc, end_loc, num_spans, num_joints,
                 name='ikSpline',bs_node = None):
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
        self.joints = place_joint_chain(
                start_loc = self.start_loc,
                end_loc = self.end_loc,
                num_joints = self.num_joints,
                parent = None, 
                name = self.name)
        
        self.ik_handle, self.ik_effector, self.ik_crv = pm.ikHandle(
                startJoint = self.joints[0],
                endEffector = self.joints[-1],
                name = self.name + '_ikHandle',
                solver = 'ikSplineSolver')
        self.ik_handle.inheritsTranform = False

        self.ik_crv.rename(self.name + '_crv')

        pm.rebuildCurve(self.ik_crv,
                degree = 3,
                spans = self.num_spans,
                keepRange = 0,
                constructionHistory=False)

class ManDynHair(object):
    def __init__(self, curve, start_loc, end_loc, num_ctrls=3,
                 name='manDynHair', color=0, hair_system=None):
        self.curve_in = pm.PyNode(curve)
        self.start_loc = pm.PyNode(start_loc)
        self.end_loc = pm.PyNode(end_loc)
        self.num_ctrls = num_ctrls
        self.name = name
        self.color = color

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
        print self.curve_in,type(self.curve_in)
        # create a crv and ctrls to act as a manual driver for the sys
        self.man_crv = pm.duplicate(self.curve_in,returnRootsOnly=True, 
                                    name = '%s_man_%s' % (self.name,CURVE))
        self.man_crv[0].inheritsTransform = False

        linear_skin = LinearSkin(
                mesh = self.man_crv, 
                start_loc = self.start_loc,
                end_loc = self.end_loc,
                num_ctrls = self.num_ctrls,
                name = self.name,
                color = self.color)

        self.driver_joints = linear_skin.drivers
        self.controls = linear_skin.controls

        self.dyn_in_crv = pm.duplicate(self.man_crv,returnRootsOnly=1,
                                       name = '%s_dynIn_%s' % (self.name,
                                                               CURVE))[0]
        # drive the dynmanic input curve with the manual curve
        self.shape_bs = pm.blendShape(self.man_crv, self.dyn_in_crv,
                                      name = '%s_shape_%s' % (self.name,
                                                              BLENDSHAPE))
        pm.blendShape(self.shape_bs, edit=True, weight=[(0,1)])
        
        # make a dynamic curve that is driven by a hairSystem
        self.dyn_out_crv = pm.duplicate(
                self.dyn_in_crv, returnRootsOnly=1,
                name = '%s_dynOut_%s' % (self.name, CURVE))[0]
        self.dyn_out_crv.inheritsTransform = False
        self.follicle = pm.createNode('follicle', skipSelect=1, 
                                      name = '%s_%sShape' % (
                                          self.name,FOLLICLE))
        self.follicle = pm.rename(self.follicle.getParent(),
                                  '%s_%s' % (self.name,FOLLICLE))
        self.follicle.restPose.set(1)
        
        if self.hair_system == None or not pm.objExist(self.hair_system):
            self.hair_system = pm.createNode(
                    'hairSystem', skipSelect=1,
                    name='%s_%sShape' % (self.name,HAIR_SYS))
            self.hair_system = pm.rename(self.hair_system.getParent(),
                                         '%s_%s' % (self.name,HAIR_SYS))
            pm.PyNode('time1').outTime >> \
                    self.hair_system.getShape().currentTime

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
                name='%s_manDyn_%s' % (self.name, BLENDSHAPE))[0]

        pm.addAttr(self.controls[0],
                longName='manDynBlend', attributeType='float',
                minValue = 0.0, maxValue = 1.0, keyable=True)

        pma = pm.createNode('plusMinusAverage', skipSelect=1,
                            name = '%s_%s' % (self.name, PMA))
        pma.setAttr('operation','Subtract')
        pma.setAttr('input1D[0]',1)

        self.controls[0].manDynBlend >> self.man_dyn_bs.weight[1]
        self.controls[0].manDynBlend >> pma.input1D[1]
        pma.output1D >> self.man_dyn_bs.weight[0]
