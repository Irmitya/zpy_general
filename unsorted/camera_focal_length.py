import bpy
from mathutils import Matrix, Vector
from zpy import keyframe


class CAMERA_OT_adjust_focal_length(bpy.types.Operator):
    bl_description = ""
    bl_idname = 'zpy.adjust_camera_focal_length'
    bl_label = "Adjust Camera Focal Length"
    bl_options = {'UNDO', 'BLOCKING', 'GRAB_CURSOR'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        obj = context.object
        self.initial_x = event.mouse_x
        self.initial_matrix = obj.matrix_basis.copy()
        self.initial_lens = obj.data.lens
        self.object = repr(obj)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        obj = eval(self.object)

        if (event.type in {'MOUSEMOVE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}):
            if (event.type == 'WHEELUPMOUSE'):
                self.dof += [1, 0.1][event.shift]
            elif (event.type == 'WHEELDOWNMOUSE'):
                self.dof -= [1, 0.1][event.shift]

            # Update
            offset = (event.mouse_x - self.initial_x) * -0.01
            lens = (self.initial_lens + self.dof * offset)

            if (1 <= lens):
                obj.matrix_basis = self.initial_matrix @ Matrix.Translation(Vector((0, 0, offset)))
                obj.data.lens = lens

            text = f"Camera Lens Angle: {lens:.1f}mm" "  |  " f"Depth: {self.dof:.2f}"
            context.area.header_text_set(text)
        elif (event.type in {'LEFTMOUSE'}):
            context.area.header_text_set(None)
            if keyframe.use_auto(context):
                keyframe.location(context, obj)
                keyframe.rotation(context, obj)
                keyframe.manual(context, obj.data, 'lens')
            return {'FINISHED'}
        elif (event.type in {'RIGHTMOUSE', 'ESC'}):
            obj.matrix_basis = self.initial_matrix
            obj.data.lens = self.initial_lens
            context.area.header_text_set(None)
            # return {'CANCELLED'}
            return {'FINISHED'}  # keep the dof value

        return {'RUNNING_MODAL'}

    dof: bpy.props.FloatProperty(
        name="",
        description="",
        default=4,
        # min=-1,
        step=3,
        #   (int) – Step of increment/decrement in UI, in [1, 100], defaults to 3 (* 0.01)
        precision=2,
        #   (int) – Maximum number of decimal digits to display, in [0, 6].
        # options={'SKIP_SAVE'},
    )


class VIEWPORT_OT_adjust_focal_length(bpy.types.Operator):
    bl_description = ""
    bl_idname = 'zpy.adjust_viewport_focal_length'
    bl_label = "Adjust Viewport Focal Length"
    bl_options = {'BLOCKING', 'GRAB_CURSOR'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'VIEW_3D')

    def invoke(self, context, event):
        space = context.space_data
        self.initial_x = event.mouse_x
        self.initial_matrix = space.region_3d.view_matrix.copy()
        self.initial_lens = space.lens

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        space = context.space_data

        if (event.type in {'MOUSEMOVE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}):
            if (event.type == 'WHEELUPMOUSE'):
                self.dof += [1, 0.1][event.shift]
            elif (event.type == 'WHEELDOWNMOUSE'):
                self.dof -= [1, 0.1][event.shift]

            # Update
            offset = (event.mouse_x - self.initial_x) * 0.01
            lens = (self.initial_lens + self.dof * offset)

            if (1 <= lens <= 250):
                # Lens limit is 250; beyond that, it's just moving the viewport
                space.region_3d.view_matrix.translation.z = self.initial_matrix.translation.z - offset
                space.lens = lens

            text = f"Viewport Lens Angle: {lens:.1f}mm" "  |  " f"Depth: {self.dof:.2f}"
            context.area.header_text_set(text)
        elif (event.type in {'LEFTMOUSE'}):
            context.area.header_text_set(None)
            return {'FINISHED'}
        elif (event.type in {'RIGHTMOUSE', 'ESC'}):
            space.region_3d.view_matrix.translation.z = self.initial_matrix.translation.z
            space.lens = self.initial_lens
            context.area.header_text_set(None)
            # return {'CANCELLED'}
            return {'FINISHED'}  # keep the dof value

        return {'RUNNING_MODAL'}

    dof: bpy.props.FloatProperty(
        name="",
        description="",
        default=4,
        # min=-1,
        step=3,
        #   (int) – Step of increment/decrement in UI, in [1, 100], defaults to 3 (* 0.01)
        precision=2,
        #   (int) – Maximum number of decimal digits to display, in [0, 6].
        # options={'SKIP_SAVE'},
    )
