import maya.cmds as cmds
import os

import threading
import subprocess
from datetime import datetime
       
import maya.cmds as cmds
import os
import maya.mel as mel
       
def save_before(title = "Save Before?",message = "Do you want to save your scene before ?"):
    """Validate scene, find version based on convention, and return relevant information."""
    
    scene_path = cmds.file(sceneName=True, query=True)
    if cmds.file (query=True, modified=True):
        result = cmds.confirmDialog(title=title, message=message, button=['Yes','No'], defaultButton='Yes', cancelButton='No',dismissString='No')
    if result is "No":
        ind.error("Canceled")
    elif result=="Yes":
        mel.eval('SaveScene;')

def bake_animation_nix():
    save_before(title = "Save Before?",message = "Do you want to save your scene before ?")
    select_joints = cmds.select("*:export_skeleton_Set")
    joints = cmds.ls("*:export_skeleton_Set")
    vp2_state = cmds.ogs(pause=True)

    cmds.bakeSimulation(joints, time=(cmds.playbackOptions(animationStartTime=True, query=True), cmds.playbackOptions(animationEndTime=True, query=True)), at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], simulation=True, sampleBy=True, oversamplingRate=True, disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False, removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False,minimizeRotation=True, controlPoints=False,shape=True)
    cmds.select(clear=True)
    select_joints = cmds.select("*:export_skeleton_Set")
    scene_path = cmds.file(query=True, sceneName=True)

    scene_dir, scene_name = os.path.split(scene_path)
    scene_incremented = r"{}/incrementalSave/{}".format(str(scene_dir),str(scene_name))
    liste_scene = os.listdir(scene_incremented)
    
    path = scene_path.rsplit("/", 3)
    scene_name_extension = os.path.basename(scene_path)
    scene_name= os.path.splitext(scene_name_extension.lower())
    
    start_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filepath = r"{}/exports/{}_nix_{}.fbx".format(str(path[0]), str(scene_name[0]), str(start_date))
    cmds.file(filepath, force = True, options = "v = 0", type = "FBX export", exportSelected = True, prompt=False)
    cmds.file(new=True, force=True) 
    cmds.file(scene_path, open=True)
    open_maya_no_gui(filepath, scene_path)
   

def open_maya_no_gui(export_path):
    mayaPy_path = "C:/Program Files/Autodesk/Maya2020/bin/mayapy.exe"
    background_script = "C:/Users/oabbonato/OneDrive - Ubisoft/Documents/nix_exporter/exporter_second_part_script_nix.py"

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


def on_subprocess_finished():
    """
    Function called when subprocess has finished
    """
    # you can open a popup to warn animator that export is done here
    pass


bake_animation_nix()