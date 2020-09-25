import bpy
from zpy import Set


class SET_OT_active(bpy.types.Operator):
    bl_description = "Set item as active"
    bl_idname = 'zpy.set_active'
    bl_label = "Set Active"
    # bl_options = {}

    @classmethod
    def poll(self, context):
        return hasattr(context, 'active_target')

    def invoke(self, context, event):
        target = context.active_target

        if event.alt:
            Set.select(target, False)
        elif event.shift:
            Set.active_select(context, target, isolate=False)
        elif event.ctrl:
            Set.active_select(context, target, isolate=True)
        else:
            return self.execute(context)

        return {'FINISHED'}

    def execute(self, context):
        target = context.active_target

        Set.active_select(context, target, True)

        return {'FINISHED'}
