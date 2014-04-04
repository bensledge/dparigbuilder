import json

import pymel.core as pm
import defines
reload(defines)

#import soloBlock as sb
#reload(sb)

JSON_INDENT = 0

# joint orientation
PRIMARY_AXIS    = 'xzy'
L_SECONDARY_AXIS= 'zdown'
M_SECONDARY_AXIS= 'zdown'
R_SECONDARY_AXIS= 'zdown'



##  Creates the entry for a xform node in a dict-recursively grabs children.
#   @param node The 'root' node to start at.
def gen_node_entry(node):
    node = pm.PyNode(node)
    if type(node) != pm.nodetypes.Transform:
        raise TypeError, "must be xform node"

    parent = node.getParent()
    if parent: parent = parent.name()

    entry = {
            'name': node.name(),
            'type': node.type(),
            'matrix':node.getMatrix(worldSpace=True).formated(),
            'parent':parent,
            }
    return entry

##  Build a dict of joint information keyed on joint name
#   @param nodes A list of nodes to create dicts for
def build_nodes_dict(nodes):
    node_list = []
    for node in nodes:
        node_list.append(gen_node_entry(node))
    return node_list

##  Write data to a file
#   Uses JSON to pickle and write a file
#   @param path Path to write to
#   @param data The data to write out
def write_file(path,data):
    fn = open(path,'w')
    json.dump(data,fn,indent=JSON_INDENT)
    fn.close()

##  Returns the current selection in Maya
#   @param mtype Type of object to return (default: 'transform')
def get_selected(mtype='transform'):
    sel = pm.ls(selection=True,type=mtype)
    if not sel:
        raise RuntimeError, 'No %s selected.' % mtype
    return sel

##  Read in a file and return a dictionary of its contents
#   Uses JSON to read file
#   @param path Path to read from
def read_file(path):
    fn = open(path,'r')
    data = json.load(fn)
    fn.close()
    return data

##  Adds a postfix node in Maya
#   @param nodes (None) nodes to rename (if None, query selection)
#   @param strpost (None) string to add as a postfix
#   @param mtype ('transform') node type to rename
#   @param recursive (True) if false will not rename children
#   
#   @return The name of the last node renamed
def postfix(nodes=None, strpost=None, mtype='transform'):
    if node == None:
        node = get_selected(mtype)

    newname=''
    for node in nodes:
        newname = pm.rename(node, "%s%s" % (node, strpost))
    return newname

##  changes the last token of a name to the given string
#   @param node (None) nodes to rename (if None, query selection)
#   @param newpost (None) the new postfix
#   @param oldpost (None) the postfix to replace (will ignore others)
#   @param mtype ('transform') node type to rename
#   @param commit ('True') rename the node in the scene (or not)
#
#   @return a dict of {old node : new node}'s
def repostfix(nodes=None, newpost=None, oldpost=None, 
        mtype='transform',commit=True):
    if nodes == None:
        node = get_selected()

    if type(nodes) != list:
        nodes = [nodes]

    renamed = dict()

    for node in nodes:
        oldname= node.name() if type(node) != unicode else node
        name = ''
        if type(node) == unicode:
            tokens = node.split('_')
        else:
            tokens = node.name().split('_')

        if oldpost != None:
            if tokens[-1] != oldpost:
                tokens.append(oldpost)

        tokens[-1] = newpost
        for t in tokens:
            name += t + '_'
        name = name[:-1]
        if commit:
            name = pm.rename(node, '%s' % (name))

        if type(node) != unicode:
            node = node.name()

        renamed.update({oldname:name})
    return renamed


def repostfix_hierarchy(nodes=None, newpost=None, oldpost=None, 
        mtype='transform'):
    if nodes == None:
        nodes = get_selected(mtype=mtype)

    renamed = dict()
    for node in nodes:
        renamed.update(repostfix([node], newpost, oldpost, mtype))
        
        for n in renamed.values():
            descendents = n.listRelatives(allDescendents=True,type=mtype)
            renamed.update(repostfix(descendents, newpost, oldpost, mtype))

    return renamed

##  matches one object's position and rotation to another(s)
#   @param guide ('None') node to match, if None queries selection
#   @param nodes ('None') nodes to move, if None queries selection
#   @param mtype ('transform') type of nodes to move
#
#   if guide and nodes are both None, guide will be the first selected
def snap_to(guide=None, nodes=None, mtype='transform'):
    if nodes == None:
        nodes = get_selected(mtype)

    if type(nodes) != list:
        nodes = [nodes]

    matrix = guide.getTransformation()

    if guide == None:
        if len(nodes) < 2:
            raise RuntimeError, 'Select at least two %s nodes' % (mtype)
        guide = nodes[0]
        nodes = nodes[1:]

    for node in nodes:
        node.setTransformation(matrix)
        ptcnt = pm.pointConstraint(guide, node, name='st_ptcnt')
        pm.delete(ptcnt)
        orcnt = pm.orientConstraint(guide, node, name='st_orcnt')
        pm.delete(orcnt)

##  gets the worldspace coords of a transform
#   @param node ('None') node to get location of, if None queries selection
def get_ws_location(node=None,mtype='transform'):
    if node == None:
        node = get_selected(mtype)[0]

    node = pm.PyNode(node)
        
    return pm.xform(node, query=True, worldSpace=True, rotatePivot=True)

##  create pm objects for the given list of nodes
#   @param nodes ('None') nodes to create objects for if None query selected
def toPmNodes(nodes=None,mtype='transform'):
    if nodes == None:
        nodes = get_selected(mtype)

    if type(nodes) != list:
        nodes = [nodes]

    pmnodes = []
    for n in nodes:
        if type(n) != unicode:
            listn = pm.ls(n)
            pmnodes.append(listn[0])
        else:
            pmnodes.append(n)

    return pmnodes

##  standard way to orient joints in the scene
#   @param joint joint to orient
#   @param side ('l') side of the body the joint is on [l|r|m]
def orient_joint(joint,side='l'):
    if type(joint) != list:
        joint = [joint]

    for j in joint:
        try:
            if   side == 'l':
                j.orientJoint(PRIMARY_AXIS, 
                        secondaryAxisOrient = L_SECONDARY_AXIS)
            elif side == 'r':
                j.orientJoint(PRIMARY_AXIS, 
                        secondaryAxisOrient = R_SECONDARY_AXIS)
            elif side == 'm':
                j.orientJoint(PRIMARY_AXIS, 
                        secondaryAxisOrient = M_SECONDARY_AXIS)

        except Exception as e:
            print 'Could not orient joint %s (probably a leaf node): %s' \
                    % (j,e)

##  connect attributes from one node to another
#   @param outnode   node that drives the other node
#   @param innode    node that gets driven
#   @param attr      attr to connect (string)
def connect_attr(outnode, innode, attr):
    if type(attr) != list:
        attr = [attr]

    for a in attr:
        pm.connectAttr("%s.%s" % (outnode,a),
                       "%s.%s" % (innode, a))
"""
##  create solo blocks from a list
#   @param joints   ('None') list of joints to create blocks for
#   @return         list of blocks created
def make_solo_blocks(joints=None,radius=1.0,ctrl_normal=[0,1,0],mtype='transform'):
    if joints == None:
        joints = get_selected(mtype)

    if type(joints) != list:
        joints = [joints]

    joints = to_pm_nodes(joints)

    blocks = []

    for j in joints:
        name = j.name().split("_")
        side = name[0]
        name = "%s_%s" % (name[0],name[1])
        socket = j.listRelatives(parent=True)

        block = sb.Solo(
                name=name,joints=[j],side=side,plug=socket,radius=radius)
        block.build()
        blocks.append(block)

    return blocks
"""
def get_nurbs_shapes(nodes=None,mtype='transform'):
    '''Returns the nurbs shapes of a transform node'''
    if nodes == None:
        nodes = get_selected(mtype)

    if type(nodes) != list:
        nodes = [nodes]

    shapes = []
    for n in nodes:
        shape = False
        if type(n) == 'unicode':
            n = to_pm_nodes(n)[0]
        if type(n) == 'transform':
            shape = n.getShape()
        elif type(n) == 'nurbsSurface':
            shape = n
        if shape:
            shapes.append(shape)

    return shapes

def distance(xforma, xformb):
    '''Calculates the distance between two transform nodes'''
    ax, ay, az = xforma.getTranslation(space='world')
    bx, by, bz = xformb.getTranslation(space='world')
    return ((ax-bx)**2 + (ay-by)**2 + (az-bz)**2)**0.5

def place_joint(position,name='joint',parent=None):
    joint = pm.joint(name=name, position=(0,0,0))
    joint.setTranslation(position, 'world')
    if parent:
        pm.delete(pm.orientConstraint(parent,joint))
    joint.setParent(parent)
    return joint

def place_joint_chain(start_loc, end_loc, num_joints=3, 
                      parent=None, name='jointChain'):
    joints = []
    start_joint = place_joint(
            get_ws_location(start_loc),
            name = '%s%02d' % (name, 1),
            parent = parent)
    end_joint = place_joint(
            get_ws_location(end_loc),
            name = '%s%02d' % (name, num_joints),
            parent = start_joint)
    dist = end_joint.getTranslation()
    dist = dist / float(num_joints-1)

    joints.append(start_joint)
    for i in range(2,num_joints):
        inside_joint = pm.insertJoint(joints[-1])
        inside_joint = to_pm_nodes(inside_joint)[0]
        inside_joint = pm.rename(inside_joint,
                                 '%s%02d' % (name, i))
        inside_joint.translateBy(dist)
        end_joint.translateBy(-dist)
        joints.append(inside_joint)
    joints.append(end_joint)

    return joints


def place_xform(name, mtype, matrix, parent=None, worldSpace=True):
    pm.select(clear=True)

    if mtype == 'joint':
        xform = pm.joint(name=name)
    elif mtype == 'group':
        xform = pm.group(name=name, empty=True)
    else:
        xform = pm.spaceLocator(name=name)

    if worldSpace:
        xform.setMatrix(matrix,worldSpace=True)
    else:
        xform.setMatrix(matrix,objectSpace=True)

    if parent:
        xform.setParent(pm.PyNode(parent))
    pm.makeIdentity(xform, apply=True)

    return xform

def place_xform_list(xform_list, worldSpace=True):
    xforms = []
    for xform in xform_list:
        xf = place_xform(name=xform['name'], mtype=xform['type'],
                         matrx=xform['matrix'],parent=xform['parent'],
                         worldSpace=worldSpace)
        xforms.append(xf)

    return xforms

def aim_normal(node, normal=[1,0,0]):
    loc = pm.spaceLocator(name='tmp_aimNormal_loc')
    loc.setTranslation(normal)
    pm.delete(pm.aimConstraint(loc, node, aimVector=(0,1,0)))
    pm.delete(loc)

def makeNonRendering(node):
    node.setAttr('castsShadows',0)
    node.setAttr('receiveShadows',0)
    node.setAttr('motionBlur',0)
    node.setAttr('primaryVisibility',0)
    node.setAttr('smoothShading',0)
    node.setAttr('visibleInReflections',0)
    node.setAttr('visibleInRefractions',0)

    return node