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
        {'outerTentacleS3_0001':{
            'start_loc':'outerTentacleS3_0001_top_loc',
            'end_loc':'outerTentacleS3_0001_bottom_loc',
            'color':Ctrl.RED,
            'parent':None,}},
        ]

def build():
    innerTentacle_locs = [] #TODO: take this out
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
        ctrls.append(drivers.controls)

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


    hair_sys = None
    for dict_ in outerTentacle_locs:
        # get the names
        mesh = dict_.keys()[0]
        attrs = dict_.values()[0]

        name = mesh.split('_')
        name = name[0] + name[-1]

        # build the rig
        spline = IkSpline(
                start_loc = attrs['start_loc'],
                end_loc = attrs['end_loc'],
                name = name + '_spline',
                num_spans = 10,
                num_joints = 10)
        joints = [x.name() for x in spline.joints]

        mdhair = ManDynHair(
                curve = spline.ik_crv,
                start_loc = spline.start_loc,
                end_loc = spline.end_loc,
                num_ctrls = 5,
                name = name,
                color = attrs['color'],
                hair_system = hair_sys)
        hair_sys = mdhair.hair_system

        ctrls.append(mdhair.controls)

        # update the skinning dict
        mesh = NAMESPACE + mesh
        skin_dict[NAMESPACE][skin.SMOOTH].update(
                {mesh:joints})

        # group everything together
        ctrl_grp = pm.group(
                spline.joints[0],spline.ik_crv, spline.ik_handle,
                mdhair.man_crv, mdhair.dyn_out_crv, mdhair.controls[0],
                mdhair.follicle,
                name = '%s_ctrlGrp' % name)
        ctrl_grp.setParent(all_ctrl)

    ## SKIN
    print skin_dict
    skin.bind(skin_dict)

    # save skin dict
    utils.write_file('rigPirateCaptain_skin.json',skin_dict)
