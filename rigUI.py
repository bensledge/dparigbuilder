from pymel.core import *
import pymel.core as pm
from pymel import *

WINDOW_NAME = 'dpaRigging'

class UI(object):
    def __init__(self):
        title   = 'dpaRigTools gui'
        version = '0.0.1'

        if pm.window(WINDOW_NAME, exists=True):
            pm.deleteUI(WINDOW_NAME)

        with pm.window(WINDOW_NAME, 
                title   = title + ' | ' + version,
                menuBar = True,
                menuBarVisible  = True,
                minimizeButton  = True,
                maximizeButton  = False,
                numberOfMenus   = 2, 
                




def buttonPressed(name):
    print "pressed %s!" % name

def main():
    win = pm.window(title='dpaRigTools')
    layout = pm.columnLayout()
    names = ['chad','robert','james']
    for name in names:
        pm.button( label=name, command = Callback( buttonPressed, name))

    pm.showWindow()
