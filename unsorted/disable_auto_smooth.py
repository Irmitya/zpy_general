import bpy

class MESH_OT_disable_auto_smooth_global(bpy.types.Operator):
    bl_description = "Disable Auto Smooth in all animated object meshes"
    bl_idname = 'mesh.disable_auto_smooth_global'
    bl_label = "Disable Auto Smooth"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for ob in bpy.data.objects:
            if (ob.type != 'MESH') or (not ob.data.use_auto_smooth):
                continue

            # Try to filter objects, to keep static objects, for example furniture
            for mod in ob.modifiers:
                if mod.type == 'ARMATURE':
                    break
            else:
                if ob.data.shape_keys:
                    if ob.data.shape_keys.animation_data:
                        pass
                    else:
                        # Maybe scan for other animated data, like modifiers
                        continue
                else:
                    continue

            # Mesh has been considered to be animated, so disable auto smooth
            ob.data.use_auto_smooth = False

        return {'FINISHED'}


def draw(self, context):
    layout = self.layout
    layout.operator('mesh.disable_auto_smooth_global')


def register():
    bpy.types.DATA_PT_normals.append(draw)


def unregister():
    bpy.types.DATA_PT_normals.remove(draw)
