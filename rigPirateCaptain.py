import pymel.core as pm

import blocks
from blocks import RibbonIk, LinearSkin, Ctrl, ManDynHair, IkSpline
import skin
import utils 
reload(utils)
reload(blocks)
reload(skin)

NAMESPACE = 'surface:model:'

ctrls = []
all_ctrl = blocks.Ctrl(name='all_ctrl', shape=Ctrl.CIRCLE, radius=20,
                       normal=[0,1,0],color=Ctrl.YELLOW, group=False).ctrl

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
        {'outerTentacleS2_00010':{
            'start_loc':'outerTentacleS2_0010_top_loc',
            'end_loc':'outerTentacleS2_0010_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_00011':{
            'start_loc':'outerTentacleS2_0011_top_loc',
            'end_loc':'outerTentacleS2_0011_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_00012':{
            'start_loc':'outerTentacleS2_0012_top_loc',
            'end_loc':'outerTentacleS2_0012_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_00013':{
            'start_loc':'outerTentacleS2_0013_top_loc',
            'end_loc':'outerTentacleS2_0013_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_00014':{
            'start_loc':'outerTentacleS2_0014_top_loc',
            'end_loc':'outerTentacleS2_0014_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':None,}},
        {'outerTentacleS2_00015':{
            'start_loc':'outerTentacleS2_0015_top_loc',
            'end_loc':'outerTentacleS2_0015_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_00016':{
            'start_loc':'outerTentacleS2_0016_top_loc',
            'end_loc':'outerTentacleS2_0016_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':None,}},
        {'outerTentacleS2_00017':{
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

def build():

    #
    # Inner Tentacles
    #

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




    #
    # Outer Tentacles
    #

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

    #
    # SKIN
    #
    skin.bind(skin_dict)

    # save skin dict
    utils.write_file('rigPirateCaptain_skin.json',skin_dict)
