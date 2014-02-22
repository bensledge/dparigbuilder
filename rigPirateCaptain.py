import pymel.core as pm

from ribbonIk import RibbonIk, LinearSkin, Ctrl
import skin
reload(ribbonIk)
reload(skin)

NAMESPACE = 'surface:model:'

ctrls = []

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
            'end_loc'  :'tentacleR1_ring_grp_0001_bottom_loc',
            'color'    : Ctrl.BLUE,}},
        {'tentacleR1_ring_grp_0002':{
            'start_loc':'tentacleR1_ring_grp_0002_top_loc',
            'end_loc'  :'tentacleR1_ring_grp_0002_bottom_loc',
            'color'    : Ctrl.RED,}},
        {'tentacleR1_grp_0003':{
            'start_loc':'tentacleR1_grp_0003_top_loc',
            'end_loc'  :'tentacleR1_grp_0003_bottom_loc',
            'color'    : Ctrl.RED,}},
        {'tentacleR1_grp_0004':{
            'start_loc':'tentacleR1_grp_0004_top_loc',
            'end_loc'  :'tentacleR1_grp_0004_bottom_loc',
            'color'    : Ctrl.BLUE,}},
        {'ringTentacleR2_grp_0001':{
            'start_loc':'ringTentacleR2_grp_0001_top_loc',
            'end_loc'  :'ringTentacleR2_grp_0001_bottom_loc',
            'color'    : Ctrl.RED,}},
        {'ringTentacleR2_grp_0002':{
            'start_loc':'ringTentacleR2_grp_0002_top_loc',
            'end_loc'  :'ringTentacleR2_grp_0002_bottom_loc',
            'color'    : Ctrl.BLUE,}},
        {'tentacleR3_grp_0001':{
            'start_loc':'tentacleR3_grp_0001_top_loc',
            'end_loc'  :'tentacleR3_grp_0001_bottom_loc',
            'color'    : Ctrl.YELLOW,}},
        {'tentacleR3_grp_0002':{
            'start_loc':'tentacleR3_grp_0002_top_loc',
            'end_loc'  :'tentacleR3_grp_0002_bottom_loc',
            'color'    : Ctrl.BLUE,}},
        {'tentacleR3_grp_0003':{
            'start_loc':'tentacleR3_grp_0003_top_loc',
            'end_loc'  :'tentacleR3_grp_0003_bottom_loc',
            'color'    : Ctrl.RED,}},
        ]

def build():
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

        groupname = "%s%s" % (NAMESPACE,group)
        geo = pm.listRelatives(groupname, children=True, path=True)
        joints = [x.name() for x in ribbon.bind_joints]
        for node in geo:
            skin_dict[NAMESPACE][skin.SMOOTH].update(
                    {node.name():joints})


    ## SKIN
    print skin_dict
    skin.bind(skin_dict)




            


