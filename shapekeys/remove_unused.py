import bpy
from zpy import Is, Set


class OBJECT_OT_remove_unused_shapekeys(bpy.types.Operator):
    bl_description = "Remove shape keys with no changes"
    bl_idname = 'zpy.remove_unused_shapekeys'
    bl_label = "Remove Unused Shape Keys"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return

    @classmethod
    def poll(cls, context):
        return Is.mesh(context.object) and (context.object.data.shape_keys)

    def invoke(self, context, event):
        if event.alt:
            active = context.object
            for ob in context.selected_objects:
                if Is.mesh(ob) and (ob.data.shape_keys):
                    Set.active(context, ob)
                    self.purge(ob)
            Set.active(context, active)
        else:
            self.purge(context.object)
        return {'FINISHED'}

    def execute(self, context):
        self.purge(context.object)
        return {'FINISHED'}

    @staticmethod
    def purge(ob):
        sk = ob.data.shape_keys.key_blocks

        active_index = ob.active_shape_key_index
        remove = list()

        for (key_index, key) in enumerate(sk[1:]):
            basis = {sk[0], key.relative_key}
            for base in basis:
                for (vert_index, vert) in enumerate(key.data):
                    if (vert.co != base.data[vert_index].co):
                        # Shapekey has a change, so keep it
                        break
                else:
                    # Maybe shapekey only has difference against its basis
                    continue
                break
            else:
                # Shapekey no changes, so remove it
                print("Removing", key.name, "from", ob.name)
                remove.append(key_index + 1)

        for index in reversed(remove):
            ob.active_shape_key_index = index
            bpy.ops.object.shape_key_remove(all=False)

        ob.active_shape_key_index = active_index
