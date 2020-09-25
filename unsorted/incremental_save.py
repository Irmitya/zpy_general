import bpy
from datetime import datetime
from os.path import basename, splitext, getmtime, isfile
from shutil import move
from zpy import register_keymaps
km = register_keymaps()

# saved_incremental = bool()


class SAVE_OT_incremental(bpy.types.Operator):
    bl_description = "Create another save file with a timestamp"\
        " for incremental backups"
    bl_idname = 'zpy.save_file'
    bl_label = "Save (Incremental File)"
    # bl_options = {}

    @classmethod
    def poll(cls, context):
        return (bpy.data.is_saved and bpy.data.filepath)

    def __init__(self):
        self.use_incremental_save = False

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'suffix')

    def invoke(self, context, event):
        if self.prompt:
            return context.window_manager.invoke_props_dialog(self)
        elif context.scene.use_incremental_save:
            return self.execute(context)
        else:
            return {'PASS_THROUGH'}
        # """Rather than only save when needed, just replace the backup saver"""
        # return self.execute(context)  # .union({'PASS_THROUGH'})
        # # # global saved_incremental

        # # # if bpy.data.is_dirty:
        # # #     saved_incremental = False
        # # #     return {'PASS_THROUGH'}
        # # # elif saved_incremental:
        # # #     saved_incremental = None  # allow saving anyway on every other press
        # # #     return {'CANCELLED'}
        # # else:
        # # #     ret = ({}, {'PASS_THROUGH'})[saved_incremental is None]
        # # #     saved_incremental = True
        # # #     return self.execute(context).union(ret)

    def execute(self, context):
        fpath = bpy.data.filepath
        fname, ext = splitext(fpath)
        file = fname.split(ext + " (")[0]
            # get original name if in a backup file
        basepath = file + ext

        try:
            now = datetime.fromtimestamp(getmtime(fpath))
            incr = f"{ext} ({now.year:04}-{now.month:02}-{now.day:02}"\
                f"_{now.hour:02}{now.minute:02}{now.second:02})"

            filepath = file + incr + " " + self.suffix + ext
            if isfile(basepath):
                if isfile(filepath):
                    print(f"Backup of Backup already exists; overwriting {filepath}")
                move(basepath, filepath)  # Rename the base file
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT', filepath=basepath)

            report = f"""Saved \"{basename(filepath)}\"\t(Incremental)"""
        except:
            # Happens when saving a (recovered) file
            report = f"""Saved \"{basename(filepath)}\""""

        bpy.ops.wm.save_mainfile('INVOKE_DEFAULT', filepath=basepath)

        if report:
            self.report({'INFO'}, report)

        return {'FINISHED'}

    suffix: bpy.props.StringProperty(
        name="Suffix",
        description="Text to insert after the previous file's date",
        default="",
        options={'SKIP_SAVE'},
        subtype='FILE_NAME',
    )

    prompt: bpy.props.BoolProperty(
        description="Show menu to insert suffix on previous save file",
        options={'HIDDEN', 'SKIP_SAVE'},
    )


def draw(self, context):
    layout = self.layout
    layout.prop(context.scene, 'use_incremental_save', icon='FILE_TICK')
    layout.operator('zpy.save_file', icon='FILE_TICK').prompt = True


def register():
    bpy.types.Scene.use_incremental_save = bpy.props.BoolProperty(
        name="Use Incremental Save",
        description="Enable unlimited backup saving of the file",
        default=True,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'},
    )
    bpy.types.TOPBAR_MT_app.prepend(draw)
    km.add(SAVE_OT_incremental, type='S', ctrl=True)


def unregister():
    km.remove()
    bpy.types.TOPBAR_MT_app.remove(draw)
    del bpy.types.Scene.use_incremental_save
