import bpy


class ops:
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_rna.description

    @classmethod
    def poll(cls, context):
        def scan(seq):
            if (seq.type == 'MOVIE'):
                return True
            elif (seq.type == 'META'):
                for sub in seq.sequences:
                    result = scan(sub)
                    if result:
                        return True

        for seq in context.selected_sequences:
            if scan(seq):
                return True

    def invoke(self, context, event):
        self.selected = event.alt
        return self.execute(context)

    def execute(self, context):
        seq_ed = context.scene.sequence_editor

        def scan(seq, meta=None):
            if (seq.type == 'MOVIE'):
                # Found the real strip that needs adjusting
                if meta:
                    # Need to open the metastrip to add effect inside it
                    active = seq_ed.active_strip
                    seq_ed.active_strip = meta
                    bpy.ops.sequencer.meta_toggle()
                    self.process(context, seq)
                    bpy.ops.sequencer.meta_toggle()
                    seq_ed.active_strip = active
                else:
                    self.process(context, seq)
            elif (seq.type == 'META'):
                # Need to find an actual video strip inside this strip
                for sub in seq.sequences:
                    scan(sub, seq)

        if self.selected:
            for seq in context.selected_sequences:
                scan(seq)
        else:
            scan(act_strip(context))

        return {'FINISHED'}

    selected: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})


class SEQUENCER_OT_retime_fps(bpy.types.Operator, ops):
    bl_description = "Add Speed controller to selected movie sequences and match scene fps"
    bl_idname = 'zpy.retime_sequencer_fps'
    bl_label = "Retime Sequencer FPS"

    def process(self, context, seq):
        scn = context.scene
        seqs = scn.sequence_editor.sequences
        scn_fps = (scn.render.fps / scn.render.fps_base)
        prefix = "(FPS) "

        if ('fps' not in seq) and (seq.fps == scn_fps):
            return

        def scan(top):
            for strip in seqs:
                if getattr(strip, 'input_1', None) != top:
                    continue

                if (strip.type == 'SPEED') and (strip.name.startswith(prefix)):
                    return strip
                else:
                    sub = scan(strip)
                    if sub:
                        # Found controller
                        return sub
                    else:
                        # Found last strip connected to original
                        return strip

        top = scan(seq)
        if top and (top.type == 'SPEED') and (top.name.startswith(prefix)):
            # Transformer already on strip, so continue
            effect = top
        else:
            if top is None:
                top = seq

            # Find an empty channel/layer
            channel = seq.channel + 1
            seq_start = seq.frame_final_start
            seq_end = seq.frame_final_end
            layers = [s for s in seqs if s.channel >= channel]
            while layers:
                for ch in layers:
                    if ch.channel != channel:
                        continue
                    if (seq_start <= ch.frame_final_start <= seq_end) or (
                        seq_start <= ch.frame_final_end <= seq_end):
                        # Conflict found; go to next layer
                        channel += 1
                        break
                else:
                    # No more conflicts, exit while loop
                    break

            name = prefix + seq.name
            effect = seqs.new_effect(
                name, 'SPEED', channel, seq_start, seq1=top)

        fps = seq.get('fps', seq.fps)
        seq.frame_final_duration /= fps
        seq.frame_final_duration *= scn_fps
        seq['fps'] = scn_fps

        if (effect.input_1 != seq):
            # Was added to a different strip, so need to use speed factor
            effect.multiply_speed = (seq.fps / scn_fps)

        if (seq.fps == scn_fps):
            if ('_RNA_UI' in seq) and ('fps' in seq['_RNA_UI']):
                del seq['_RNA_UI']['fps']
                if not seq['_RNA_UI']:
                    del seq['_RNA_UI']
            del seq['fps']
        else:
            if '_RNA_UI' not in seq:
                seq['_RNA_UI'] = dict()
            seq['_RNA_UI']['fps'] = {
                # 'min': -10000.0, 'max': 10000.0,
                # 'soft_min': -10000.0, 'soft_max': 10000.0,
                'description': "Strip's current frame rate scaled to the scene's",
                'default': seq.fps,
            }


class SEQUENCER_OT_reset_fps(bpy.types.Operator, ops):
    bl_description = "Remove Speed controller from selected movie sequences and reset fps"
    bl_idname = 'zpy.reset_sequencer_fps'
    bl_label = "Reset Sequencer FPS"

    def process(self, context, seq):
        seqs = context.scene.sequence_editor.sequences
        strips = list()
        prefix = "(FPS) "

        def scan(top):
            for strip in seqs:
                if getattr(strip, 'input_1', None) != top:
                    continue

                if (strip.type == 'SPEED') and (strip.name.startswith(prefix)):
                    return strip
                else:
                    sub = scan(strip)
                    if sub:
                        # Found controller
                        return sub

        if 'fps' in seq:
            effect = scan(seq)

            # for effect in seqs.values():
                # if (effect.type == 'SPEED') and (effect.name.startswith(prefix)) and (effect.input_1 in strips):
            if effect:
                seqs.remove(effect)

            seq.frame_final_duration /= seq['fps']
            seq.frame_final_duration *= seq.fps
            del seq['fps']


class SEQUENCER_PT_retime_fps(bpy.types.Panel):
    bl_category = "Strip"
    bl_label = "Retime Strip FPS"
    bl_region_type = 'UI'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_parent_id = 'SEQUENCER_PT_adjust'

    @classmethod
    def poll(cls, context):
        if (context.space_data.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}):
            return (act_strip(context) is not None)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        seq = act_strip(context)

        if (seq.type == 'MOVIE') and (seq.get('fps', seq.fps) == seq.fps):
            layout.operator('zpy.retime_sequencer_fps', text="Set to Scene FPS")
            layout.prop(seq, 'fps')
        else:
            row = layout.row(align=True)
            row.operator('zpy.retime_sequencer_fps', text="Set to Scene FPS")
            row.operator('zpy.reset_sequencer_fps', text="", icon='CANCEL')

            if (seq.type == 'MOVIE'):
                row = layout.split()
                row.enabled = False
                row.prop(seq, 'fps', text="Base FPS")
                row.prop(seq, '["fps"]', text="FPS")


def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


def draw(self, context):
    layout = self.layout
    # layout.separator(factor=1.0)
    layout.operator('zpy.retime_sequencer_fps', text="Set to Scene FPS")


def register():
    # bpy.types.SEQUENCER_MT_add_effect.append(draw)
    bpy.types.SEQUENCER_MT_add.append(draw)


def unregister():
    # bpy.types.SEQUENCER_MT_add_effect.remove(draw)
    bpy.types.SEQUENCER_MT_add.remove(draw)
