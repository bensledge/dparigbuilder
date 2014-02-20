import json

import pymel.core as pm
import defines

import soloBlock as sb
reload(sb)

# joint orientation
PRIMARY_AXIS    = 'xzy'
L_SECONDARY_AXIS= 'zdown'
M_SECONDARY_AXIS= 'zdown'
R_SECONDARY_AXIS= 'zdown'



##  Creates the entry for a xform node in a dict-recursively grabs children.
#   @param node The 'root' node to start at.
def gen_node_entry(node):
    if type(node) != pm.nodetypes.Joint:
        node = pm.ls(node)[0]
    entry = {
            'name': node.name(),
            # get the [x,y,z] coords. of the worldspace position
            'position':node.getScalePivot(space='world').get()[:3],
            # list the children of the current node, then call 
            # gen_node_entry on each and add it to the list
            'children':[gen_node_entry(x) for x in \
                node.listRelatives(children=True, type='transform')],
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
    json.dump(data,fn,indent=defines.JSON_INDENT)
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

def postfix_ui():
    pass


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

    node = pm.ls(node)[0]
    return pm.xform(node, query=True, worldSpace=True, rotatePivot=True)

##  create pm objects for the given list of nodes
#   @param nodes ('None') nodes to create objects for if None query selected
def to_pm_nodes(nodes=None,mtype='transform'):
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

def get_nurbs_shapes(nodes=None,mtype='transform'):
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
