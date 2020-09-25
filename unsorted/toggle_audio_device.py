import bpy


class SOUND_OT_reload_audio_device(bpy.types.Operator):
    bl_description = "Reload the active audio device currently used in Blender"
    bl_idname = 'zpy.reload_audio_device'
    bl_label = "Reload Audio Device"

    @classmethod
    def description(cls, context, properties):
        return cls.bl_rna.description

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        sys = context.preferences.system
        sys.audio_device = sys.audio_device

        return {'FINISHED'}


def draw_playback(self, context):
    layout = self.layout
    layout.operator('zpy.reload_audio_device', icon='OUTLINER_OB_SPEAKER')


def register():
    bpy.types.TIME_PT_playback.append(draw_playback)


def unregister():
    bpy.types.TIME_PT_playback.remove(draw_playback)


# import bpy
# from bpy.props import BoolProperty
# from bpy.types import WindowManager
# from os import system


# def draw(self, context):
    # layout = self.layout
    # region = context.region

    # if region.alignment == 'RIGHT':
        # wm = context.window_manager

        # # if wm.audio_sys_device:
            # # sys = 'SPEAKER'
        # # else:
            # # sys = 'SOUND'
            # # 'PLAY_SOUND'

        # # if wm.audio_blend_device:
            # # blend = 'OUTLINER_OB_SPEAKER'
        # # else:
            # # blend = 'OUTLINER_DATA_SPEAKER'
        # blend = 'OUTLINER_OB_SPEAKER'

        # row = layout.row(align=True)
        # row.emboss = 'PULLDOWN_MENU'
        # # row.prop(wm, 'audio_sys_device', text="", icon=sys)
        # row.prop(wm, 'audio_blend_device', text="", icon=blend)


# def register():
    # def toggle_system(self, context):
    #     # system('SSD.exe 77729997773hidden')  # Toggle to other device

    #     if self.audio_sys_device:
    #         system('nircmd setdefaultsounddevice "Speakers" 1')
    #         system('nircmd setdefaultsounddevice "Speakers" 2')
    #     else:
    #         system('nircmd setdefaultsounddevice "Headphones" 1')
    #         system('nircmd setdefaultsounddevice "Headphones" 2')
    # WindowManager.audio_sys_device = BoolProperty(
    #     name="Toggle System Device",
    #     description="Switch Default audio device used in Windows",
    #     default=True,
    #     # update=toggle_system,
    # )

    # def toggle_audio(self, context):
    #     # spk = self.audio_sys_device

    #     # self.audio_sys_device = self.audio_blend_device

    #     sys = context.preferences.system
    #     sys.audio_device = sys.audio_device
    #     # self.audio_sys_device = spk
    # WindowManager.audio_blend_device = BoolProperty(
    #     name="Toggle Audio Device",
    #     description="Switch audio device currently used in Blender",
    #     default=True,
    #     update=toggle_audio,
    # )

    # bpy.types.TOPBAR_HT_upper_bar.prepend(draw)


# def unregister():
    # del WindowManager.audio_blend_device
    # del WindowManager.audio_sys_device
    # bpy.types.TOPBAR_HT_upper_bar.remove(draw)
