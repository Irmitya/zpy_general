import bpy


class SEQUENCER_OT_aspect_ratio(bpy.types.Operator):
    bl_description = "Add Transform controller to selected movie sequences and match scene aspect ratio"
    bl_idname = 'zpy.sequencer_aspect_ratio'
    bl_label = "Sequencer to Scene Aspect Ratio"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        def scan(seq):
            if (seq.type in ('IMAGE', 'MOVIE')):
                return True
            elif (seq.type == 'META'):
                for sub in seq.sequences:
                    result = scan(sub)
                    if result:
                        return True
            elif (seq.type == 'TRANSFORM') and (seq.input_1 is not None):
                return scan(seq.input_1)

        for seq in context.selected_sequences:
            if scan(seq):
                return True

    def invoke(self, context, event):
        self.selected = event.alt
        return self.execute(context)

    def execute(self, context):
        seq_ed = context.scene.sequence_editor

        def scan(seq, meta=None):
            if (seq.type in ('IMAGE', 'MOVIE')):
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
            elif (seq.type == 'TRANSFORM') and (seq.input_1 is not None):
                scan(seq.input_1, meta)

        if self.selected:
            for seq in context.selected_sequences:
                scan(seq)
        else:
            scan(act_strip(context))

        return {'FINISHED'}

    def process(self, context, seq):
        scn = context.scene
        seqs = scn.sequence_editor.sequences
        res = (scn.render.resolution_x, scn.render.resolution_y)
        prefix = '(Aspect Ratio) '

        if (seq.type == 'IMAGE'):
            # Current element for the filename.
            elem = seq.strip_elem_from_frame(scn.frame_current)
        else:  # elif (seq.type == 'MOVIE'):
            elem = seq.elements[0]

        size = (elem.orig_width, elem.orig_height) if elem else (0, 0)
        if not (size[0] and size[1]):
            return

        def scan(top):
            for strip in seqs:
                if getattr(strip, 'input_1', None) != top:
                    continue

                if (strip.type == 'TRANSFORM') and (strip.name.startswith(prefix)):
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
        if top and (top.type == 'TRANSFORM') and (top.name.startswith(prefix)):
            # Transformer already on strip, so continue
            effect = top
        else:
            if top is None:
                top = seq

            # Find an empty channel/layer
            channel = top.channel + 1
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
                name, 'TRANSFORM', channel, seq_start, seq1=top)

        if min(size) == size[1]:
            # Height is smaller than Width (widescreen)
            effect.scale_start_y = (size[1] / size[0] * res[0] / res[1]) * effect.scale_start_x
        else:
            # Width is smaller than Height (phonescreen)
            effect.scale_start_x = (size[0] / size[1] * res[1] / res[0]) * effect.scale_start_y

    selected: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})


class SEQUENCER_PT_aspect_ratio(bpy.types.Panel):
    bl_category = "Strip"
    bl_label = "Strip Aspect Ratio"
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
        layout.operator('zpy.sequencer_aspect_ratio', text="Set to Scene Aspect Ratio")

        seq = act_strip(context)
        scn = context.scene

        if (seq.type == 'IMAGE'):
            # Current element for the filename.
            elem = seq.strip_elem_from_frame(scn.frame_current)
        else:  # elif (seq.type == 'MOVIE'):
            elem = seq.elements[0]

        res = (scn.render.resolution_x, scn.render.resolution_y)
        size = (elem.orig_width, elem.orig_height) if elem else (0, 0)
        if all(res) and all(size):
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text=f"{size[0]}x{size[1]} > {res[0]}x{res[1]}")


def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


def draw(self, context):
    layout = self.layout
    # layout.separator(factor=1.0)
    layout.operator('zpy.sequencer_aspect_ratio', text="Set to Scene Aspect Ratio")


def register():
    # bpy.types.SEQUENCER_MT_add_effect.append(draw)
    bpy.types.SEQUENCER_MT_add.append(draw)


def unregister():
    # bpy.types.SEQUENCER_MT_add_effect.remove(draw)
    bpy.types.SEQUENCER_MT_add.remove(draw)
