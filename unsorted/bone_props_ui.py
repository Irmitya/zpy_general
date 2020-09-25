import bpy
from bpy.types import PoseBone, Panel, PropertyGroup
from zpy import utils


class CUSTOM_PROPS_PT_bone(Panel):
    bl_category = "Item"
    bl_label = "Custom Properties"
    bl_options = {'DEFAULT_CLOSED'}
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'

    @classmethod
    def poll(cls, context):
        bone = context.active_pose_bone

        if bone:
            rna_properties = {
                prop.identifier for prop in PoseBone.bl_rna.properties
                if prop.is_runtime
            }

            for key in bone.keys():
                if key == '_RNA_UI' or key in rna_properties:
                    continue
                return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        bone = context.active_pose_bone

        rna_properties = {
            prop.identifier for prop in PoseBone.bl_rna.properties
            if prop.is_runtime
        }

        row = layout.column(align=True)
        for (key, val) in bone.items():
            if (key == '_RNA_UI') or (key in rna_properties):
                continue

            to_dict = getattr(val, "to_dict", None)
            to_list = getattr(val, "to_list", None)

            if to_dict:
                val = to_dict()
                val_draw = str(val)
            elif to_list:
                val = to_list()
                val_draw = str(val)
            else:
                val_draw = val

            # explicit exception for arrays.
            show_array_ui = (to_list and (0 < len(val) <= 4))

            if show_array_ui and isinstance(val[0], (int, float)):
                row.prop(bone, f'["{key}"]', text="")
            elif to_dict or to_list:
                row.label(text=val_draw, translate=False)
            else:
                row.prop(bone, f'["{key}"]', text=key, slider=True)


# class cprops(PropertyGroup):
    # pass


# def register():
    # PoseBone.custom_props = utils.register_collection(cprops)


# def unregister():
    # del PoseBone.custom_props
