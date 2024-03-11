import maya.cmds as cmds
import os
import sys

import threading
import subprocess


def create_new_scene():
    scene_path = cmds.file(query=True, sceneName=True)
    path = scene_path.rsplit("/", 3)
    scene_name_extension = os.path.basename(scene_path)
    scene_name= os.path.splitext(scene_name_extension.lower())

    scene_temp = cmds.file(rename="{}/maya/scenes/export_scene_only/tmp_{}.ma".format(str(path[0]),str(scene_name[0])))
    cmds.file(save=True, type="mayaAscii")
    rename_curent_scene = cmds.file(rename="{}/maya/scenes/{}.ma".format(str(path[0]), str(scene_name[0])))
    open_maya_no_gui(scene_temp)


def bake_animation_nix(export_path):
    cmds.file(new=True, force=True) 
    cmds.file(export_path, open=True)
    #select_joints = cmds.select("*:export_skeleton_Set")
    joints = cmds.ls("*:export_skeleton_Set")
    vp2_state = cmds.ogs(pause=True)

    cmds.bakeSimulation(joints, time=(cmds.playbackOptions(animationStartTime=True, query=True), cmds.playbackOptions(animationEndTime=True, query=True)), at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], simulation=True, smart=False, disableImplicitControl=True, preserveOutsideKeys=False, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False, minimizeRotation=True, sampleBy=1.0)
    cmds.select(clear=True)
    select_joints = cmds.select("*:export_skeleton_Set")
    
    scene_path = cmds.file(query=True, sceneName=True)
    path = scene_path.rsplit("/", 3)
    scene_name_extension = os.path.basename(scene_path)
    scene_name= os.path.splitext(scene_name_extension.lower())
    filepath = r"{}/exports/{}_nix_cin_tmp.fbx".format(str(path[0]), str(scene_name[0]))

    cmds.file(filepath, force = True, options = "v = 0", type = "FBX export", exportSelected = True, prompt=False)
  
    
    

def open_maya_no_gui(export_path):
    
    mayaPy_path = "C:/Program Files/Autodesk/Maya2020/bin/mayapy.exe"
    background_script = "//ubisoft.org/mtpstudio/Departments/Cine/Tools/TechnicalDirection/mtp_cin_tools/tools/nix_exporter/exporter_first_part_nix_002.py"

    args = [mayaPy_path, background_script]
    # additional arguments to pass to the second Maya :
    args += [export_path]
    
    # Basic startup infos
    startupinfo = subprocess.STARTUPINFO()

    # Customize startup infos
    # CREATE_NEW_CONSOLE : make sure the output window is open so that maya writes logs in it
    # STARTF_USESHOWWINDOW : allow use of wShowWindow just after
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    # Hides the console window so that it doesn't pop in front of current Maya
    startupinfo.wShowWindow = subprocess.SW_HIDE

    # Run the new Maya in a thread
    run_subprocess(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, startupinfo=startupinfo)
    
    
    
def run_subprocess(args, stdin, stdout, startupinfo):
    """
    Runs the subprocess in a thread, then call on_subprocess_finished afterwards
    """

    def subprocess_thread(args, stdin, stdout, startupinfo):
        """
        Run subprocess and wait for exit
        """
        # main command
        process = subprocess.Popen(args, stdin=stdin, stdout=stdout, startupinfo=startupinfo)
        
        # this will print log and errors while the subprocess works. Not sure if it works well with thread, needs to be tested. comminicate wait already
        output, errors = process.communicate()
        print (output)
        print (errors)
        
        # wait for the end of the subprocess
        #process.wait()
        
        # when the second Maya has finished, launch this function
        on_subprocess_finished()

    # start thread 
    thread = threading.Thread(target=subprocess_thread, args=(args, stdin, stdout, startupinfo))
    thread.start()
    
    # return just after the thread starts
    return thread


def on_subprocess_finished(export_path):
    """
    Function called when subprocess has finished
    """
    # you can open a popup to warn animator that export is done here
    pass

# maya.standalone allows the use of Python commands in Mayapy
#import maya.standalone
#maya.standalone.initialize()

def YourExportFunction(export_path):
    bake_animation_nix(export_path)
    # # Make sure that maya.standalone is correctly initialized. Might not be needed, but if the script cannot find some python commands, uncomment this line
    # maya.standalone.initialize()


    # WRITE YOUR CODE HERE
    print("Export to " + export_path)
     
    cmds.file(new=True, force=True)
    os._exit(0)
        


if __name__ == "__main__":
    # This will run when Mayapy has started. You can grab the additional arguments you gave Maya through sys.argv
    # sys.argv[0] will be your background script's path, but after that, it will be the additional arguments you added at line 13
    export_path = sys.argv[0]
    YourExportFunction(export_path)