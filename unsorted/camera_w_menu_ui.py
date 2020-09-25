import bpy
from zpy import popup, New, Set, Is


def draw_menu(self, context):
    layout = self.layout

    def modal(op, iter, item, text):
        op.data_path_iter = iter
        op.data_path_item = item
        op.header_text = text
        # input_scale=0.01, invert=False, initial_x=0
        return op
    op = 'zpy.context_modal_mouse'

    obj = context.object
    space = context.area.spaces.active

    if space.camera:
        view = space.camera
    else:
        view = context.scene.camera

    if Is.camera(view):
        camera = view.data
    else:
        camera = None
    camera_view = (space.region_3d.view_perspective == 'CAMERA')

    # if not (camera or camera_view or Is.camera(obj)):
        # return

    col = layout.column()
    col.operator_context = 'INVOKE_REGION_WIN'

    if Is.camera(obj):
        col.prop(obj.data, 'display_size')

    # Properties
    if (camera and camera_view):
        if camera.show_passepartout:
            col.prop(camera, 'passepartout_alpha')
        else:
            col.prop(camera, 'show_passepartout')

        col.prop(space, 'lock_camera')

        if space.lock_camera:
            col.operator('view3d.view_center_camera', text="Center Viewport")
                # Re-center the camera view window if it was changed
                # space.region_3d.view_camera_offset = [0.0, 0.0]
            modal(
                col.operator(op, text="Viewport Zoom", icon='PARTICLE_DATA'),
                'area', 'spaces.active.region_3d.view_camera_zoom',
                "Viewport Zoom: %.1f",
            )
        col.separator()

    if not camera_view:
        col.operator('zpy.adjust_viewport_focal_length', text="Viewport Focal Length")
        modal(
            col.operator(op, text="Viewport Lens Angle"),
            'space_data', 'lens', "Viewport Lens Angle: %.1fmm",
        )
        col.separator()

    if camera:
        if space.camera:
            args = ('area', 'spaces.active.camera.data.dof.aperture_fstop')
        else:
            args = ('scene', 'camera.data.dof.aperture_fstop')

        row = col.row()
        if not Is.camera(obj):
            row.context_pointer_set('object', view)
        row.operator('zpy.adjust_camera_focal_length', text="Camera Focal Length")

        if not Is.camera(obj):
            # if active object is a different camera,
                # it would display a separate operator to control each camera
            if space.camera:
                args = ('area', 'spaces.active.camera.data.lens')
            else:
                args = ('scene', 'camera.data.lens')
            modal(
                col.operator(op, text="Camera Lens Angle"),
                *args, "Camera Lens Angle: %.1fmm",
            )

        modal(
            col.operator(
                op, text=f"DOF F-Stop    ({camera.dof.aperture_fstop:.2f})"),
            *args,
            "Aperature F-Stop: %.4f",
        ).input_scale = 0.0003
        if camera_view and not Is.camera(obj):
            col.operator('ui.eyedropper_depth', text="DOF Distance (Pick)")
        if not camera_view:
            col.separator()


def draw_append(self, context):
    layout = self.layout
    layout.menu('CAMERA_MT_controls')


class CAMERA_MT_controls(bpy.types.Menu):
    bl_description = ""
    bl_label = "Camera Controls"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        draw_menu(self, context)


menues = (
    bpy.types.VIEW3D_MT_pose_context_menu,
    bpy.types.VIEW3D_MT_object_context_menu,
)


def register():
    for menu in menues:
        menu.prepend(draw_menu)
    bpy.types.VIEW3D_MT_view.append(draw_append)


def unregister():
    bpy.types.VIEW3D_MT_view.remove(draw_append)
    for menu in menues:
        menu.remove(draw_menu)
