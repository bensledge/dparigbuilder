from pymel.core import * 
import pymel.core as pm
from pymel import *

import utils as u
reload (u)

# defines

BIND = 'bind'
FOLLICLE = 'follicle'
JOINT = 'joint'
CURVE = 'crv'
WIRE  = 'wire'
DRVR  = 'drvr%s' % (JOINT.title())
CTRL  = 'ctrl'

# utils

def distance(xforma, xformb):
    ax, ay, az = xforma.getTranslation(space='world')
    bx, by, bz = xformb.getTranslation(space='world')

    return ((ax-bx)**2 + (ay-by)**2 + (az-bz)**2)**0.5

def create_follicle(shape, posU=0.5, posV=0.5, name='follicle'):
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

def place_joint(position,name='joint',parent=None):
    joint = pm.joint(name=name, position=(0,0,0))
    joint.setTranslation(position, 'world')
    if parent:
        pm.delete(pm.orientConstraint(parent,joint))
    joint.setParent(parent)
    return joint

class Ctrl(object):
    CIRCLE  = 'circle'
    
    # shapes
    def circle(name, radius, normal):
        return pm.circle(object=True,
                name    = name,
                normal  = normal,
                radius  = radius)[0]
    
    build_shape = {
        CIRCLE: circle,
    }
    def __init__(self,xform, name="ctrl", shape=CIRCLE, radius=1.0,
            normal=[1,0,0], group=True):
        self.name   = name
        self.shape  = shape
        self.radius = radius
        self.normal = normal
        self.xform  = xform
        self.group  = group

        self.ctrl   = None

        self.build()

    def build(self):
        self.ctrl = Ctrl.build_shape[self.shape](self.name, self.radius, self.normal)
        
        pos_obj = self.ctrl
        if self.group:
            pos_obj = pm.group(
                    self.ctrl, world=True, name=self.ctrl.name() + 'Grp')
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
        self.start_loc  = u.to_pm_nodes(start_loc)[0]
        self.end_loc    = u.to_pm_nodes(end_loc)[0]
        self.num_spans  = num_spans
        self.num_joints = num_joints
        self.name       = name
        self.bind_joints= []
        self.ribbonIkPlane = None

        self.build()

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
        pm.rebuildSurface(self.ribbonIkPlane,degreeU=1,spansU=1,direction=0)
        make_non_rendering(self.ribbonIkPlane)
        pm.setAttr('%s.%s'% (self.ribbonIkPlane.name(),'visibility'), 0)

        # move the pivots to the top of the plane
        self.ribbonIkPlane.setPivots((0,(self.num_spans/2.0),0))

        # place and scale the plane in 3d space
        pm.delete(pm.pointConstraint(self.start_loc,self.ribbonIkPlane))
        pm.delete(pm.orientConstraint(self.start_loc,self.ribbonIkPlane))
        #pm.delete(pm.aimConstraint(self.end_loc,self.ribbonIkPlane, 
        #            aimVector=(0,-1,0)))
                    #skip     =('x','z'))) 
        height = distance(self.start_loc, self.end_loc)
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
            follicle = create_follicle(
                    shape = self.ribbonIkPlane.getShape(),
                    posV  = (i-1.0)/float(self.num_joints-1.0),
                    posU  = 0.5, 
                    name  = self.name + "_%s%02d" % (FOLLICLE,i))
            follicles.append(follicle)

        follicle_grp=pm.group(follicles, name='%s_%s_grp' % \
                (self.name,FOLLICLE))
        
        # create the bind joints
        for i,f in enumerate(follicles):
            self.bind_joints.append(place_joint(
                position= u.get_ws_location(f),
                name    = '%s%s%02d_%s' %(self.name,JOINT.title(),i+1,BIND),
                parent  = f))

class WireCurve(object):
    def __init__(self, mesh, start_loc, end_loc, num_spans=9, num_ctrls=3,
            name='wireCrv'):
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
        pm.rebuildCurve(self.wire_crv,
                #constructionHistory = False,
                degree  = 3,
                spans   = self.num_spans,
                keepRange=0)
        self.wire_crv.centerPivots()
        # create deformer 
        dist = distance(self.start_loc, self.end_loc)
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
    def __init__(self,joints,radius=1.0):
        if type(joints) != list:
            joints  = [joints]

        self.joints = joints
        self.ctrls  = []

        self.build()

    def build(self):
        for joint in self.joints:
            print 'joint',joint
            parent = joint.getParent()
            ctrl   = Ctrl(xform = joint,
                    name    = joint.name() + '_ctrl',
                    shape   = Ctrl.CIRCLE,
                    radius  = 1.0,
                    normal  = [0,1,0],
                    group   = False).ctrl
            ctrl.setParent(parent)
            pm.makeIdentity(ctrl, apply=True)
            joint.setParent(ctrl)
            self.ctrls.append(ctrl)

class LinearSkin(object):
    def __init__(self, mesh, start_loc, end_loc, num_ctrls=3, name="ls"):
        #super(LinearSkin,self).__init__()
        self.mesh_in    = mesh
        self.start_loc  = start_loc
        self.end_loc    = end_loc
        self.num_ctrls  = num_ctrls
        self.name       = name

        self.controls   = []
        self.drivers    = []
        self.skin       = None

        self.build()

    def build(self):
        '''builds'''
        # place joints in the scene
        start_joint = place_joint(
                u.get_ws_location(self.start_loc),
                name= '%s_%s%02d' % (self.name,DRVR,1))
        end_joint = place_joint(
                u.get_ws_location(self.end_loc),
                parent=start_joint,
                name= '%s_%s%02d' % (self.name,DRVR,self.num_ctrls))
        dist = end_joint.getTranslation()
        dist = dist / float(self.num_ctrls - 1 )

        parent_joint = start_joint
        self.drivers.append(start_joint)
        for i in range(2,self.num_ctrls):
            inside_joint= pm.insertJoint(self.drivers[-1])
            inside_joint= u.to_pm_nodes(inside_joint)[0]
            inside_joint = pm.rename(inside_joint,
                '%s_%s%02d' % (self.name,DRVR,i))
            inside_joint.translateBy(dist)
            end_joint.translateBy(-dist)
            self.drivers.append(inside_joint)
        self.drivers.append(end_joint)

        self.skin = pm.skinCluster(self.drivers, self.mesh_in,
                toSelectedBones = True,
                maximumInfluences   = 2)
        print self.skin, type(self.skin)

        InlineOffset(self.drivers)

        
