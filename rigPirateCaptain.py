import pymel.core as pm

import blocks
from blocks import RibbonIk, LinearSkin, Ctrl, ManDynHair, IkSpline, IkSC,\
                   InlineOffset, place_xform, BIND, JOINT, IK
import skin
import utils 
reload(utils)
reload(blocks)
reload(skin)

NAMESPACE = 'surface:model:'

#
# Save the locators to file...just in case
#
loc_shapes = pm.ls(exactType='locator')
locs = [x.getParent() for x in pm.ls(exactType='locator')]
json = [utils.gen_node_entry(x) for x in locs]
utils.write_file('rigPirateCaptain_locs.json',json)


ctrls = []
all_ctrl = None

skin_dict = {
        # namespace:{
        #   SMOOTH:{mesh:[joints,],},
        #   RIGID:{joint:[meshes,],}, }

        NAMESPACE:{
            skin.SMOOTH:{ },#SMOOTH
            skin.RIGID:{  },#RIGID
            },#'surface:model:'
        }#skin_dict


innerTentacle_locs = [
        {'tentacleR1_ring_grp_0001':{
            'start_loc':'tentacleR1_ring_grp_0001_top_loc',
            'end_loc':'tentacleR1_ring_grp_0001_bottom_loc',
            'color':Ctrl.BLUE,}},
        {'tentacleR1_ring_grp_0002':{
            'start_loc':'tentacleR1_ring_grp_0002_top_loc',
            'end_loc':'tentacleR1_ring_grp_0002_bottom_loc',
            'color':Ctrl.RED,}},
        {'tentacleR1_grp_0003':{
            'start_loc':'tentacleR1_grp_0003_top_loc',
            'end_loc':'tentacleR1_grp_0003_bottom_loc',
            'color':Ctrl.RED,}},
        {'tentacleR1_grp_0004':{
            'start_loc':'tentacleR1_grp_0004_top_loc',
            'end_loc':'tentacleR1_grp_0004_bottom_loc',
            'color':Ctrl.BLUE,}},
        {'ringTentacleR2_grp_0001':{
            'start_loc':'ringTentacleR2_grp_0001_top_loc',
            'end_loc':'ringTentacleR2_grp_0001_bottom_loc',
            'color':Ctrl.RED,}},
        {'ringTentacleR2_grp_0002':{
            'start_loc':'ringTentacleR2_grp_0002_top_loc',
            'end_loc':'ringTentacleR2_grp_0002_bottom_loc',
            'color':Ctrl.BLUE,}},
        {'tentacleR3_grp_0001':{
            'start_loc':'tentacleR3_grp_0001_top_loc',
            'end_loc':'tentacleR3_grp_0001_bottom_loc',
            'color':Ctrl.YELLOW,}},
        {'tentacleR3_grp_0002':{
            'start_loc':'tentacleR3_grp_0002_top_loc',
            'end_loc':'tentacleR3_grp_0002_bottom_loc',
            'color':Ctrl.BLUE,}},
        {'tentacleR3_grp_0003':{
            'start_loc':'tentacleR3_grp_0003_top_loc',
            'end_loc':'tentacleR3_grp_0003_bottom_loc',
            'color':Ctrl.RED,}},
        ]

outerTentacle_locs = [
        # S3
        {'outerTentacleS3_0001':{
            'start_loc':'outerTentacleS3_0001_top_loc',
            'end_loc':'outerTentacleS3_0001_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS3_0002':{
            'start_loc':'outerTentacleS3_0002_top_loc',
            'end_loc':'outerTentacleS3_0002_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS3_0003':{
            'start_loc':'outerTentacleS3_0003_top_loc',
            'end_loc':'outerTentacleS3_0003_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS3_0004':{
            'start_loc':'outerTentacleS3_0004_top_loc',
            'end_loc':'outerTentacleS3_0004_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS3_0005':{
            'start_loc':'outerTentacleS3_0005_top_loc',
            'end_loc':'outerTentacleS3_0005_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS3_0006':{
            'start_loc':'outerTentacleS3_0006_top_loc',
            'end_loc':'outerTentacleS3_0006_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS3_0007':{
            'start_loc':'outerTentacleS3_0007_top_loc',
            'end_loc':'outerTentacleS3_0007_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS3_0008':{
            'start_loc':'outerTentacleS3_0008_top_loc',
            'end_loc':'outerTentacleS3_0008_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS3_0009':{
            'start_loc':'outerTentacleS3_0009_top_loc',
            'end_loc':'outerTentacleS3_0009_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        # S2
        {'outerTentacleS2_0001':{
            'start_loc':'outerTentacleS2_0001_top_loc',
            'end_loc':'outerTentacleS2_0001_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0006':{
            'start_loc':'outerTentacleS2_0006_top_loc',
            'end_loc':'outerTentacleS2_0006_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_0007':{
            'start_loc':'outerTentacleS2_0007_top_loc',
            'end_loc':'outerTentacleS2_0007_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0008':{
            'start_loc':'outerTentacleS2_0008_top_loc',
            'end_loc':'outerTentacleS2_0008_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0009':{
            'start_loc':'outerTentacleS2_0009_top_loc',
            'end_loc':'outerTentacleS2_0009_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0010':{
            'start_loc':'outerTentacleS2_0010_top_loc',
            'end_loc':'outerTentacleS2_0010_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0011':{
            'start_loc':'outerTentacleS2_0011_top_loc',
            'end_loc':'outerTentacleS2_0011_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0012':{
            'start_loc':'outerTentacleS2_0012_top_loc',
            'end_loc':'outerTentacleS2_0012_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_0013':{
            'start_loc':'outerTentacleS2_0013_top_loc',
            'end_loc':'outerTentacleS2_0013_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_0014':{
            'start_loc':'outerTentacleS2_0014_top_loc',
            'end_loc':'outerTentacleS2_0014_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_0015':{
            'start_loc':'outerTentacleS2_0015_top_loc',
            'end_loc':'outerTentacleS2_0015_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_0016':{
            'start_loc':'outerTentacleS2_0016_top_loc',
            'end_loc':'outerTentacleS2_0016_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_0017':{
            'start_loc':'outerTentacleS2_0017_top_loc',
            'end_loc':'outerTentacleS2_0017_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        # S1
        {'outerTentacleS1_0001':{
            'start_loc':'outerTentacleS1_0001_top_loc',
            'end_loc':'outerTentacleS1_0001_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS1_0002':{
            'start_loc':'outerTentacleS1_0002_top_loc',
            'end_loc':'outerTentacleS1_0002_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS1_0003':{
            'start_loc':'outerTentacleS1_0003_top_loc',
            'end_loc':'outerTentacleS1_0003_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS1_0004':{
            'start_loc':'outerTentacleS1_0004_top_loc',
            'end_loc':'outerTentacleS1_0004_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS1_0005':{
            'start_loc':'outerTentacleS1_0005_top_loc',
            'end_loc':'outerTentacleS1_0005_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS1_0006':{
            'start_loc':'outerTentacleS1_0006_top_loc',
            'end_loc':'outerTentacleS1_0006_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS1_0007':{
            'start_loc':'outerTentacleS1_0007_top_loc',
            'end_loc':'outerTentacleS1_0007_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS1_0008':{
            'start_loc':'outerTentacleS1_0008_top_loc',
            'end_loc':'outerTentacleS1_0008_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        ]
lowerBell_locs = [
        {'lowerBell01_loc':{
            'color':Ctrl.BLUE,
            'parent':'root',}},
        {'lowerBell02_loc':{
            'color':Ctrl.BLUE,
            'parent':'root',}},
        {'lowerBell03_loc':{
            'color':Ctrl.BLUE,
            'parent':'root',}},
        {'lowerBell04_loc':{
            'color':Ctrl.YELLOW,
            'parent':'root',}},
        {'lowerBell05_loc':{
            'color':Ctrl.RED,
            'parent':'root',}},
        {'lowerBell06_loc':{
            'color':Ctrl.RED,
            'parent':'root',}},
        {'lowerBell07_loc':{
            'color':Ctrl.RED,
            'parent':'root',}},
        {'lowerBell08_loc':{
            'color':Ctrl.RED,
            'parent':'root',}},
        {'lowerBell09_loc':{
            'color':Ctrl.RED,
            'parent':'root',}},
        {'lowerBell10_loc':{
            'color':Ctrl.YELLOW,
            'parent':'root',}},
        {'lowerBell11_loc':{
            'color':Ctrl.BLUE,
            'parent':'root',}},
        {'lowerBell12_loc':{
            'color':Ctrl.BLUE,
            'parent':'root',}},
        ]
upperBell_locs = [
        {'root_loc':{
            'color':Ctrl.YELLOW,
            'parent':None,}},
        {'upperBell_loc':{
            'color':Ctrl.YELLOW,
            'parent':'root',}}
        ]

def inner_tentacles(all_ctrl):
    innerTentacle_ctrls = []
    pm.addAttr(all_ctrl, longName='innerTentacleGeo',
               attributeType='bool', defaultValue=True, keyable=True)
    for dict_ in innerTentacle_locs:
        group = dict_.keys()[0]
        attrs = dict_.values()[0]

        mesh_name  = group.split('_')
        name   = mesh_name[0] + mesh_name[-1]
        print "Building RibbonIK for", name
        ribbon = RibbonIk(
                start_loc = attrs['start_loc'], 
                end_loc   = attrs['end_loc'],
                name      = name + "_ribbonIk",
                num_spans = 9,
                num_joints= 20)
        print "Building Driver for", name
        drivers = LinearSkin(
                mesh = ribbon.ribbonIkPlane,
                start_loc = attrs['start_loc'], 
                end_loc   = attrs['end_loc'],
                num_ctrls = 6,
                name = name,
                color     = attrs['color'])
        innerTentacle_ctrls.extend(drivers.controls)

        geo_grp = "%s%s" % (NAMESPACE,group)
        geo = pm.listRelatives(geo_grp, children=True, path=True)
        joints = [x.name() for x in ribbon.bind_joints]
        for node in geo:
            skin_dict[NAMESPACE][skin.SMOOTH].update(
                    {node.name():joints})
        ctrl_grp = pm.group(ribbon.ribbonIkPlane, 
                            drivers.controls[0], name='%s_ctrlGrp' % group)
        ribbon.follicle_grp.setParent(ctrl_grp)
        ctrl_grp.setParent(all_ctrl)
        all_ctrl.innerTentacleGeo >> pm.PyNode(NAMESPACE+group).visibility

    pm.addAttr(all_ctrl, longName='innerTentacleCtrls',
               attributeType='bool', defaultValue=True, keyable=True)
    for ctrl in innerTentacle_ctrls:
        all_ctrl.innerTentacleCtrls >> ctrl.visibility

    ctrls.extend(innerTentacle_ctrls)
    pm.sets(innerTentacle_ctrls,name="innerTentacleCtrls")

def outer_tentacles(all_ctrl):
    pm.addAttr(all_ctrl, longName='outerTentacleGeo',
               attributeType='bool', defaultValue=True, keyable=True)
    hair_sys = None
    outerTentacle_ctrls = []
    for dict_ in outerTentacle_locs:
        # get the names
        mesh = dict_.keys()[0]
        attrs = dict_.values()[0]

        name = mesh.split('_')
        name = name[0] + name[-1]

        # build the rig
        print "Building Spline for",name
        spline = IkSpline(
                start_loc = attrs['start_loc'],
                end_loc = attrs['end_loc'],
                name = name + '_spline',
                num_spans = 10,
                num_joints = 10)
        joints = [x.name() for x in spline.joints]

        print "Building ManDynHair for",name
        mdhair = ManDynHair(
                curve = spline.ik_crv,
                start_loc = spline.start_loc,
                end_loc = spline.end_loc,
                num_ctrls = 5,
                name = name,
                color = attrs['color'],
                hair_system = hair_sys,
                ctrl_radius = 1)
        hair_sys = mdhair.hair_system

        outerTentacle_ctrls.extend(mdhair.controls)

        # update the skinning dict
        mesh = NAMESPACE + mesh
        skin_dict[NAMESPACE][skin.SMOOTH].update(
                {mesh:joints})

        # set geo.visibility to ctrl.visibiltiy
        mdhair.controls[0].visibility >> pm.PyNode(mesh).visibility

        # group everything together
        ctrl_grp = pm.group(
                spline.joints[0],spline.ik_crv, spline.ik_handle,
                mdhair.man_crv, mdhair.dyn_out_crv, mdhair.controls[0],
                mdhair.follicle,
                name = '%s_ctrlGrp' % name)
        ctrl_grp.setParent(all_ctrl)

        all_ctrl.outerTentacleGeo >> pm.PyNode(mesh).visibility

    pm.addAttr(all_ctrl, longName='outerTentacleCtrls',
               attributeType='bool', defaultValue=True, keyable=True)
    for ctrl in outerTentacle_ctrls:
        all_ctrl.outerTentacleCtrls >> ctrl.visibility
    
    ctrls.extend(outerTentacle_ctrls)
    pm.sets(outerTentacle_ctrls,name="outerTentacleCtrls")

def upper_bell(all_ctrl):
    upperBell_ctrls = []
    upperBell_joints = []
    for dict_ in upperBell_locs:
        loc = dict_.keys()[0]
        attrs = dict_.values()[0]

        name = loc.split('_')[0]
        loc = pm.PyNode(loc)

        joint = place_xform(name=name+'_%s'%BIND, mtype='joint',
                            matrix=loc.getMatrix(worldSpace=True),
                            worldSpace=True)
        parent = attrs['parent']
        if parent:
            parent = parent + '_%s' % BIND
        joint.setParent(parent)
        ctrl = InlineOffset(joint, radius=10, ctrl_shape='circle',
                            color=attrs['color']).controls[0]
        upperBell_ctrls.append(ctrl)
        upperBell_joints.append(joint)

    pm.addAttr(all_ctrl, longName='upperBellCtrls',attributeType='bool',
               defaultValue=True, keyable=True)
    for ctrl in upperBell_ctrls:
        all_ctrl.upperBellCtrls >> ctrl.visibility
    upperBell_ctrls[0].setParent(all_ctrl)

    return {'ctrls':upperBell_ctrls, 'joints':upperBell_joints}


def lower_bell(all_ctrl):
    lowerBell_ctrls = []
    lowerBell_joints = []
    for dict_ in lowerBell_locs:
        loc = dict_.keys()[0]
        attrs = dict_.values()[0]

        name = loc.split('_')[0]
        loc = pm.PyNode(loc)
                
        parent_joint = place_xform(name=name + '_%s' % BIND, mtype='joint',
                                    matrix=loc.getMatrix(worldSpace=True),
                                    worldSpace=True)
        parent = attrs['parent']
        if parent:
            parent = parent + '_%s' % BIND
        parent_joint.setParent(parent)
        parent_ctrl = InlineOffset(
                parent_joint, radius=1,ctrl_shape='circle',
                color=attrs['color']).controls[0]
        lowerBell_ctrls.append(parent_ctrl)
        lowerBell_joints.append(parent_joint)
        children = loc.listRelatives(children=True,type='transform')
        for endloc in children:
            endname = endloc.name().split('_')[0]
            endjoint = place_xform(
                    name=endname+'_%s'%BIND,mtype='joint',
                    matrix=endloc.getMatrix(worldSpace=True),
                    worldSpace=True)
            ikjoint = pm.duplicate(
                    parent_joint,name=endname+'_%s'%(IK+JOINT.title()),
                    parentOnly=True)[0]
            ikjoint = pm.PyNode(ikjoint)
            ikjoint.setParent(parent_joint)
            endjoint.setParent(ikjoint)
            ik = IkSC(start_joint=ikjoint, end_joint=endjoint, 
                      name=endname, color=attrs['color'], radius=0.5)
            lowerBell_ctrls.extend(ik.controls)
            ik.controls[0].getParent().setParent(parent_joint)

            lowerBell_joints.append(endjoint)

    pm.addAttr(all_ctrl, longName='lowerBellCtrls',
               attributeType='bool', defaultValue=True, keyable=True)
    for ctrl in lowerBell_ctrls:
        all_ctrl.lowerBellCtrls >> ctrl.visibility

    ctrls.extend(lowerBell_ctrls)
    pm.sets(lowerBell_ctrls,name='lowerBellCtrls')
    
    return {'ctrls':lowerBell_ctrls, 'joints':lowerBell_joints}

def bell(all_ctrl):
    upper = upper_bell(all_ctrl)
    lower = lower_bell(all_ctrl)
    joints = [x.name() for x in upper['joints']]

    skin_dict[NAMESPACE][skin.SMOOTH].update(
            {NAMESPACE + 'innerDome': joints})

    joints = joints + [x.name() for x in lower['joints']]

    skin_dict[NAMESPACE][skin.SMOOTH].update(
            {NAMESPACE + 'headDome': joints})



def build():
    all_ctrl = blocks.Ctrl(name='all_ctrl', shape=Ctrl.CIRCLE, radius=20,
                        normal=[0,1,0],color=Ctrl.YELLOW, group=False).ctrl

    #
    # Inner Tentacles
    #

    inner_tentacles(all_ctrl)


    #
    # Outer Tentacles
    #
    outer_tentacles(all_ctrl)
    
    #
    # LOWER BELL
    #
    bell(all_ctrl)
    
    #
    # SKIN
    #
    skin.bind(skin_dict)

    # save skin dict
    utils.write_file('rigPirateCaptain_skin.json',skin_dict)
