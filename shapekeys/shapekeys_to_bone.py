# import bpy
# from bpy.props import BoolProperty
# from zpy import Get


# class SHAPEKEYS_OT_to_bone(bpy.types.Operator):
    # bl_description = ""
    # bl_idname = 'zpy.shapekeys_to_bone'
    # bl_label = "Shapekeys to Bone"
    # bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def description(cls, context, properties):
        # return cls.bl_description

    # @classmethod
    # def poll(cls, context):
        # return context.active_pose_bone

    # # def invoke(self, context, event):
        # # return self.execute(context)

    # def execute(self, context):
        # return {'FINISHED'}

    # add_drivers: BoolProperty(
        # name="Add Drivers",
        # description="Drive the available shapekeys, using the newly added sliders on the bone",
        # default=True,
        # options={'SKIP_SAVE'},
    # )
    # all_shapes: BoolProperty(
        # name="All Shapes",
        # description="Add Slider for shapekeys even if they already have a driver",
        # default=False,
        # options={'SKIP_SAVE'},
    # )
