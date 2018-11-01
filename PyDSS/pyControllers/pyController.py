from os.path import dirname, basename, isfile
import glob

from  PyDSS.pyControllers import Controllers

modules = glob.glob(Controllers.__path__[0]+"/*.py")
pythonFiles = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py') ]

from PyDSS.dssElement import dssElement
ControllerTypes = {}

for file in pythonFiles:
    exec('from PyDSS.pyControllers.Controllers import {}'.format(file))
    exec('ControllerTypes["{}"] = {}.{}'.format(file, file, file))

print(ControllerTypes)

def Create(ElmName, ControllerType, Settings, ElmObjectList, dssInstance, dssSolver):
    try:
        print(ElmObjectList)
        relObject = ElmObjectList[ElmName]
    except:
        Index = dssInstance.Circuit.SetActiveElement(ElmName)
        if int(Index) >= 0:
            ElmObjectList[ElmName] = dssElement(dssInstance)
            relObject = ElmObjectList[ElmName]
        else:
            print('The controller dictionary does not contain ' + ControllerType)
            return -1
    ObjectController = ControllerTypes[ControllerType](relObject, Settings, dssInstance, ElmObjectList, dssSolver)
    return ObjectController