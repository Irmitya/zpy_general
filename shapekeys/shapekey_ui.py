import bpy


def draw_top(self, context):
    layout = self.layout
    layout.operator('zpy.apply_shapekey_mask', icon='CHECKMARK')
    layout.operator('zpy.duplicate_shapekey', icon='DUPLICATE').mirror = False
    layout.operator('zpy.duplicate_shapekey', text="Duplicate Shape Key (Mirrored)", icon='DUPLICATE').mirror = True



def draw_bottom(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('zpy.remove_unused_shapekeys', icon='CANCEL')
    layout.operator('zpy.toggle_global_shapekeys', icon='SHAPEKEY_DATA')


def draw_panel(self, context):
    layout = self.layout

    if bpy.ops.zpy.apply_shapekey_mask.poll():
        layout.operator('zpy.apply_shapekey_mask', icon='CHECKMARK')
        # row = layout.row(align=True)
        # row.operator('zpy.apply_shapekey_mask', icon='CHECKMARK').keep_vertex_group = True
        # row.operator('zpy.apply_shapekey_mask', icon='X', text="").keep_vertex_group = False


def register():
    bpy.types.MESH_MT_shape_key_context_menu.prepend(draw_top)
    bpy.types.MESH_MT_shape_key_context_menu.append(draw_bottom)
    bpy.types.DATA_PT_shape_keys.append(draw_panel)


def unregister():
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_bottom)
    bpy.types.MESH_MT_shape_key_context_menu.remove(draw_top)
    bpy.types.DATA_PT_shape_keys.remove(draw_panel)
