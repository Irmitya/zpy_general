import bpy
from zpy import keyframe


class MOVIE_OT_set_fps(bpy.types.Operator):
    bl_description = "Change the fps of the active movie clip, by animating it's start frame"
    bl_idname = 'zpy.set_movieclip_fps'
    bl_label = "Set MovieClip FPS"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_rna.description

    @classmethod
    def poll(cls, context):
        # return True
        return getattr(context.space_data, 'clip', None)

    def execute(self, context):
        if not self.fps:
            self.fps = context.scene.render.fps

        clip = context.space_data.clip

        # Create a new action or clear any existing animation
        anim = clip.animation_data_create()
        if not anim.action:
            anim.action = bpy.data.actions.new(name=clip.name)

        fc = anim.action.fcurves.find('frame_start')
        if fc:
            while fc.keyframe_points:
                fc.keyframe_points.remove(fc.keyframe_points[0])
        else:
            fc = anim.action.fcurves.new('frame_start')

        # Insert the keyframes to retime the movieclip to the scene
        off = clip.frame_offset
        start_frame = context.scene.frame_start - off
        end_frame = int(clip.frame_duration / clip.fps * self.fps) - off
        end_value = int(end_frame - clip.frame_duration)

        fc.keyframe_points.insert(start_frame, 0, options={'FAST'})
        fc.keyframe_points.insert(end_frame, end_value, options={'FAST'})
        fc.extrapolation = 'LINEAR'
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'

        return {'FINISHED'}

    fps: bpy.props.FloatProperty(
        name="Frame Rate",
        description="Set as 0 to use the scene's fps",
        default=0,
        min=0,
        options={'SKIP_SAVE'},
    )


def draw(self, context):
    layout = self.layout
    layout.operator('zpy.set_movieclip_fps')


def register():
    bpy.types.CLIP_PT_footage.append(draw)
    # bpy.types.DATA_PT_camera_background_image.append(draw)


def unregister():
    bpy.types.CLIP_PT_footage.remove(draw)
    # bpy.types.DATA_PT_camera_background_image.remove(draw)
