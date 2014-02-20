import pymel.core as pm
import utils as u
reload(u) #TODO: remove in production
import baseBlock as b
reload(b)

PREFERED_ANGLE = (0.0, 0.20, 0.0)

class Solo(b.Block):
    '''A solo joint'''

    def __init__(self, joints, name="solo", side='m', postfix="solo",
            rig_node=None, plug=None, radius=4.0, ctrl_normal=[0,1,0]):
        super(Solo,self).__init__(joints, name, side, 
                postfix, rig_node, plug)
        self.sockets = ['base',]
        self.radius  = radius
        self.normal  = ctrl_normal

    def _load_template(self,joints):
        template = dict()
        joints = u.to_pm_nodes(joints)

        parent = None
        key = 'base'
        template = {key  :{'injoint':joints[0],'parent':parent,},}

        return template

    def get_socket(self,key=None):
        '''return the socket'''
        return self.template[self.sockets[0]]['injoint']
    
    def build(self):

        solo_ctrl = "%s_ctrl" % (self.template['base']['injoint'])
        solo_ctrl = self._make_ctrl(
                name    = solo_ctrl,
                radius  = self.radius,
                normal  = self.normal)
        solo_ctrlGrp = pm.group(
                solo_ctrl,
                world=True,
                name = solo_ctrl.name() + "Grp")
        u.snap_to(guide = self.template['base']['injoint'],
                  nodes = solo_ctrlGrp)
        solo_ctrlGrp.setParent(self.plug)

        self.template['base'].update({
                'ctrlGrp': solo_ctrlGrp,
                'ctrl'   : solo_ctrl,  })
        self.template['base']['injoint'].setParent(
                self.template['base']['ctrl'])


    def destroy(self):
        pm.delete(self.template['base']['name'])
