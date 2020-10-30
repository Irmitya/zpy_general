import bpy
from zpy import Is, Get, Set, utils


class OBJECT_OT_duplicate_shapekey(bpy.types.Operator):
    bl_description = "Duplicate the active shape key and its properties"
    bl_idname = 'zpy.duplicate_shapekey'
    bl_label = "Duplicate Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

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
            mirrored = mirror(shape, 'vertex_group', vg)
            mirror(shape, 'name', active.name)
        else:
            shape.vertex_group = vg
            shape.name = active.name
            mirrored = False
        for var in ('interpolation', 'mute', 'relative_key',
                    'slider_max', 'slider_min', 'value'):
            setattr(shape, var, getattr(active, var))
            driver = Get.driver(active, var)
            if driver:
                newdriver = utils.copy_driver(driver, shape, var)
                if mirrored:
                    for v in newdriver.driver.variables:
                        for t in v.targets:
                            mirror(t, 'bone_target', t.bone_target)


        # obj.active_shape_key_index = index
        obj.show_only_shape_key = pin

        if in_edit:
            Set.mode(context, 'EDIT')

        return {'FINISHED'}

    mirror: bpy.props.BoolProperty(name='Mirror Shape Key')


def mirror(src, attr, default):
    swaps = {
        'L.': 'R.', 'l.': 'r.', '.L': '.R', '.l': '.r',
        'R.': 'L.', 'r.': 'l.', '.R': '.L', '.r': '.l',
        'LEFT': 'RIGHT', 'Left': 'Right', 'left': 'right',
        'RIGHT': 'LEFT', 'Right': 'Left', 'right': 'left',
        '.LEFT': '.RIGHT', '.Left': '.Right', '.left': '.right',
        '.RIGHT': '.LEFT', '.Right': '.Left', '.right': '.left',
        'RIGHT.': 'LEFT.', 'Right.': 'Left.', 'right.': 'left.',
        'LEFT.': 'RIGHT.', 'Left.': 'Right.', 'left.': 'right.',
    }

    for m in swaps:
        if default[-len(m):] == m:  # endswith.lr
            setattr(src, attr, default[:-len(m)] + swaps[m])
            return 'end'
        # elif vg[:len(m)].title() == m.title():  # lr.startswith
        elif default[:-len(m)] == m:  # lr.startswith
            # name = default[:len(m)]
            # if m not in (name.upper(), name.title(), name.lower()):
                # if name == name.lower():
                    # m = m.lower()
            setattr(src, attr, swaps[m] + default[-len(m):])
            return 'start'
    else:
        setattr(src, attr, default)
