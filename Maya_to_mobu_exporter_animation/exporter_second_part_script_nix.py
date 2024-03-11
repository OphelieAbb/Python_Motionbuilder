import sys
import maya.cmds as cmds
import os
# maya.standalone allows the use of Python commands in Mayapy
import maya.standalone
maya.standalone.initialize()

def YourExportFunction(export_path):
    # # Make sure that maya.standalone is correctly initialized. Might not be needed, but if the script cannot find some python commands, uncomment this line
    # maya.standalone.initialize()


    # WRITE YOUR CODE HERE
    #Export Nix in Maya in background during this time the animateur can work as same time
    cmds.file(force=True, new=True )
    cmds.file(export_path, i=True, type='FBX', ignoreVersion=True, mergeNamespacesOnClash=False, preserveReferences=True)

    list_join = cmds.listRelatives("*:ExtraDeformationSystem", children = True)
    for obj in list_join:
        cmds.parent(obj, world=True)
        
    cmds.delete("*:NIX")
    cmds.select( all=True )
    cmds.file(export_path, force = True, options = "v = 0", type = "FBX export", exportSelected = True, prompt=False)


     
    cmds.file(new=True, force=True)
    os._exit(0)
        


if __name__ == "__main__":
    # This will run when Mayapy has started. You can grab the additional arguments you gave Maya through sys.argv
    # sys.argv[0] will be your background script's path, but after that, it will be the additional arguments you added at line 13
    export_path = sys.argv[1]
    YourExportFunction(export_path)
