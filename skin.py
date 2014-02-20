import pymel.core as pm

RIGID = 'rigid_bind'
SMOOTH= 'smooth_bind'
bind_post=""#this is a hack

def bind(skin_dict):
    unbind(skin_dict)
    for model,binds in skin_dict.iteritems():
        print model
        if RIGID in binds:
            for joint_,meshes in binds[RIGID].iteritems():
                joint_ = "%s%s" % (joint_,bind_post)
                meshes_named = []
                for mesh in meshes:
                    meshes_named.append("%s%s" % (model,mesh))
                try:
                    pm.bindSkin(joint_,meshes_named, toSelectedBones=True,
                            doNotDescend=True)
                except Exception as e:
                    print 'Rigid Bind:',e
                #print joint_, meshes_named
        if SMOOTH in binds:
            for mesh, joints in binds[SMOOTH].iteritems():
                #mesh = "%s%s" % (model,mesh)
                joints_named = []
                for joint_ in joints:
                    joints_named.append('%s%s' % (joint_,bind_post))
                try:
                    print 'mesh',mesh
                    #mesh = pm.select(mesh)
                    #print 'pmmesh',mesh
                    pm.skinCluster(
                            mesh,
                            joints_named,
                            toSelectedBones=True, 
                            maximumInfluences=len(joints_named))
                except Exception as e:
                    print 'Smooth Bind:',e
                #print mesh
                
def unbind(skin_dict):
    for model,binds in skin_dict.iteritems():
        print model
        if RIGID in binds:
            for joint_,meshes in binds[RIGID].iteritems():
                meshes_named = []
                for mesh in meshes:
                    meshes_named.append("%s%s" % (model,mesh))
                try:
                    pm.bindSkin(meshes_named, unbind=True)
                except Exception as e:
                    print 'Rigid Unbind:',e
                #print joint_, meshes_named
        if SMOOTH in binds:
            for mesh, joints in binds[SMOOTH].iteritems():
                try:
                    pm.skinCluster("%s%s" % (model,mesh),
                            edit=True,unbind=True)
                except Exception as e:
                    print 'Smooth Unbind:',e
                #print mesh
