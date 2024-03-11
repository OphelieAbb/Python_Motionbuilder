# -*- coding: utf-8 -*-
import pyfbsdk as fb
import os
import re
PROPS_PATH = r"\\ubisoft.org\mtpstudio\Departments\Cine\Share\Ophelie\dev\4-Props_test"

    
def browse_fbx_files(path=PROPS_PATH):
    for root, dirs, files in os.walk(PROPS_PATH):
        for name in files:
            if name.endswith((".fbx", ".FBX")):
                print("------------- Le props{}a été ouvert".format(name))
                file_fbx_name_separated = re.split('[.]', name)
                file_name = file_fbx_name_separated[0]
                files_fbx = os.path.join(path, name)
                open_fbx_files(files_fbx)
                align_roation_translation(file_name)
                export_fbx_props(file_name, path=PROPS_PATH)
                #app = fb.FBApplication()
                #app.FileOpen(path + name)
            #return file_fbx_name
            
def open_fbx_files(files):
    head_tail = os.path.split(files)
    file_fbx_name_separated = re.split('[.]', head_tail[1])
    file_fbx_name = file_fbx_name_separated[0]
    app = fb.FBApplication()
    app.FileOpen(files)
    return file_fbx_name
    
def get_props_asset():
    internal_node = "UDCCInternalNode"
    for model in fb.FBSystem().Scene.RootModel.Children:
        if not model.Name == internal_node:
            continue
        return model
        
def create_maker_ctrl(file_name):
    cross_marker = fb.FBModelMarker("CTRL_{}".format(file_name))
    cross_marker.Look = fb.FBMarkerLook.kFBMarkerLookHardCross
    cross_marker.Show = True
    cross_marker.Size = 500 
    
    return cross_marker
    
def align_roation_translation(file_name):
    props_asset = get_props_asset()
    marker = create_maker_ctrl(file_name)
    
    sourceTrans = fb.FBVector3d()
    sourceRot = fb.FBVector3d()  

    props_asset.GetVector (sourceTrans, fb.FBModelTransformationMatrix.kModelTranslation)
    props_asset.GetVector (sourceRot, fb.FBModelTransformationMatrix.kModelRotation)

    marker.Translation = sourceTrans
    marker.Rotation = sourceRot

    parent = marker
    props_asset.Parent = parent

def export_fbx_props(file_name,path=PROPS_PATH):
    #system = fb.FBSystem()
    for component in fb.FBSystem().Scene.Components:
        component.Selected = True
    app = fb.FBApplication()
    fbx_options = fb.FBFbxOptions(False)
    fbx_options.SetAll(fb.FBElementAction.kFBElementActionSave, True) 
    fbx_options.FileFormatAndVersion = fb.FBFileFormatAndVersion.kFBFBX2018 # FBX save version 2014_2015 
    fbx_options.EmbedMedia = False

    file_name = "/{}.fbx".format(file_name)
    app.FileSave(path + file_name, fbx_options)
    print("EXPORT IS DONE{}".format(file_name))
      
def launch():
    #align_roation_translation(model , cross_marker)
    files = browse_fbx_files(path=PROPS_PATH)
    file_name = open_fbx_files(files)
    browse_fbx_files(path = PROPS_PATH)
    #align_roation_translation(file_name)
    #export_fbx_props(file_name,path=PROPS_PATH)
 
launch()