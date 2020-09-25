import bpy
from zpy import Is, Get


class OBJECT_OT_apply_shapekey_mask(bpy.types.Operator):
    bl_description = "Apply the active shape key, based on the Vertex Group mask"
    bl_idname = 'zpy.apply_shapekey_mask'
    bl_label = "Apply Mask to Shape Key"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_rna.description

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (Is.mesh(ob) and getattr(ob.active_shape_key, 'vertex_group', None))

    def execute(self, context):
        obj = context.object

        active = obj.active_shape_key
        index = obj.active_shape_key_index
        pin = obj.show_only_shape_key

        obj.show_only_shape_key = True
        bpy.ops.object.shape_key_add(from_mix=True)
        while obj.active_shape_key_index > (index + 1):
            bpy.ops.object.shape_key_move(type='UP')

        shape = obj.active_shape_key
        for var in ('interpolation', 'mute', 'relative_key', 'slider_max', 'slider_min', 'value'):
            setattr(shape, var, getattr(active, var))
        # if self.keep_vertex_group:
            # shape.vertex_group = active.vertex_group

        # Redirect drivers, so that they auto update after operation
        for var in ('slider_max', 'slider_min', 'value'):
            driver = Get.driver(active, var)
            if driver:
                driver.data_path = f'key_blocks["{shape.name}"].{var}'
                # driver.data_path = driver.data_path.replace(active.name, shape.name, 1)

        name = active.name
        active.name += ".masked"
        shape.name = name

        obj.active_shape_key_index = index
        bpy.ops.object.shape_key_remove(all=False)
        obj.active_shape_key_index = index
        obj.show_only_shape_key = pin

        return {'FINISHED'}

    # keep_vertex_group: bpy.props.BoolProperty(
        # name="Keep Vertex Group",
        # description="After applying the shape key's vertex group masking, keep it active",
    # )
