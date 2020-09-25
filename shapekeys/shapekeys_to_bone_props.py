import bpy
from zpy import Get, Is, popup


class DRIV_OT_shapes_to_bone(bpy.types.Operator):
    bl_description = "Add drivers to shapekeys, using custom properties in active pose bone"
    bl_idname = 'zpy.shapekeys_to_bone_props'
    bl_label = "Drive Shapekeys to Bone Props"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_rna.description

    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj or len(getattr(context.object.data.shape_keys, 'key_blocks', [])) <= 1:
            return
        for m in obj.modifiers:
            if m.type == 'ARMATURE':
                rig = m.object
                if rig in context.selected_objects:
                    return rig.data.bones.active

    def invoke(self, context, event):
        return popup.invoke_popup(context, self, width=174)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'active')
        col = layout.column()
        col.active = not self.active
        col.prop(self, 'overwrite')
        col.prop(self, 'filter')

        layout.operator_context = 'EXEC_DEFAULT'
        op = layout.operator('zpy.shapekeys_to_bone_props', text="OK")
        op.active = self.active
        if self.active:
            op.overwrite = True
            op.filter = ""
        else:
            op.overwrite = self.overwrite
            op.filter = self.filter

    def execute(self, context):
        obj = context.object

        for m in obj.modifiers:
            if m.type == 'ARMATURE':
                rig = m.object
                if rig in context.selected_objects:
                    bone_name = rig.data.bones.active.name
                    bone = rig.pose.bones[bone_name]
                    break

        keys = obj.data.shape_keys.key_blocks

        if self.active:
            key = obj.active_shape_key
            if key == keys[0]:
                self.report({'WARNING'}, "Active shape key is the base shape")
                return {'CANCELLED'}

            if Get.driver(key, 'value'):
                key.driver_remove('value')
            # if key.name in bone:
                # del bone[key.name]

            self.add_driver(key, bone)
        else:
            for key in keys[1:]:
                if (self.filter and (self.filter not in key.name)):
                    continue
                if not (self.overwrite or (not Get.driver(key, 'value'))):
                    continue

                self.add_driver(key, bone)

        return {'FINISHED'}

    def add_driver(self, key, bone):
        if key.name not in bone:
            bone[key.name] = key.value
            bone['_RNA_UI'] = bone.get('_RNA_UI', dict())
            bone['_RNA_UI'][key.name] = dict(
                min=key.slider_min, max=key.slider_max,
                soft_min=key.slider_min, soft_max=key.slider_max,
                description="",
                default=0.0,
            )
        else:
            # Update existing limits
            block = bone['_RNA_UI'][key.name]

            for attr in 'min', 'soft_min':
                block[attr] = min(block.get(attr, key.slider_min), key.slider_min)
            for attr in 'max', 'soft_max':
                block[attr] = max(block.get(attr, key.slider_max), key.slider_max)
        bone.property_overridable_library_set(f'[\"{key.name}\"]', True)

        _driver = key.driver_add('value')
        driver = _driver.driver
        # driver.expression = 'var'
        driver.type = 'AVERAGE'

        if 'var' in driver.variables:
            variable = driver.variables['var'].targets[0]
        else:
            variable = driver.variables.new().targets[0]
        variable.id_type = 'OBJECT'
        variable.id = bone.id_data

        variable.data_path = bone.path_from_id(f'["{key.name}"]')

        # driver.expression += " "
        # driver.expression = driver.expression[:-1]

    active: bpy.props.BoolProperty(
        name="Active Key",
        description="Insert drivers to only the active key (and overwrite any existing driver)",
        default=False,
        # options={'SKIP_SAVE'},
    )
    overwrite: bpy.props.BoolProperty(
        name="Overwrite",
        description="Replace driver when it already exists",
        default=True,
        # options={'SKIP_SAVE'},
    )
    filter: bpy.props.StringProperty(
        name="Filter",
        description="Only add drivers to keys containing this text",
        default="",
        subtype='NONE',
    )


def draw_menu(self, context):
    layout = self.layout
    if bpy.ops.zpy.shapekeys_to_bone_props.poll():
        layout.operator('zpy.shapekeys_to_bone_props', text="Drive Shapekeys to Bone Props", icon='DRIVER')
        # layout.operator('zpy.shapekeys_to_bone_props', text="Drive Shapekeys to Bone Props (All)").active = False
        # layout.operator('zpy.shapekeys_to_bone_props', text="Drive Shapekeys to Bone Props (Active)").active = True


def register():
    bpy.types.MESH_MT_shape_key_context_menu.append(draw_menu)


def unregister():
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_menu)
