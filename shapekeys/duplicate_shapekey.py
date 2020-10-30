import bpy
from zpy import Is, Get, Set, utils


class OBJECT_OT_duplicate_shapekey(bpy.types.Operator):
    bl_description = "Duplicate the active shape key and its properties"
    bl_idname = 'zpy.duplicate_shapekey'
    bl_label = "Duplicate Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        txt = cls.bl_description

        if properties.mirror:
            obj = context.object
            if obj and obj.active_shape_key:
                active = obj.active_shape_key
                sk = utils.flip_name(active.name)
                vg = utils.flip_name(active.vertex_group)

                if (sk != active.name):
                    txt += f", and name it {sk}"
                    if (vg != active.vertex_group):
                        txt += f" with the vertex group [{vg}]"
                elif (vg != active.vertex_group):
                    txt += f", and switch its vertex group with [{vg}]"
            else:
                txt += ", and flip it's name and vertex group if it has a Left/Right mirroed name indicators"

        return txt

    @classmethod
    def poll(cls, context):
        return Is.mesh(context.object) and (context.object.data.shape_keys)

    def execute(self, context):
        obj = context.object

        in_edit = (obj.mode == 'EDIT')
        if in_edit:
            Set.mode(context, 'OBJECT')

        active = obj.active_shape_key
        vg = active.vertex_group
        index = obj.active_shape_key_index
        pin = obj.show_only_shape_key

        obj.show_only_shape_key = True
        active.vertex_group = ''
        bpy.ops.object.shape_key_add(from_mix=True)
        while obj.active_shape_key_index > (index + 1):
            bpy.ops.object.shape_key_move(type='UP')
        active.vertex_group = vg

        shape = obj.active_shape_key

        if self.mirror:
            shape.name = utils.flip_name(active.name)
            shape.vertex_group = utils.flip_name(vg)
        else:
            shape.vertex_group = vg
            shape.name = active.name

        for var in ('interpolation', 'mute', 'relative_key',
                    'slider_max', 'slider_min', 'value'):
            setattr(shape, var, getattr(active, var))
            driver = Get.driver(active, var)
            if not driver:
                continue
            newdriver = utils.copy_driver(driver, shape, var)

            if self.mirror:
                for v in newdriver.driver.variables:
                    for t in v.targets:
                        t.bone_target = utils.flip_name(t.bone_target)

        # obj.active_shape_key_index = index
        obj.show_only_shape_key = pin

        if in_edit:
            Set.mode(context, 'EDIT')

        return {'FINISHED'}

    mirror: bpy.props.BoolProperty(name='Mirror Shape Key')
