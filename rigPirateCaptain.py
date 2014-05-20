import pymel.core as pm

import blocks
from blocks import RibbonIk, LinearSkin, Ctrl, ManDynHair, IkSpline, IkSC,\
                   InlineOffset, Lattice
import skin
import utils 
import defines
reload(utils)
#reload(blocks)
reload(skin)
reload(defines)

NAMESPACE = 'model:'

#
# Save the locators to file...just in case
#
loc_shapes = pm.ls(exactType='locator')
locs = [x.getParent() for x in pm.ls(exactType='locator')]
json = [utils.genNodeEntry(x) for x in locs]
utils.writeFile('rigPirateCaptain_locs.json',json)


ctrls = []
allCtrl = None
root = None

skinDict = {
        # namespace:{
        #   SMOOTH:{mesh:[joints,],},
        #   RIGID:{joint:[meshes,],}, }

        NAMESPACE:{
            skin.SMOOTH:{ },#SMOOTH
            skin.RIGID:{  },#RIGID
            },#'model:'
        }#skin_dict


innerTentacleLocs = [
        {'tentacleR1_ring_grp_0001':{
            'start_loc':'tentacleR1_ring_grp_0001_top_loc',
            'end_loc':'tentacleR1_ring_grp_0001_bottom_loc',
            'color':Ctrl.BLUE,
            'parent':'m_root_bind',}},
        {'tentacleR1_ring_grp_0002':{
            'start_loc':'tentacleR1_ring_grp_0002_top_loc',
            'end_loc':'tentacleR1_ring_grp_0002_bottom_loc',
            'color':Ctrl.RED,
            'parent':'m_root_bind',}},
        {'tentacleR1_grp_0003':{
            'start_loc':'tentacleR1_grp_0003_top_loc',
            'end_loc':'tentacleR1_grp_0003_bottom_loc',
            'color':Ctrl.RED,
            'parent':'m_root_bind',}},
        {'tentacleR1_grp_0004':{
            'start_loc':'tentacleR1_grp_0004_top_loc',
            'end_loc':'tentacleR1_grp_0004_bottom_loc',
            'color':Ctrl.BLUE,
            'parent':'m_root_bind',}},
        {'ringTentacleR2_grp_0001':{
            'start_loc':'ringTentacleR2_grp_0001_top_loc',
            'end_loc':'ringTentacleR2_grp_0001_bottom_loc',
            'color':Ctrl.RED,
            'parent':'m_root_bind',}},
        {'ringTentacleR2_grp_0002':{
            'start_loc':'ringTentacleR2_grp_0002_top_loc',
            'end_loc':'ringTentacleR2_grp_0002_bottom_loc',
            'color':Ctrl.BLUE,
            'parent':'m_root_bind',}},
        {'tentacleR3_grp_0001':{
            'start_loc':'tentacleR3_grp_0001_top_loc',
            'end_loc':'tentacleR3_grp_0001_bottom_loc',
            'color':Ctrl.YELLOW,
            'parent':'m_root_bind',}},
        {'tentacleR3_grp_0002':{
            'start_loc':'tentacleR3_grp_0002_top_loc',
            'end_loc':'tentacleR3_grp_0002_bottom_loc',
            'color':Ctrl.BLUE,
            'parent':'m_root_bind',}},
        {'tentacleR3_grp_0003':{
            'start_loc':'tentacleR3_grp_0003_top_loc',
            'end_loc':'tentacleR3_grp_0003_bottom_loc',
            'color':Ctrl.RED,
            'parent':'m_root_bind',}},
        ]

outerTentacleLocs = [
        # S1
        {'outerTentacleS1_0001':{
            'start_loc':'outerTentacleS1_0001_top_loc',
            'end_loc':'outerTentacleS1_0001_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd06_bind',}},
        {'outerTentacleS1_0002':{
            'start_loc':'outerTentacleS1_0002_top_loc',
            'end_loc':'outerTentacleS1_0002_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd11_bind',}},
        {'outerTentacleS1_0003':{
            'start_loc':'outerTentacleS1_0003_top_loc',
            'end_loc':'outerTentacleS1_0003_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd03_bind',}},
        {'outerTentacleS1_0004':{
            'start_loc':'outerTentacleS1_0004_top_loc',
            'end_loc':'outerTentacleS1_0004_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd30_bind',}},
        {'outerTentacleS1_0005':{
            'start_loc':'outerTentacleS1_0005_top_loc',
            'end_loc':'outerTentacleS1_0005_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd26_bind',}},
        {'outerTentacleS1_0006':{
            'start_loc':'outerTentacleS1_0006_top_loc',
            'end_loc':'outerTentacleS1_0006_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd13_bind',}},
        {'outerTentacleS1_0007':{
            'start_loc':'outerTentacleS1_0007_top_loc',
            'end_loc':'outerTentacleS1_0007_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd22_bind',}},
        {'outerTentacleS1_0008':{
            'start_loc':'outerTentacleS1_0008_top_loc',
            'end_loc':'outerTentacleS1_0008_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd16_bind',}},
        # S2
        {'outerTentacleS2_0001':{
            'start_loc':'outerTentacleS2_0001_top_loc',
            'end_loc':'outerTentacleS2_0001_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd04_bind',}},
        {'outerTentacleS2_0006':{
            'start_loc':'outerTentacleS2_0006_top_loc',
            'end_loc':'outerTentacleS2_0006_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd09_bind',}},
        {'outerTentacleS2_0007':{
            'start_loc':'outerTentacleS2_0007_top_loc',
            'end_loc':'outerTentacleS2_0007_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd05_bind',}},
        {'outerTentacleS2_0008':{
            'start_loc':'outerTentacleS2_0008_top_loc',
            'end_loc':'outerTentacleS2_0008_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd07_bind',}},
        {'outerTentacleS2_0009':{
            'start_loc':'outerTentacleS2_0009_top_loc',
            'end_loc':'outerTentacleS2_0009_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd02_bind',}},
        {'outerTentacleS2_0010':{
            'start_loc':'outerTentacleS2_0010_top_loc',
            'end_loc':'outerTentacleS2_0010_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd29_bind',}},
        {'outerTentacleS2_0011':{
            'start_loc':'outerTentacleS2_0011_top_loc',
            'end_loc':'outerTentacleS2_0011_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd27_bind',}},
        {'outerTentacleS2_0012':{
            'start_loc':'outerTentacleS2_0012_top_loc',
            'end_loc':'outerTentacleS2_0012_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd13_bind',}},
        {'outerTentacleS2_0013':{
            'start_loc':'outerTentacleS2_0013_top_loc',
            'end_loc':'outerTentacleS2_0013_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd11_bind',}},
        {'outerTentacleS2_0014':{
            'start_loc':'outerTentacleS2_0014_top_loc',
            'end_loc':'outerTentacleS2_0014_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd24_bind',}},
        {'outerTentacleS2_0015':{
            'start_loc':'outerTentacleS2_0015_top_loc',
            'end_loc':'outerTentacleS2_0015_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd21_bind',}},
        {'outerTentacleS2_0016':{
            'start_loc':'outerTentacleS2_0016_top_loc',
            'end_loc':'outerTentacleS2_0016_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd19_bind',}},
        {'outerTentacleS2_0017':{
            'start_loc':'outerTentacleS2_0017_top_loc',
            'end_loc':'outerTentacleS2_0017_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd15_bind',}},
        # S3
        {'outerTentacleS3_0001':{
            'start_loc':'outerTentacleS3_0001_top_loc',
            'end_loc':'outerTentacleS3_0001_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd01_bind',}},
        {'outerTentacleS3_0002':{
            'start_loc':'outerTentacleS3_0002_top_loc',
            'end_loc':'outerTentacleS3_0002_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd08_bind',}},
        {'outerTentacleS3_0003':{
            'start_loc':'outerTentacleS3_0003_top_loc',
            'end_loc':'outerTentacleS3_0003_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd10_bind',}},
        {'outerTentacleS3_0004':{
            'start_loc':'outerTentacleS3_0004_top_loc',
            'end_loc':'outerTentacleS3_0004_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd28_bind',}},
        {'outerTentacleS3_0005':{
            'start_loc':'outerTentacleS3_0005_top_loc',
            'end_loc':'outerTentacleS3_0005_bottom_loc',
            'color':Ctrl.NAVY,
            'parent':'lowerBellEnd25_bind',}},
        {'outerTentacleS3_0006':{
            'start_loc':'outerTentacleS3_0006_top_loc',
            'end_loc':'outerTentacleS3_0006_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd14_bind',}},
        {'outerTentacleS3_0007':{
            'start_loc':'outerTentacleS3_0007_top_loc',
            'end_loc':'outerTentacleS3_0007_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd23_bind',}},
        {'outerTentacleS3_0008':{
            'start_loc':'outerTentacleS3_0008_top_loc',
            'end_loc':'outerTentacleS3_0008_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd20_bind',}},
        {'outerTentacleS3_0009':{
            'start_loc':'outerTentacleS3_0009_top_loc',
            'end_loc':'outerTentacleS3_0009_bottom_loc',
            'color':Ctrl.BRICK,
            'parent':'lowerBellEnd17_bind',}},
        ]
lowerBellLocs = [
        {'lowerBell01_loc':{
            'color':Ctrl.BLUE,
            'parent':'m_root',}},
        {'lowerBell02_loc':{
            'color':Ctrl.BLUE,
            'parent':'m_root',}},
        {'lowerBell03_loc':{
            'color':Ctrl.BLUE,
            'parent':'m_root',}},
        {'lowerBell04_loc':{
            'color':Ctrl.YELLOW,
            'parent':'m_root',}},
        {'lowerBell05_loc':{
            'color':Ctrl.RED,
            'parent':'m_root',}},
        {'lowerBell06_loc':{
            'color':Ctrl.RED,
            'parent':'m_root',}},
        {'lowerBell07_loc':{
            'color':Ctrl.RED,
            'parent':'m_root',}},
        {'lowerBell08_loc':{
            'color':Ctrl.RED,
            'parent':'m_root',}},
        {'lowerBell09_loc':{
            'color':Ctrl.RED,
            'parent':'m_root',}},
        {'lowerBell10_loc':{
            'color':Ctrl.YELLOW,
            'parent':'m_root',}},
        {'lowerBell11_loc':{
            'color':Ctrl.BLUE,
            'parent':'m_root',}},
        {'lowerBell12_loc':{
            'color':Ctrl.BLUE,
            'parent':'m_root',}},
        ]
upperBellLocs = [
        # {'root_loc':{
        #     'color':Ctrl.YELLOW,
        #     'parent':None,}},
        {'upperBell_loc':{
            'color':Ctrl.YELLOW,
            'parent':'m_root_bind',}},
        ]
upperBellVerts = [
    pm.MeshVertex(u'model:headDomeShape.vtx[0:421]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[426:431]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[433:434]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[436:437]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[439:442]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[444:445]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[458:461]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[474:477]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[480:481]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[483:486]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[488:489]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[491:492]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[494:496]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[498]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[511:514]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[524:526]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[528:530]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[532:535]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[537:543]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[545:547]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[549:553]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[555:559]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[561:563]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[585:595]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[620:633]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[636:638]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[640:644]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[646:650]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[652:654]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[656:660]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[662:666]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[668:669]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[694:705]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[727:750]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[760:765]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[778:801]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[814:821]'), 
    pm.MeshVertex(u'model:headDomeShape.vtx[834:841]')
    ]

upperBellGeo = [
    pm.nt.Transform(u'model:innerDome'),
    pm.nt.Transform(u'model:headDome'),
    ]


def innerTentacles(allCtrl, rootCtrl):
    innerTentacleCtrls = []
    pm.addAttr(allCtrl, longName='innerTentacleGeo',
               attributeType='bool', defaultValue=True, keyable=True)
    pm.addAttr(allCtrl, longName='innerTentacleCtrls',
               attributeType='bool', defaultValue=True, keyable=True)
    for dict_ in innerTentacleLocs:
        group = dict_.keys()[0]
        attrs = dict_.values()[0]

        meshName = group.split('_')
        name = meshName[0] + meshName[-1]
        print "Building RibbonIK for", name
        ribbon = RibbonIk(
                startLoc = attrs['start_loc'], 
                endLoc = attrs['end_loc'],
                name = name + "_ribbonIk",
                numSpans = 9,
                numJoints = 20)
        print "Building Driver for", name
        drivers = LinearSkin(
                mesh = ribbon.ribbonIkPlane,
                startLoc = attrs['start_loc'], 
                endLoc = attrs['end_loc'],
                numControls = 6,
                name = name,
                controlColor = attrs['color'],
                parent = attrs['parent'])
        innerTentacleCtrls.extend(drivers.controls)

        geoGrp = "%s%s" % (NAMESPACE,group)
        geo = pm.listRelatives(geoGrp, children=True, path=True)
        joints = [x.name() for x in ribbon.bindJoints]
        for node in geo:
            skinDict[NAMESPACE][skin.SMOOTH].update(
                    {node.name():joints})
        ctrlGrp = pm.group(ribbon.ribbonIkPlane, 
                            drivers.controls[0], name='%s_ctrlGrp' % group)
        ribbon.follicleGrp.setParent(ctrlGrp)
        ctrlGrp.setParent(rootCtrl.controls[0])
        allCtrl.innerTentacleGeo >> pm.PyNode(NAMESPACE+group).visibility
        for joint in ribbon.bindJoints:
            allCtrl.innerTentacleCtrls >> joint.visibility

    for ctrl in innerTentacleCtrls:
        allCtrl.innerTentacleCtrls >> ctrl.visibility

    ctrls.extend(innerTentacleCtrls)
    pm.sets(innerTentacleCtrls,name="innerTentacleCtrls")

def outerTentacles(allCtrl):
    pm.addAttr(allCtrl, longName='outerTentacleGeo',
               attributeType='bool', defaultValue=True, keyable=True)
    hairSys = None
    outerTentacleCtrls = []
    for dict_ in outerTentacleLocs:
        # get the names
        mesh = dict_.keys()[0]
        attrs = dict_.values()[0]

        name = mesh.split('_')
        name = name[0] + name[-1]

        # build the rig
        print "Building Spline for",name
        spline = IkSpline(
                startLoc = attrs['start_loc'],
                endLoc = attrs['end_loc'],
                name = name + '_spline',
                numSpans = 10,
                numJoints = 20)
        joints = [x.name() for x in spline.joints]

        print "Building ManDynHair for",name
        mdhair = ManDynHair(
                curve = spline.ikCrv,
                startLoc = spline.startLoc,
                endLoc = spline.endLoc,
                numControls = 5,
                name = name,
                controlColor = attrs['color'],
                hairSystem = hairSys,
                controlRadius = 1)
        hairSys = mdhair.hairSystem

        outerTentacleCtrls.extend(mdhair.controls)

        # update the skinning dict
        mesh = NAMESPACE + mesh
        skinDict[NAMESPACE][skin.SMOOTH].update(
                {mesh:joints})

        # set geo.visibility to ctrl.visibiltiy
        mdhair.controls[0].visibility >> pm.PyNode(mesh).visibility

        # group everything together
        ctrlGrp = pm.group(
                spline.joints[0],spline.ikCrv, spline.ikHandle,
                mdhair.manCrv, mdhair.dynOutCrv, mdhair.controls[0],
                mdhair.follicle,
                name = '%s_ctrlGrp' % name)
        ctrlGrp.setParent(attrs['parent'])

        allCtrl.outerTentacleGeo >> pm.PyNode(mesh).visibility

    pm.addAttr(allCtrl, longName='outerTentacleCtrls',
               attributeType='bool', defaultValue=True, keyable=True)
    for ctrl in outerTentacleCtrls:
        allCtrl.outerTentacleCtrls >> ctrl.visibility
    
    ctrls.extend(outerTentacleCtrls)
    pm.sets(outerTentacleCtrls,name="outerTentacleCtrls")

def upperBell(allCtrl, rootCtrl):
    upperBellCtrls = []
    upperBellJoints = []

    upperBellJoints.append(rootCtrl.joints[0])

    #
    lattice = Lattice(
            geometry = [upperBellVerts, upperBellGeo[0]],
            latticeDivisions = [5,5,5],
            name = 'upperBellLattice',
            parent = rootCtrl.controls[0]
            )
    # pm.select(upperBellVerts, upperBellGeo)
    # lattice = pm.nt.Lattice(objectCentered=True, divisions=[5,5,5])

    print lattice.lattice
    upperBellCtrls.extend(lattice.controls)

    return {'ctrls':upperBellCtrls, 'joints':upperBellJoints}


def lowerBell(allCtrl):
    lowerBellCtrls = []
    lowerBellJoints = []
    for dict_ in lowerBellLocs:
        loc = dict_.keys()[0]
        attrs = dict_.values()[0]

        name = loc.split('_')[0]
        loc = pm.PyNode(loc)
                
        parentJoint = utils.placeXform(name=name + '_%s' % defines.BIND, 
                                       mtype='joint',
                                       matrix=loc.getMatrix(worldSpace=True),
                                       worldSpace=True)
        parent = attrs['parent']
        if parent:
            parent = parent + '_%s' % defines.BIND
        parentJoint.setParent(parent)
        parentCtrl = InlineOffset(
                parentJoint, controlRadius=1, controlShape='circle',
                controlColor=attrs['color']).controls[0]
        lowerBellCtrls.append(parentCtrl)
        lowerBellJoints.append(parentJoint)
        children = loc.listRelatives(children=True, type='transform')
        for endloc in children:
            endname = endloc.name().split('_')[0]
            endjoint = utils.placeXform(
                    name=endname+'_%s'%defines.BIND,mtype='joint',
                    matrix=endloc.getMatrix(worldSpace=True),
                    worldSpace=True)
            ikjoint = pm.duplicate(
                    parentJoint,
                    name=endname+'_%s'%(defines.IK+defines.JOINT.title()),
                    parentOnly=True)[0]
            ikjoint = pm.PyNode(ikjoint)
            ikjoint.setParent(parentJoint)
            endjoint.setParent(ikjoint)
            ik = IkSC(startJoint=ikjoint, endJoint=endjoint, 
                      name=endname, controlColor=attrs['color'], 
                      controlRadius=0.5)
            lowerBellCtrls.extend(ik.controls)
            ik.controls[0].getParent().setParent(parentJoint)

            lowerBellJoints.append(endjoint)

    pm.addAttr(allCtrl, longName='lowerBellCtrls',
               attributeType='bool', defaultValue=True, keyable=True)
    for ctrl in lowerBellCtrls:
        allCtrl.lowerBellCtrls >> ctrl.visibility

    ctrls.extend(lowerBellCtrls)
    pm.sets(lowerBellCtrls,name='lowerBellCtrls')
    
    return {'ctrls':lowerBellCtrls, 'joints':lowerBellJoints}

def bell(allCtrl, rootCtrl):
    upper = upperBell(allCtrl, rootCtrl)
    lower = lowerBell(allCtrl)
    joints = [x.name() for x in upper['joints']]

    skinDict[NAMESPACE][skin.SMOOTH].update(
            {NAMESPACE + 'innerDome': joints})

    joints = joints + [x.name() for x in lower['joints']]

    skinDict[NAMESPACE][skin.SMOOTH].update(
            {NAMESPACE + 'headDome': joints})

def build():
    allCtrl = blocks.Ctrl(name='all_ctrl', shape=Ctrl.CIRCLE, radius=20,
                          normal=[0,1,0], color=Ctrl.YELLOW, group=False).ctrl
    rootLoc = pm.PyNode('root_loc')
    rootJoint = utils.placeXform(name="m_root_%s" % defines.BIND, mtype='joint',
                                  matrix=rootLoc.getMatrix(worldSpace=True),
                                  worldSpace=True, parent=allCtrl)
    rootCtrl = InlineOffset(
                     rootJoint, name='m_root_%s' % defines.CTRL,
                     controlShape=Ctrl.CIRCLE, controlRadius=15,
                     controlColor=Ctrl.YELLOW)

    #
    # Inner Tentacles
    #

    innerTentacles(allCtrl, rootCtrl)

    #
    # LOWER BELL
    #
    bell(allCtrl, rootCtrl)
    
    #
    # Outer Tentacles
    #
    outerTentacles(allCtrl)
    
    #
    # SKIN
    #
    skin.bind(skinDict)

    pm.PyNode(u'upperBellLatticeBase').setParent(rootCtrl.controls[0])

    upperBellDefVerts = [MeshVertex(u'headDomeShapeDeformed.vtx[0:421]'), MeshVertex(u'headDomeShapeDeformed.vtx[426:431]'), MeshVertex(u'headDomeShapeDeformed.vtx[433:434]'), MeshVertex(u'headDomeShapeDeformed.vtx[436:437]'), MeshVertex(u'headDomeShapeDeformed.vtx[439:442]'), MeshVertex(u'headDomeShapeDeformed.vtx[444:445]'), MeshVertex(u'headDomeShapeDeformed.vtx[458:461]'), MeshVertex(u'headDomeShapeDeformed.vtx[474:477]'), MeshVertex(u'headDomeShapeDeformed.vtx[480:481]'), MeshVertex(u'headDomeShapeDeformed.vtx[483:486]'), MeshVertex(u'headDomeShapeDeformed.vtx[488:489]'), MeshVertex(u'headDomeShapeDeformed.vtx[491:492]'), MeshVertex(u'headDomeShapeDeformed.vtx[494:496]'), MeshVertex(u'headDomeShapeDeformed.vtx[498]'), MeshVertex(u'headDomeShapeDeformed.vtx[511:514]'), MeshVertex(u'headDomeShapeDeformed.vtx[524:526]'), MeshVertex(u'headDomeShapeDeformed.vtx[528:530]'), MeshVertex(u'headDomeShapeDeformed.vtx[532:535]'), MeshVertex(u'headDomeShapeDeformed.vtx[537:543]'), MeshVertex(u'headDomeShapeDeformed.vtx[545:547]'), MeshVertex(u'headDomeShapeDeformed.vtx[549:553]'), MeshVertex(u'headDomeShapeDeformed.vtx[555:559]'), MeshVertex(u'headDomeShapeDeformed.vtx[561:563]'), MeshVertex(u'headDomeShapeDeformed.vtx[585:595]'), MeshVertex(u'headDomeShapeDeformed.vtx[620:633]'), MeshVertex(u'headDomeShapeDeformed.vtx[636:638]'), MeshVertex(u'headDomeShapeDeformed.vtx[640:644]'), MeshVertex(u'headDomeShapeDeformed.vtx[646:650]'), MeshVertex(u'headDomeShapeDeformed.vtx[652:654]'), MeshVertex(u'headDomeShapeDeformed.vtx[656:660]'), MeshVertex(u'headDomeShapeDeformed.vtx[662:666]'), MeshVertex(u'headDomeShapeDeformed.vtx[668:669]'), MeshVertex(u'headDomeShapeDeformed.vtx[694:705]'), MeshVertex(u'headDomeShapeDeformed.vtx[727:750]'), MeshVertex(u'headDomeShapeDeformed.vtx[760:765]'), MeshVertex(u'headDomeShapeDeformed.vtx[778:801]'), MeshVertex(u'headDomeShapeDeformed.vtx[814:821]'), MeshVertex(u'headDomeShapeDeformed.vtx[834:873]'), MeshVertex(u'headDomeShapeDeformed.vtx[922:953]'), MeshVertex(u'headDomeShapeDeformed.vtx[1002:1105]'), MeshVertex(u'headDomeShapeDeformed.vtx[1154:1177]'), MeshVertex(u'headDomeShapeDeformed.vtx[1214:1296]'), MeshVertex(u'headDomeShapeDeformed.vtx[1339:1362]'), MeshVertex(u'headDomeShapeDeformed.vtx[1411:1414]'), MeshVertex(u'headDomeShapeDeformed.vtx[1417:1427]'), MeshVertex(u'headDomeShapeDeformed.vtx[1430:1441]'), MeshVertex(u'headDomeShapeDeformed.vtx[1444:1449]'), MeshVertex(u'headDomeShapeDeformed.vtx[1452:1463]'), MeshVertex(u'headDomeShapeDeformed.vtx[1466:1477]'), MeshVertex(u'headDomeShapeDeformed.vtx[1480:1485]'), MeshVertex(u'headDomeShapeDeformed.vtx[1490:1517]'), MeshVertex(u'headDomeShapeDeformed.vtx[1566:1587]'), MeshVertex(u'headDomeShapeDeformed.vtx[1630:1635]'), MeshVertex(u'headDomeShapeDeformed.vtx[1638:1649]'), MeshVertex(u'headDomeShapeDeformed.vtx[1652:1663]'), MeshVertex(u'headDomeShapeDeformed.vtx[1666:1671]'), MeshVertex(u'headDomeShapeDeformed.vtx[1674:1691]'), MeshVertex(u'headDomeShapeDeformed.vtx[1694:1701]'), MeshVertex(u'headDomeShapeDeformed.vtx[1704:1709]'), MeshVertex(u'headDomeShapeDeformed.vtx[1712:2583]'), MeshVertex(u'headDomeShapeDeformed.vtx[2632:2663]'), MeshVertex(u'headDomeShapeDeformed.vtx[2712:2823]'), MeshVertex(u'headDomeShapeDeformed.vtx[2872:2895]'), MeshVertex(u'headDomeShapeDeformed.vtx[2932:3361]')]

    pm.skinPercent('skinCluster84', upperBellDefVerts, 
                   transformValue = [(rootJoint,1.0)])
    pm.reorderDeformers(u'upperBellLattice',u'skinCluster84',
                        u'model:headDome')
    pm.reorderDeformers(u'upperBellLattice',u'skinCluster48',
                        u'model:innerDome')

    # save skin dict
    utils.writeFile('rigPirateCaptain_skin.json',skinDict)
