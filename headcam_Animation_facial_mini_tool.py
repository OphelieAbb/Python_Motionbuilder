# -*- coding: utf-8 -*-
import pyfbsdk as fb
import os

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


def get_selected_model():
    selectedModels = fb.FBModelList()
    topModel = None  # Search all models, not just a particular branch
    selectionState = True  # Return models that are selected, not deselected
    sortBySelectOrder = True  # The last model in the list was selected most recently
    fb.FBGetSelectedModels(selectedModels, topModel, selectionState, sortBySelectOrder)

    if selectedModels:
        for model in selectedModels:
            character = str(model.LongName)
            mymodel = fb.FBFindModelByName(character)

    return mymodel


def create_camera(name='head_cam', parent=None, tran=(0,0,0), rot=(0,0,0)):
    # Create a camera looking at the model.
    camera = fb.FBCamera(name)
    camera.Show = True
    camera.FieldOfView = 50
    camera.FocalLength = 16
    camera.FrameSizeMode.kFBFrameSizeFixedResolution
    camera.ResolutionHeight = 1080
    camera.ResolutionWidth = 1920
    # 2D magnifier
    camera.Use2DMagnifier = True
    camera.MagnifierPosX = 0
    camera.Use2DMagnifier = False

    if parent is not None:
        camera.Parent = parent

    camera.Translation = fb.FBVector3d(tran[0]+0,tran[1]+4,tran[2]+31)
    camera.Rotation = fb.FBVector3d(rot)

    return camera


def create_video_plane(parent=None, tran=(0,0,0), rot=(0,0,0)):
    video_plane = fb.FBModelPlane('video_plane')
    video_plane.Visible = True
    video_plane.Show = True

    if parent is not None:
        video_plane.Parent = parent

    video_plane.Translation = fb.FBVector3d(tran[0]+30,tran[1]-2,tran[2]-24)
    video_plane.Rotation = fb.FBVector3d(rot[0]+0,rot[1]+90,rot[2]+0)
    video_plane.SetVector( fb.FBVector3d( -0.10, -0.30,-0.20), fb.FBModelTransformationType.kModelScaling )

    return video_plane


def pick_video_file():
    app = fb.FBApplication()
    saveDialog = fb.FBFilePopup()
    saveDialog.Style = fb.FBFilePopupStyle.kFBFilePopupOpen
    saveDialog.Filter = "*.mov"

    # Pop up name for UI!
    saveDialog.Caption = "Merge Animations"

    # FRVideoTrack = FBStoryTrack(FBStoryTrackType.kFBStoryTrackVideo)
    # Run pop up UI!
    if saveDialog.Execute():
        # Once file has closed get chosen file add path details and
        # use them to FileOpen
        file_chosen = saveDialog.FileName
        path_chosen = saveDialog.Path
        file_path = r"{}\{}".format(path_chosen, file_chosen)
        app.FileMerge(file_path)

        return file_path

def get_video_from_video_track(fb_track):
    for vid in fb.FBSystem().Scene.VideoClips:
        if vid.Name == fb_track.Name:
            return vid
        

def set_video_plane_texture(video_plane, video_filepath):

    fr_path = os.path.normpath(video_filepath)
    fr_video = fb.FBVideoClip(fr_path)
    fr_video_track = fb.FBStoryTrack(fb.FBStoryTrackType.kFBStoryTrackVideo)

    _ = fb.FBStoryClip(fr_video, fr_video_track, fb.FBTime(0, 0, 0, 0))

    my_video = get_video_from_video_track(fr_video_track)
    fb_texture = fb.FBTexture("video_texture")


    fb_texture.Video = my_video

    # FBPropertyVideo
    fb_material = fb.FBMaterial("video_material")
    video_plane.ConnectSrc(fb_material)
    fb_material.SetTexture(fb_texture, fb.FBMaterialTextureType.kFBMaterialTextureDiffuse)

    textureTranslation = fb_texture.Translation
    fb_texture.Translation = fb.FBVector3d(-1.67, -0.12, 0)
    textureTranslation = fb_texture.Scaling
    fb_texture.Scaling = fb.FBVector3d(0.32, 1.02, 1)
    # # FRTexture.Scaling = fb.FBVector3d(0.40, 1, 1)
    # # FRTexture.SwapUV = True


class ToolNameGui(QDialog):

    def __init__(self):
        self.windowId = "ToolNameGui"

        # delete old instance
        self.close_windows(self.windowId)

        # window initialisation
        super(ToolNameGui, self).__init__(self.get_mobu_main_window())
        self.setObjectName(self.windowId)
        self.setWindowTitle("Head Camera")

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
        LYT_main.setContentsMargins(0, 0, 0, 0)
        LYT_main.setSpacing(3)
        self.setLayout(LYT_main)

        BTN = QPushButton("Create Head Camera")
        BTN.clicked.connect(self.create_head_camera)
        LYT_main.addWidget(BTN)

        BTN_settings = QToolButton()
        BTN_settings.setFixedSize(22, 22)
        BTN_settings.setAutoRaise(True)
        LYT_main.addWidget(BTN_settings)

    def create_head_camera(self):
        mymodel = get_selected_model()
        if mymodel:
            camera = create_camera(parent=mymodel, rot=(0, 90, 0))
            video_plane = create_video_plane(parent=camera, rot=(0, 0, 90))

            video_filepath = pick_video_file()
            if video_filepath:
                set_video_plane_texture(video_plane, video_filepath)

        else:
            # Simple message box: just a OK button.
            fb.FBMessageBox("DS la best team", "Select CTRL of head character on which you want head camera", "OK")


def launch():
    tool = ToolNameGui()


launch()

if __name__ == "__main__":
    launch()
# ==================================================================================