import bpy


class MATS_OT_decompact(bpy.types.Operator):
    bl_description = "Go through materials and align nodes"
    bl_idname = 'zpy.decompact_node_trees'
    bl_label = "Decompact Nodes"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        def sort_inputs(output):
            if output in nodes:
                # avoid cycle loop for dummies
                return
            else:
                nodes.append(output)

            for input in output.inputs:
                if not input.links:
                    # Nothing is connected to the socket
                    continue

                node = input.links[0].from_node

                if not hasattr(node, 'location'):
                    print('bad node?')
                    continue

                node.location.x = (output.location.x - (node.width + 50))
                if (node.type == 'BSDF_PRINCIPLED') and (output.type == 'OUTPUT_MATERIAL'):
                    node.location.y = (output.location.y)
                elif (node.type == 'TEX_IMAGE') and (output.type == 'NORMAL_MAP'):
                    node.location.y = (output.location.y)
                if (output.type == 'BSDF_PRINCIPLED'):
                    if (node.type == 'NORMAL_MAP'):
                        node.location.y = (output.location.y - 480)
                    elif (node.type == 'TEX_IMAGE'):
                        if input.identifier == 'Base Color':
                            node.location.y = (output.location.y - 80)
                        elif input.identifier == 'Specular':
                            node.location.y = (output.location.y - 185)
                sort_inputs(node)

        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue

            nodes = list()
            node_tree = mat.node_tree.nodes

            for node in node_tree:
                if node.type == 'OUTPUT_MATERIAL':
                    sort_inputs(node)
                node.select = (node == node_tree.active)

            for node in node_tree.values():
                if node.name == 'Principled BSDF.001':
                    other = node_tree.get('Principled BSDF')
                    if other:
                        if other not in nodes:
                            node_tree.remove(other)
                        else:
                            continue
                    node.name = 'Principled BSDF'

        return {'FINISHED'}


class MATS_PT_tool(bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_region_type = 'TOOLS'
    bl_space_type = 'NODE_EDITOR'

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.operator('zpy.decompact_node_trees', icon='NODE_COMPOSITING')
