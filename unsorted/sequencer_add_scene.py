import bpy


class SEQUENCER_MT_add_scene(bpy.types.Menu):
    bl_description = ""
    bl_label = ""

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.operator('sequencer.add_active_scene', icon='SCENE_DATA')


class SEQUENCER_OT_add_scene(bpy.types.Operator):
    bl_description = "Add current scene sequencer (Blender refuses to list active scene in scene list)"
    bl_idname = 'sequencer.add_active_scene'
    bl_label = "Add Active Scene"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        scn = context.scene
        seqs = scn.sequence_editor_create().sequences
        channel = 0

        for seq in seqs:
            while seq.channel >= channel:
                channel += 1
        else:
            seqs.new_scene(
                name=scn.name,
                scene=scn,
                channel=channel,
                frame_start=scn.frame_start,
            )

        return {'FINISHED'}


def register():
    bpy.types.SEQUENCER_MT_add.append(SEQUENCER_MT_add_scene.draw)


def unregister():
    bpy.types.SEQUENCER_MT_add.remove(SEQUENCER_MT_add_scene.draw)
