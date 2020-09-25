import bpy
from zpy import Is, Get


class PROXY_PT_display_op(bpy.types.Panel):
    bl_label = "Make Proxy"
    bl_options = {'HIDE_HEADER'}
    bl_region_type = 'TOOLS'
    bl_space_type = 'VIEW_3D'

    @classmethod
    def poll(self, context):
        obj = context.object
        group = getattr(obj, 'instance_collection', None)

        return (group and group.library) or (obj and obj.library)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 2
        obj = context.object

        show_text = Is.panel_expanded(context)

        group = getattr(obj, 'instance_collection', None)

        icon = ('GROUP', 'NONE')[show_text[0]]

        args = dict(
            operator='zpy.make_proxy', icon=icon,
            text=("", "Make Proxy..."[:(-3, None)[bool(group)]])[show_text[0]],
        )

        col = layout.column(align=True)
        if group:
            col.context_pointer_set('group', group)
            col.operator_menu_hold(**args, menu='PROXY_MT_operator_display')
        else:
            col.operator_context = 'EXEC_DEFAULT'
            col.operator(**args)
        txt = dict(text="") if not show_text[0] else dict()
        col.operator('object.make_local', **txt, icon='ASSET_MANAGER').type = 'SELECT_OBJECT'
        col.operator('object.make_override_library', **txt, icon='LIBRARY_DATA_OVERRIDE')
        # The override operator functions like the make_proxy operator
        # As in, it will search through object names
        # The difference is it will make an override for everything either way


class PROXY_MT_operator_display(bpy.types.Menu):
    bl_description = ""
    # bl_idname = 'PROXY_MT_operator_display'
    bl_label = ""

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.75
        # layout.operator_context = 'INVOKE_DEFAULT'

        obj = context.object
        group = getattr(obj, 'instance_collection', None)
        lib = group.library

        objects = list(group.objects)

        # objects from collections
        children = getattr(group, 'children', [])
        while children:
            sub = []
            for (be, col) in enumerate(children):
                sub.extend(col.children)
                objects.extend(col.objects)
            children = sub

        for o in objects:
            row = layout.row()
            row.context_pointer_set('instance', o)
            row.operator('zpy.make_proxy', text=o.name,
                icon=Get.icon_from_type(o),
            )
            # row.operator('object.proxy_make', text=o.name,
                            # icon=Get.icon_from_type(o)).object = o.name


class LINK_OT_make_proxy(bpy.types.Operator):
    bl_description = ""
    bl_idname = 'zpy.make_proxy'
    bl_label = "Make Proxy"
    # bl_options = {}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        from inspect import getmembers

        # for o in getattr(context, 'objects', [context.object]):

        if hasattr(context, 'instance'):
            instance = context.instance
            bpy.ops.object.proxy_make(object=instance.name)
        else:
            instance = context.object
            bpy.ops.object.proxy_make()

        obj = context.object

        for m in instance.modifiers:
            mod = obj.modifiers.new(m.name, m.type)

            for (prop, val) in getmembers(m):
                try:
                    if not mod.is_property_readonly(prop):
                        setattr(mod, prop, val)
                except:
                    continue

        return {'FINISHED'}
