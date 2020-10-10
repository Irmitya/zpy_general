import bpy


class HOOK_OT_clear_mod(bpy.types.Operator):
    bl_description = "Remove all vertices from hook modifier"
    bl_idname = 'object.hook_clear'
    bl_label = "Clear Hook"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'modifier')

    def execute(self, context):
        context.modifier.vertex_indices_set(())
        return {'FINISHED'}


def HOOK(self, layout, ob, md):
    use_falloff = (md.falloff_type != 'NONE')
    split = layout.split()

    col = split.column()
    col.label(text="Object:")
    col.prop(md, "object", text="")
    if md.object and md.object.type == 'ARMATURE':
        col.label(text="Bone:")
        col.prop_search(md, "subtarget", md.object.data, "bones", text="")
    col = split.column()
    col.label(text="Vertex Group:")
    col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

    layout.separator()

    row = layout.row(align=True)
    if use_falloff:
        row.prop(md, "falloff_radius")
    row.prop(md, "strength", slider=True)
    layout.prop(md, "falloff_type")

    col = layout.column()
    if use_falloff:
        if md.falloff_type == 'CURVE':
            col.template_curve_mapping(md, "falloff_curve")

    split = layout.split()

    col = split.column()
    col.prop(md, "use_falloff_uniform")

    if ob.mode == 'EDIT':
        row = col.row(align=True)
        row.operator("object.hook_reset", text="Reset")
        row.operator("object.hook_recenter", text="Recenter")

        row = layout.row(align=True)
        row.operator("object.hook_select", text="Select")
        row.operator("object.hook_assign", text="Assign")
    else:
        row = layout.row(align=True)
    row.context_pointer_set('modifier', md)
    row.operator("object.hook_clear", text="Clear")


# mods = bpy.types.DATA_PT_modifiers


# class backup:
    # HOOK = None


# def register():
    # backup.HOOK = mods.HOOK
    # mods.HOOK = HOOK


# def unregister():
    # mods.HOOK = backup.HOOK
