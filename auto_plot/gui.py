# -*- coding: utf-8 -*-
import pyfbsdk as fb
import os
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

#################################################################
#           CHECK ASSET PRESENT IN SCENE
#################################################################

#List vraiment tout contraintes etc 
#for component in fb.FBSystem().Scene.Components:
#    print (component.LongName)

#List plus succinte
#for model in fb.FBSystem().Scene.RootModel.Children:
#    print (model.LongName)
# def get_selected__model():
#     selectedModels = fb.FBModelList()
#     topModel = None  # Search all models, not just a particular branch
#     selectionState = True  # Return models that are selected, not deselected
#     sortBySelectOrder = True  # The last model in the list was selected most recently
#     fb.FBGetSelectedModels(selectedModels, topModel, selectionState, sortBySelectOrder)

#     if selectedModels:
#         for model in selectedModels:
#             character = str(model.LongName)
#             mymodel = fb.FBFindModelByName(character)
#             #print("___/", character)
#     return mymodel
#################################################################
#                EXPORT AND PLOT CHARACTER
#################################################################
    
##Get All Story Track
def select_tracks_in_story():
    trackList = []
    for track in fb.FBStory().RootFolder.Tracks:
        trackList.extend([track])
        track.Selected = True
        for clip in track.Clips:
            clip.Selected = True
            
def get_reference_nodes():
    reference_nodes = fb.FBComponentList()
    includeNamespace = True
    modelsOnly = False
    fb.FBFindObjectsByName('*_Ctrl:Reference', reference_nodes, includeNamespace, modelsOnly)
    return reference_nodes
    
def select_rigging_groupe_ctrl_ref(character_name):
    reference_nodes = get_reference_nodes()
    reference_nodes.Selected = True
    
    # Get model children
    children_rig_grp_ctrl_ref = character_name.Children
    # Check if any children exist
    if (len (children_rig_grp_ctrl_ref) != 0):
        # Loop through the children
        for child in children_rig_grp_ctrl_ref:
            # Select the child
            child.Selected = True

def select_animation_layers():
    system = fb.FBSystem()
    count = system.CurrentTake.GetLayerCount()
    for i in range(count):
        #layer = system.CurrentTake.GetLayer(i).Name
        system.CurrentTake.GetLayer(i).SelectLayer(True, False)
   
def create_character_anmation_track():
    #Get the current character in character control
    current_character = fb.FBApplication().CurrentCharacter

    track = fb.FBStoryTrack(fb.FBStoryTrackType.kFBStoryTrackCharacter, fb.FBStory().RootFolder)
    track.Details.append(current_character)
    time = fb.FBTime(0,0,0,0)
    take = fb.FBSystem().CurrentTake
    inserted_clip = track.CopyTakeIntoTrack(take.LocalTimeSpan, take)
    
def save_and_export_animation_plotted(given_path):
    system = fb.FBSystem()
    application = fb.FBApplication()
    current_character = application.CurrentCharacter

    save_character_current_name = current_character.LongName.rsplit(':', 2)[0]
    save_take_current_name = system.CurrentTake.Name
    save_fbx_file_full_name = application.FBXFileName
    
    save_dir = os.path.splitext(os.path.basename(save_fbx_file_full_name))[0]
    save_scene_name = os.path.splitext(os.path.basename(save_fbx_file_full_name))[0]
     
    # Variable for the paths
    save_path = given_path + "\\" + save_dir + "\\"
     
    # Variable for the file name
    save_file_name = save_scene_name + "--" + save_character_current_name
     
    # Variable for the full path "Root\SubFolder\FileName"
    save_character_anim = str(save_path + save_file_name)
       
    # Directory setup to save in (if director it not there then we make it)
    if not os.path.exists(save_path):
        path = os.makedirs(save_path)     
     
    # Save Animation Options    
    save_options = fb.FBFbxOptions (False) # false = will not save options 
    save_options.SaveCharacter = True
    save_options.SaveControlSet = True
    save_options.SaveCharacterExtention = True
    save_options.ShowFileDialog = False
    save_options.ShowOptionslDialog = False
    
    print (save_character_current_name + "'s Data from " + save_scene_name + " is being saved. Please wait....")
     
    # Save out animation
    application.SaveCharacterRigAndAnimation(save_character_anim, current_character, save_options)
     
    print (save_character_current_name + "'s Data from " + save_scene_name + " has been saved.")
     
def plotting_character_animation(given_path, character_name):
    select_rigging_groupe_ctrl_ref(character_name)
    select_animation_layers()
    select_tracks_in_story()
    # Defining our Characater as the currnetly selected one
    current_character = fb.FBApplication().CurrentCharacter
     
    # Defining the Plot option that will be used        
    plot_ctrl_rig_take_options = fb.FBPlotOptions()
    # To use Constant Key Reduction on the plot (True or False) 
    plot_ctrl_rig_take_options.ConstantKeyReducerKeepOneKey = False
    # To go through all takes in the scene and plot the data (True or False) 
    plot_ctrl_rig_take_options.PlotAllTakes = False
    # Do you wish to plot onto frames (True or False) 
    plot_ctrl_rig_take_options.PlotOnFrame = True
    # Set the plot period 
    plot_ctrl_rig_take_options.PlotPeriod = fb.FBTime( 0, 0, 0, 1 )
    plot_ctrl_rig_take_options.PlotTranslationOnRootOnly = False
    plot_ctrl_rig_take_options.PreciseTimeDiscontinuities = False
    # What filter to use on the plot (Unroll, GimabalKill or None)
    plot_ctrl_rig_take_options.RotationFilterToApply = fb.FBRotationFilter.kFBRotationFilterUnroll
    # Use Constant Kye Reduction (True or False)
    plot_ctrl_rig_take_options.UseConstantKeyReducer = False
     
    # Plotting to the selected character - note "kFBCharacterPlotOnControlRig" and "PlotCtrlRigTakeOptions".
    current_character.PlotAnimation(fb.FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton, plot_ctrl_rig_take_options) 
    current_character.PlotAnimation (fb.FBCharacterPlotWhere.kFBCharacterPlotOnControlRig,plot_ctrl_rig_take_options )
    
    create_character_anmation_track()
    save_and_export_animation_plotted(given_path)
    
def get_plot_all_characters(given_path, character_name):
    character_name.Selected = True
    plotting_character_animation(given_path, character_name)
    character_name.Selected = False

#################################################################
#                EXPORT AND PLOT PROPS
#################################################################

# Get props name for UI
def get_reference_nodes_props():
    reference_nodes = fb.FBComponentList()
    includeNamespace = True
    modelsOnly = False
    fb.FBFindObjectsByName('*:Prop', reference_nodes, includeNamespace, modelsOnly)
    return reference_nodes

def select_reference_nodes_props():
    reference_nodes_root = fb.FBComponentList()
    includeNamespace = True
    modelsOnly = False
    fb.FBFindObjectsByName('*:Prop', reference_nodes_root, includeNamespace, modelsOnly)
    for reference in reference_nodes_root:
        string = "_"
        if string in reference.LongName:
            reference.Selected = True
        return reference_nodes_root


def select_branches_props(props_name):
    #Need to adapt with UI same as character I will combine the the props with character for make one function
    reference_nodes = select_reference_nodes_props()
    reference_nodes.Selected = True
    # Get model children
    children__props_selection = props_name.Children
    # Check if any children exist
    if (len (children__props_selection) != 0):
        # Loop through the children
        for child in children__props_selection:
            # Select the child
            child.Selected = True   
                
def create_track_props(props_name):
    reference =  props_name
    reference.Selected = True
    track = fb.FBStoryTrack(fb.FBStoryTrackType.kFBStoryTrackAnimation, fb.FBStory().RootFolder)
    track.Details.append(reference)
    time = fb.FBTime(0,0,0,0)
    take = fb.FBSystem().CurrentTake
    inserted_clip = track.CopyTakeIntoTrack(take.LocalTimeSpan, take)
           
def save_and_export_animation_props_plotted(given_path,props_name):
    system = fb.FBSystem()
    application = fb.FBApplication()
    current_prop = props_name.LongName
    save_character_current_name = current_prop.rsplit(':', 2)[0]
    
    save_take_current_name = system.CurrentTake.Name
    save_fbx_file_full_name = application.FBXFileName
    
    save_dir = os.path.splitext(os.path.basename(save_fbx_file_full_name))[0]
    save_scene_name = os.path.splitext(os.path.basename(save_fbx_file_full_name))[0]
     
    # Variable for the paths
    save_path = given_path + "\\" + save_dir + "\\"
     
    # Variable for the file name
    save_file_name = save_scene_name + "--" + save_character_current_name
     
    # Variable for the full path "Root\SubFolder\FileName"
    save_prop_anim = str(save_path + save_file_name)
       
    # Directory setup to save in (if director it not there then we make it)
    if not os.path.exists(save_path):
        path = os.makedirs(save_path)     
  
    gFileFormat = fb.FBFileFormatAndVersion.kFBFBX2019          
    saveSelectedOptions = fb.FBFbxOptions(False)
    saveSelectedOptions.FileFormatAndVersion = gFileFormat  # set your FBX version
    saveSelectedOptions.SetAll(fb.FBElementAction.kFBElementActionDiscard, False)    # disable all element to save
    saveSelectedOptions.EmbedMedia = False  # disable export media
    saveSelectedOptions.Bones = fb.FBElementAction.kFBElementActionSave  # enable bones
    saveSelectedOptions.BonesAnimation = True    # enable bones animation
    saveSelectedOptions.Models = fb.FBElementAction.kFBElementActionSave      # enable models (Markers, nulls, meshes)
    saveSelectedOptions.ModelsAnimation = True         # enable models animation
    saveSelectedOptions.Materials = fb.FBElementAction.kFBElementActionSave    # enable material
    saveSelectedOptions.SaveSelectedModelsOnly = True      # set save selected elements only
    print (save_character_current_name + "'s Data from " + save_scene_name + " is being saved. Please wait....")
    fb.FBApplication().FileSave(save_prop_anim, saveSelectedOptions)
    print (save_character_current_name + "'s Data from " + save_scene_name + " has been saved.")
            
def plotting_for_props(given_path, props_name):
    select_tracks_in_story()
    select_animation_layers()
    select_branches_props(props_name)
    
    option_plot = fb.FBPlotOptions ()
    option_plot.UseConstantKeyReducer = True
    option_plot.ConstantKeyReducerKeepOneKey = True
    option_plot.PlotAllTakes = False
    option_plot.PlotOnFrame = True
    option_plot.PlotPeriod = fb.FBTime(0,0,0,1)
    option_plot.PlotTranslationOnRootOnly = True
        
    fb.FBSystem().CurrentTake.PlotAllTakesOnSelectedProperties(option_plot.PlotPeriod)   
    create_track_props(props_name)
    save_and_export_animation_props_plotted(given_path,props_name)

def call_plot_all_characters_each_time(given_path, props_name):
    props_name.Selected = True
    plotting_for_props(given_path, props_name)
    props_name.Selected = False 
    
       
#################################################################
#                          INTERFACE
#################################################################    
class AutoplotGui(QDialog):

    def __init__(self):
        
        self.windowId = "AutoplotGui"
        self.path = ""
        # delete old instance
        self.close_windows(self.windowId)

        # window initialisation
        super(AutoplotGui, self).__init__(self.get_mobu_main_window())
        self.setObjectName(self.windowId)
        self.setWindowTitle("Autoplot")

        # fill window
        self.build()
        self.show()

    def close_windows(self, *windows_ids):
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() in windows_ids:
                if widget.isVisible():
                    widget.close()
                widget.deleteLater()

    def get_mobu_main_window(self):
        top_level_windows = QApplication.topLevelWidgets()
        for w in top_level_windows:
            if w.windowTitle().startswith("MotionBuilder 20"):  
                return w
    ##########
    #   UI   #
    ##########

    def build(self):
        
        LYT_main = QVBoxLayout()
        #LYT_main.setContentsMargins(0, 0, 0, 0)
        LYT_main.setSpacing(3)
        self.setLayout(LYT_main)
        
        blank_line_begin_ui = QLabel("", self)
        label_character = QLabel("SELECT CHARACTERS FOR PLOT AND EXPORT :", self)
        label_character.setAlignment(Qt.AlignCenter)
        self.combo = QComboBox(self)
        LYT_main.addWidget(blank_line_begin_ui)
        LYT_main.addWidget(label_character)
        LYT_main.addWidget(self.combo)

        BTN_horizontal_box = QGridLayout()
        LYT_main.addLayout(BTN_horizontal_box)
        
        reference_nodes = get_reference_nodes()
        for reference_node in reference_nodes:
            item_string_charater = reference_node.LongName
            name_character = item_string_charater.split(":")[0]
            self.combo.addItem(name_character,reference_node)
        
        
        BTN_plot_selected = QPushButton("Plot And Export Selected \n Characters...")
        BTN_plot_selected.clicked.connect(self.plotting_only_one_characters)
        BTN_horizontal_box.addWidget(BTN_plot_selected,0,0)
        
        BTN_plot_all = QPushButton("Plot And Export \n All Characters...")
        BTN_plot_all.clicked.connect(self.plotting_all_characters)
        BTN_horizontal_box.addWidget(BTN_plot_all,0,1)
        
        blank_line_begin_ui = QLabel("", self)
        label_prop = QLabel("SELECT PROPS FOR PLOT AND EXPORT :", self)
        label_prop.setAlignment(Qt.AlignCenter)
        self.combo = QComboBox(self)

        LYT_main.addWidget(label_prop)
        LYT_main.addWidget(self.combo)

        BTN_horizontal_box_props = QGridLayout()
        LYT_main.addLayout(BTN_horizontal_box_props)
        
        reference_nodes_props = get_reference_nodes_props()
        for reference_node in reference_nodes_props:
            item_string_prop = reference_node.LongName
            name_props = item_string_prop.split(":")[0]
            self.combo.addItem(name_props,reference_node)
         
        BTN_plot_selected_props = QPushButton("Plot And Export Selected \n Props...")
        BTN_plot_selected_props.clicked.connect(self.plotting_only_one_props)
        BTN_horizontal_box_props.addWidget(BTN_plot_selected_props,0,0)

        BTN_plot_all_props = QPushButton("Plot And Export \n All Props...")
        BTN_plot_all_props.clicked.connect(self.plotting_all_props)
        BTN_horizontal_box_props.addWidget(BTN_plot_all_props,0,1)
        
        BTN_settings = QToolButton()
        BTN_settings.setFixedSize(22, 22)
        BTN_settings.setAutoRaise(True)
        LYT_main.addWidget(BTN_settings)
         
    def get_selected_reference_in_combo():
        return self.combo.currentData()  
                
    def plotting_all_characters(self):
        self.path = QFileDialog.getExistingDirectory()
        reference_nodes = get_reference_nodes()
        for reference in reference_nodes:
            selected_character = reference
            if self.path:
             print('[inside] path:', self.path)
             get_plot_all_characters(self.path, selected_character)
            else:
             print('[inside] path: - not selected -')
         
    def plotting_all_props(self):
        self.path = QFileDialog.getExistingDirectory()
        reference_nodes_pops = get_reference_nodes_props()
        #plotting_character_animation()
        for reference in reference_nodes_pops:
            selected_props = reference.LongName
            string = "_"
            if string in reference.LongName:
                selected_props = reference
                if self.path:
                 print('[inside] path:', self.path)
                 call_plot_all_characters_each_time(self.path, selected_props)
                else:
                 print('[inside] path: - not selected -')
                 
    def plotting_only_one_characters(self):
         self.path = QFileDialog.getExistingDirectory()
         if self.path:
             selected_character = self.combo.currentData()
             print('[inside] path:', self.path)
             plotting_character_animation(self.path, selected_character)
         else:
             print('[inside] path: - not selected -')
    
    def plotting_only_one_props(self):
         self.path = QFileDialog.getExistingDirectory()
         if self.path:
             selected_props = self.combo.currentData()
             print('[inside] path:', self.path)
             plotting_character_animation(self.path, selected_props)
         else:
             print('[inside] path: - not selected -')

def launch():
    tool = AutoplotGui()

#launch()

if __name__ == "__main__":
    launch()
# ==================================================================================