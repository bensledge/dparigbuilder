import pymel.core as pm

from ribbonIk import RibbonIk, LinearSkin
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
        ['tentacleR1_ring_grp_0001_top_loc','tentacleR1_ring_grp_0001_bottom_loc'],
        ]

def build():
    for i,locpair in enumerate(innerTentacle_locs):
        name   = locpair[0].split('_')
        name   = name[0] + name[3]
        print "Building RibbonIK for", name
        ribbon = RibbonIk(
                start_loc = locpair[0], 
                end_loc   = locpair[1],
                name      = name + "_ribbonIk",
                num_spans = 9,
                num_joints= 20)
        print "Building Driver for", name
        drivers = LinearSkin(
                mesh = ribbon.ribbonIkPlane,
                start_loc = locpair[0],
                end_loc   = locpair[1],
                num_ctrls = 6,
                name = name)
        ctrls.append(drivers.controls)
        mesh_name = locpair[0].split('_')
        groupname = "%s%s_%s_%s_%s" % (
                NAMESPACE,
                mesh_name[0],mesh_name[1],mesh_name[2],mesh_name[3])
        geo = pm.listRelatives(groupname, children=True, path=True)
        print geo
        joints = [x.name() for x in ribbon.bind_joints]
        print joints
        for node in geo:
            skin_dict[NAMESPACE][skin.SMOOTH].update(
                    {node.name():joints})


    ## SKIN
    print skin_dict
    skin.bind(skin_dict)




            


