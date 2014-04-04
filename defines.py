"""@package defines
Settings and globals for dpabuildingblocks.
"""

## Representation of the worldspace option in pymel
WORLD = None

## Level of indention for json.dump[s]. 0 = lowest level.
JSON_INDENT = 0

## Bind rig postfix
BIND = 'bind'
FOLLICLE = 'follicle'
JOINT = 'joint'
CURVE = 'crv'
WIRE = 'wire'
DRVR = 'drvr%s' % (JOINT.title())
CTRL = 'ctrl'
BLENDSHAPE = 'bs'
HAIR_SYS = 'hsys'
PMA = 'pma'     # plus minus average
IK_HANDLE = 'ikHandle'
IK = 'ik'
PLANE = 'plane'