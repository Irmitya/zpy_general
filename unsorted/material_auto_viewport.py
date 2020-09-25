import bpy


class MAT_OT_convert_viewport(bpy.types.Operator):
    "Copy Metalness and Roughness from nodes, to viewport display" \
    ".\nCtrl Click to apply to object's materials" \
    ".\nAlt Click to apply to all materials"
    bl_idname = 'zpy.material_viewport_convert'
    bl_label = "Convert Principled to Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return True

    def invoke(self, context, event):
        if event.ctrl:
            self.materials = [m for m in context.object.data.materials]
        if event.alt:
            self.materials = bpy.data.materials

        return self.execute(context)

    def execute(self, context):
        mats = getattr(self, 'materials', [context.material])

        # for mat in mats:
            # for node in getattr(mat.node_tree, 'nodes', []):
                # if node.type == 'OUTPUT_MATERIAL':
                    # parse_tree(mat, node)

        def scan_node(node, mat):
            if node.type == 'BSDF_PRINCIPLED':
                mat.metallic = node.inputs['Metallic'].default_value
                mat.roughness = node.inputs['Roughness'].default_value

                return True

        def scan_tree(tree, mat):
            for node in getattr(tree.node_tree, 'nodes', []):
                if scan_node(node, mat) and not node.mute:
                    return True
                elif node.type == 'GROUP':
                    if scan_tree(node, mat) and not node.mute:
                        return True

        for mat in mats:
            scan_tree(mat, mat)

        return {'FINISHED'}


def draw_material_button(self, context):
    self.layout.operator(f'zpy.material_viewport_convert')


def register():
    bpy.types.MATERIAL_PT_viewport.append(draw_material_button)


def unregister():
    bpy.types.MATERIAL_PT_viewport.remove(draw_material_button)
