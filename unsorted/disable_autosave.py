import bpy
from bpy.app.handlers import load_post, persistent
from zpy import utils

# Disable auto saving, to save space / time

ignored = (
    'D:\\!p\\!SFM\\arhoangel\\blend\\for saves\\',
    'D:\\Blender\\Library\\Models\\Models (Downloads To Import)\\',
    'D:\\Blender\\Library\\Models\\Models (SFM to Import)\\',
    'D:\\Blender\\Library\\Models\\Models (SFM Workshop)\\',
)


@persistent
def toggle_auto_save(scn, context=None):
    if not scn:
        # Prevent error on startup
        scn = bpy.context.scene

    prefs = utils.prefs().filepaths

    if (prefs.use_auto_save_temporary_files != scn.use_auto_save):
        prefs.use_auto_save_temporary_files = scn.use_auto_save

    if bpy.data.filepath.startswith(ignored):
        prefs.use_auto_save_temporary_files = False


def draw(self, context):
    self.layout.prop(context.scene, 'use_auto_save', icon='FILE_REFRESH')


def register():
    bpy.types.Scene.use_auto_save = bpy.props.BoolProperty(
        name="Auto Save Temporary Files",
        description="Automatically save backup of the blend file every minute",
        default=True,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
        update=toggle_auto_save,
    )
    bpy.types.TOPBAR_MT_app.prepend(draw)
    load_post.append(toggle_auto_save)


def unregister():
    load_post.remove(toggle_auto_save)
    bpy.types.TOPBAR_MT_app.remove(draw)
    del bpy.types.Scene.use_auto_save
