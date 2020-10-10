import bpy
from zpy import Is


class OBJECT_OT_toggle_shapekeys(bpy.types.Operator):
    bl_description = "Pin the basis shape key for all meshes in the file (for performance)"
    bl_idname = 'zpy.toggle_global_shapekeys'
    bl_label = "Toggle All Shape Keys"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        mute = None

        for obj in bpy.data.objects:
            if (not Is.mesh(obj)) or (obj.data.shape_keys is None):
                continue

            muted = bool('mute_shapekeys' in obj)

            if mute is None:
                mute = not muted

            if mute and not muted:
                # Storing shapekey settings
                obj['mute_shapekeys'] = (obj.active_shape_key_index, obj.show_only_shape_key)
                (obj.active_shape_key_index, obj.show_only_shape_key) = (0, True)
            elif not mute and muted:
                # Resetting shapekey settings
                (obj.active_shape_key_index, obj.show_only_shape_key) = obj['mute_shapekeys']
                del (obj['mute_shapekeys'])

        if mute is True:
            self.report({'INFO'}, "Locked all mesh shapekeys")
        elif mute is False:
            self.report({'INFO'}, "Unlocked all mesh shapekeys")

        return {'FINISHED'}
