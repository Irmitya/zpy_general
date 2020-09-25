import bpy
from zpy import popup, New, Set  # , register_keymaps
# km = register_keymaps()


class CAM_OT_to_viewport(bpy.types.Operator):
    bl_description = "Convert the active viewport into a camera object"
    bl_idname = 'zpy.add_camera'
    bl_label = "Viewport to New Camera"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return True

    def invoke(self, context, event):
        return popup.invoke_confirm(context, self, event)

    def execute(self, context):
        area = context.area
        view = area.spaces.active
        reg = view.region_3d

        # Create new camera object, add to scene, and select it
        camo = New.camera(context, name="Viewport", size=0.5)
        cam = camo.data
        Set.active(context, camo)
            # Set.active_select(camo)

        # Set Lock viewport to the camera
        view.camera = camo
        view.use_local_camera = True
        view.lock_camera = True

        # Send camera object to the current viewport rotation/location
        Set.matrix(camo, reg.view_matrix.inverted())

        # Switch to camera view
        if reg.view_perspective != 'CAMERA':
            bpy.ops.view3d.view_camera()
            # run op to prevent changing the (actual) viewport's position
        # reg.view_perspective = 'CAMERA'

        # Mirror viewport properties to the camera
        cam.lens = view.lens / 2
        cam.clip_start = view.clip_start
        cam.clip_end = view.clip_end

        # Re-center the camera view window if it was changed
        bpy.ops.view3d.view_center_camera()
            # reg.view_camera_offset = [0.0, 0.0]
            # reg.view_camera_zoom = 28

        # Setup Deph of Field
        cam.dof.use_dof = True
        # cam.dof.aperture_fstop = 0.5  # Blur amount
            # cam.dof.aperture_fstop = 2.8
        # cam.dof.focus_distance = reg.view_distance
        bpy.ops.ui.eyedropper_depth('INVOKE_DEFAULT')

        return {'FINISHED'}


def draw(self, context):
    layout = self.layout
    cam = layout.row()
    cam.operator_context = 'EXEC_DEFAULT'
    cam.operator('zpy.add_camera', icon='CAMERA_DATA')


def register():
    # km.add(CAM_OT_to_viewport, name='3D View', type='F8', value='PRESS')
    bpy.types.VIEW3D_MT_camera_add.append(draw)


def unregister():
    # km.remove()
    bpy.types.VIEW3D_MT_camera_add.remove(draw)
