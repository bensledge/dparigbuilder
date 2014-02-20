import json

import pymel.core as pm
import utils as u
reload(u) #TODO: remove in production

class Block(object):
    '''Defines a rig block'''
    
    ##  Initiate the block
    #
    def __init__(self, joints, name, side, postfix, rig_node=None, 
            plug=None, *args, **kwargs):
        self.name       = name    ##  the name of the rig block
        ##  the template to build joints from
        self.plug       = plug    ##  points to the parent "socket" block
        self.template   = self._load_template(joints) 
        self.side       = side    ##  the side of the body
        self.postfix    = postfix ##  the postfix for nodes created
        self.rig_node   = rig_node##  the dparignode for this block
        self.sockets    = []      ##  nodes plugs go into 
        self.controllers= []      ##  the controls created with this block

    def _load_template(self,joints,*args,**kwargs):
        '''loads the template from a list of joints'''
        raise NotImplementedError
        
        # what you do here is up to you (thanks Python)
        # ...but for the love of god,
        # make sure you have at least this included 
        # (it breaks shit if you don't)
        template = {key : {
            'injoint':joint,    ## the input, "bind" joint
            'parent':parent,    ## the parent node
            'ctrl':None,        ## the control (if any)
            'ctrlGrp':None,     ## the group the control is in (if any)
            'rigjoint':None,    ## the driver joint
            }, }        
        self.sockets = [key, ]  ## a list of keys into the template
        return template

    def _place_joint(self,name,position,parent=None):
        '''place a joint in the scene'''
        joint = pm.joint(name=name, position=(0,0,0))
        joint.setTranslation(position, 'world')
        joint.setParent(parent)
        return joint

    def _make_ctrl(self,name, radius=1.0, normal=[1,0,0]):
        '''makes a controller at the origin'''
        ctrl = pm.circle(
                #constructionHistory=True,
                object=True,
                name=name,
                normal=normal,
                radius=radius)[0]
        return ctrl
        
    def _constrain_bind(self,*args,**kwargs):
        '''attaches the rig to the bind skeleton'''
        print 'constrain_bind'
        constraints = []
        for key in self.template.keys():
            constraint = pm.orientConstraint(
                self.template[key]['rigjoint'],
                self.template[key]['injoint'],
                name = "%s_orCnst" % \
                        (self.template[key]['injoint'].name()))
            constraints.append(constraint)
        return constraints

    def _build_rig_joints(self,*args,**kwargs):
        '''build the rig joints'''
        for key, joint in self.template.iteritems():
            name = joint['injoint'].name()
            name = name.rpartition('_')[0] + '_' + self.postfix
            j    = pm.duplicate(joint['injoint'],
                    name=name, parentOnly=True)[0]
            #u.snap_to(joint['injoint'], j)
            name = j.name()
            self.template[key].update({
                'name':name,
                'rigjoint':j,
                })

    def _parent_rig_joints(self,key='rigjoint',childkey=None, 
            parentkey=None,*args,**kwargs):
        
        if parentkey == None:
            parentkey = key
        if childkey  == None:
            childkey  = key

        '''parent the rig joints'''
        for joint in self.template.values():
            if joint['parent'] != None:
                joint[childkey].setParent(
                        self.template[joint['parent']][parentkey])
            else:
                if self.plug:
                    joint[childkey].setParent(self.plug)

    def build(self,*args,**kwargs):
        '''build the rig'''
        raise NotImplementedError

    def get_socket(self,key=None):
        '''return the socket for downstream nodes to connect to'''
        if key == None:
            print 'sockets',self.sockets[0]
            return self.template[self.sockets[0]]['rigjoint']

    def destroy(self,*args,**kwargs):
        '''remove the rig from the scene'''
        raise NotImplementedError

class RigBase(Block):
    '''defines the base rig'''
    
    ##  initiate
    def __init__(self,name,template,rig_node=None,plug=None,
            *args, **kwargs):
        self.name       = name
        self.side       = 'm'
        self.postfix    = 'bind'
        self.rig_node   = rig_node
        self.plug       = plug
        self.template   = template
        self.joints     = []
        self.controllers= []
        self.sockets    = []

    def get_socket(self,key=None):
        '''return the socket'''
        return self.sockets[0]

    def build(self):
        '''builds a basic bind skeleton in the scene'''

        # make the all ctrl
        all_ctrl = self._make_ctrl(
                name    = 'm_all_ctrl',
                normal  = [0,1,0],
                radius  = 5.0     )
        self.controllers.append(all_ctrl)
        self.sockets.append(all_ctrl)

        stack = []
        parent = all_ctrl
        if self.template != []:
            children = self.template.template
        else:
            children = []
        stack.append((children,parent))
        while stack:
            children,parent = stack.pop()
            for child in children:
                name = u.repostfix(child['name'],
                        newpost=self.postfix,oldpost='loc',commit=False)
                name = name[child['name']]
                joint = self._place_joint(
                        name        = name,
                        position    = child['position'],
                        parent      = parent)
                if child['children']:
                    stack.append((child['children'],joint))
                self.joints.append(joint)

        # orient joints
        for j in self.joints:
            side = j.name().split('_',1)[0]
            u.orient_joint(j,side)


    def destoy(self):
        '''removes the rig from the scene'''
        try:
            pm.delete(self.joints)
        except Exception as e:
            print e
