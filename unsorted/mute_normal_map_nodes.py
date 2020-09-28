import bpy
from bpy.app.handlers import persistent, load_post
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator, Panel
from mathutils import Color, Vector
from zpy import Is

# https://developer.blender.org/T64458
# https://blenderartists.org/t/1175379


class MUT_OT_normal_map_nodes(Operator):
    bl_description = "Toggle all normal map nodes off/on"
    bl_idname = 'nodes.mutation'
    bl_label = "Un/Mute Normal Map nodes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return (bpy.data.materials or bpy.data.node_groups)

    def execute(self, context):
        if self.mute == 'toggle':
            mute = None
        elif self.mute == 'off':
            mute = False
        elif self.mute == 'on':
            mute = True

        def mute_nodes(nodes):
            nonlocal mute
            for node in nodes:
                if isinstance(node, bpy.types.ShaderNodeNormalMap):
                    if mute is None:
                        mute = node.mute
                    node.mute = not mute

        for mat in bpy.data.materials:
            mute_nodes(getattr(mat.node_tree, 'nodes', []))
        for group in bpy.data.node_groups:
            mute_nodes(group.nodes)

        return {'FINISHED'}

    mute: EnumProperty(
        items=[
            ('off', "Off", "Disable all"),
            ('on', "On", "Enable all"),
            ('toggle', "Toggle", "Invert values"),
            ],
        name="Un/Mute",
        description="Mode to set for all normal map nodes",
        default='toggle',
        options={'SKIP_SAVE'},
    )


class MAT_OT_remove_internal(Operator):
    bl_description = "Delete Undefined nodes from all materials"
    bl_idname = 'zpy.mats_remove_undefined'
    bl_label = "Remove Undefined nodes"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return (bpy.data.materials or bpy.data.node_groups)

    def execute(self, context):
        def remove_none(nodes):
            for n in nodes:
                if not n.type:
                    m.node_tree.nodes.remove(n)

        for mat in bpy.data.materials:
            remove_none(getattr(mat.node_tree, 'nodes', []))
        for group in bpy.data.node_groups:
            remove_none(group.nodes)

        return {'FINISHED'}


class MAT_OT_custom_normal(Operator):
    bl_description = "Switch normal map nodes to a faster custom node"
    bl_idname = 'zpy.mats_custom_normals'
    bl_label = "Normal Map nodes to Custom"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return (bpy.data.materials or bpy.data.node_groups)

    def execute(self, context):
        def mirror(new, old):
            """Copy attributes of the old node to the new node"""
            new.parent = old.parent
            new.label = old.label
            new.mute = old.mute
            new.hide = old.hide
            new.select = old.select
            new.location = old.location

            # inputs
            for (name, point) in old.inputs.items():
                input = new.inputs.get(name)
                if input:
                    input.default_value = point.default_value
                    for link in point.links:
                        new.id_data.links.new(link.from_socket, input)

            # outputs
            for (name, point) in old.outputs.items():
                output = new.outputs.get(name)
                if output:
                    output.default_value = point.default_value
                    for link in point.links:
                        new.id_data.links.new(output, link.to_socket)

        def get_custom():
            name = 'Normal Map Optimized'
            group = bpy.data.node_groups.get(name)

            if not group and self.custom:
                group = default_custom_nodes()

            return group

        def set_custom(nodes):
            group = get_custom()
            if not group:
                return

            for node in nodes:
                new = None
                if self.custom:
                    if isinstance(node, bpy.types.ShaderNodeNormalMap):
                        new = nodes.new(type='ShaderNodeGroup')
                        new.node_tree = group
                else:
                    if isinstance(node, bpy.types.ShaderNodeGroup):
                        if node.node_tree == group:
                            new = nodes.new(type='ShaderNodeNormalMap')

                if new:
                    name = node.name
                    mirror(new, node)
                    nodes.remove(node)
                    new.name = name

        for mat in bpy.data.materials:
            set_custom(getattr(mat.node_tree, 'nodes', []))
        for group in bpy.data.node_groups:
            set_custom(group.nodes)

        if (not self.custom) and get_custom():
            bpy.data.node_groups.remove(get_custom())

        return {'FINISHED'}

    custom: BoolProperty(
        name="To Custom",
        description="Set all normals to custom group, or revert back to normal",
        default=True,
    )


class IMAGES_OT_remap_duplicates(Operator):
    bl_description = "Find images ending with .### and replace them with the base"\
        ".\n For usage with SFM importer. It duplicates textures unnecessarily"
    bl_idname = 'zpy.remap_duplicate_images'
    bl_label = "Remap Duplicate Images"
    bl_options = {'UNDO'}

    @classmethod
    def description(cls, context, properties):
        return cls.bl_rna.description

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for img in bpy.data.images:
            end = img.name[-4:]
            if end.startswith('.') and Is.digit(end[1:]) and len(end) == 4:
                ipre = bpy.data.images.get(img.name[:-4])
                if ipre:
                    img.user_remap(ipre)

        return {'FINISHED'}


class MUT_PT_normal_map_nodes(Panel):
    bl_category = ""
    bl_label = "Batch Material Operations"
    bl_options = {'HIDE_HEADER'}
    bl_region_type = 'TOOLS'
    bl_space_type = 'NODE_EDITOR'

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        mut = MUT_OT_normal_map_nodes.bl_idname
        col.operator(MAT_OT_custom_normal.bl_idname, text="Custom").custom = True
        col.operator(MAT_OT_custom_normal.bl_idname, text="Normal").custom = False
        col.operator(mut, text="On").mute = 'on'
        col.operator(mut, text="Off").mute = 'off'
        col.operator(mut, text="Toggle").mute = 'toggle'

        layout.operator(MAT_OT_remove_internal.bl_idname,
                        text="Remove Undefined", icon='CANCEL')

        layout.operator(IMAGES_OT_remap_duplicates.bl_idname,
                        text="Remap Duplicates")


def default_custom_nodes():
    group = bpy.data.node_groups.new('Normal Map Optimized', 'ShaderNodeTree')

    nodes = group.nodes
    links = group.links

    # Input
    input = group.inputs.new('NodeSocketFloat', 'Strength')
    input.default_value = 1.0
    input.min_value = 0.0
    input.max_value = 1.0
    input = group.inputs.new('NodeSocketColor', 'Color')
    input.default_value = ((0.5, 0.5, 1.0, 1.0))

    # Output
    group.outputs.new('NodeSocketVector', 'Normal')

    # Add Nodes
    frame = nodes.new('NodeFrame')
    frame.name = 'Matrix * Normal Map'
    frame.label = 'Matrix * Normal Map'
    frame.location = Vector((540.0, -80.0))
    frame.hide = False
    frame.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node = nodes.new('ShaderNodeVectorMath')
    node.name = 'Vector Math'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-60.0, 20.0))
    node.operation = 'DOT_PRODUCT'
    node.inputs[0].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs[1].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs['Scale'].default_value = 1.0  # Scale  [2]  (3 in 2.83)
    node = nodes.new('ShaderNodeVectorMath')
    node.name = 'Vector Math.001'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-60.0, -20.0))
    node.operation = 'DOT_PRODUCT'
    node.inputs[0].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs[1].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs['Scale'].default_value = 1.0  # Scale  [2]  (3 in 2.83)
    node = nodes.new('ShaderNodeVectorMath')
    node.name = 'Vector Math.002'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-60.0, -60.0))
    node.inputs[0].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs[1].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs['Scale'].default_value = 1.0  # Scale  [2]  (3 in 2.83)
    node.operation = 'DOT_PRODUCT'
    node = nodes.new('ShaderNodeCombineXYZ')
    node.name = 'Combine XYZ'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((100.0, -20.0))
    node.inputs['X'].default_value = 0.0  # X  [0]
    node.inputs['Y'].default_value = 0.0  # Y  [1]
    node.inputs['Z'].default_value = 0.0  # Z  [2]

    frame = nodes.new('NodeFrame')
    frame.name = 'Generate TBN from Bump Node'
    frame.label = 'Generate TBN from Bump Node'
    frame.location = Vector((-192.01412963867188, -77.50459289550781))
    frame.hide = False
    frame.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node = nodes.new('ShaderNodeUVMap')
    node.name = 'UV Map'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-247.98587036132812, -2.4954071044921875))
    node = nodes.new('ShaderNodeSeparateXYZ')
    node.name = 'UV Gradients'
    node.label = 'UV Gradients'
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-87.98587036132812, -2.4954071044921875))
    node.inputs[0].default_value = (0.0, 0.0, 0.0)  # Vector
    # node.outputs.remove((node.outputs['Z']))
    node = nodes.new('ShaderNodeNewGeometry')
    node.name = 'Normal'
    node.label = 'Normal'
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((72.01412963867188, -62.49540710449219))
    # for out in node.outputs:
    #     if out.name not in ['Normal']:
    #         node.outputs.remove(out)
    node = nodes.new('ShaderNodeBump')
    node.name = 'Bi-Tangent'
    node.label = 'Bi-Tangent'
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((72.01412963867188, -22.495407104492188))
    node.invert = True
    node.inputs['Strength'].default_value = 1.0  # Strength  [0]
    node.inputs['Distance'].default_value = 1000.0  # Distance  [1]
    node.inputs['Height'].default_value = 1.0  # Height  [2]
    node.inputs['Height_dx'].default_value = 1.0  # Height_dx  [3]
    node.inputs['Height_dy'].default_value = 1.0  # Height_dy  [4]
    node.inputs['Normal'].default_value = (0.0, 0.0, 0.0)  # Normal  [5]
    # for inp in node.inputs:
    #     if inp.name not in ['Height']:
    #         node.inputs.remove(inp)
    node = nodes.new('ShaderNodeBump')
    node.name = 'Tangent'
    node.label = 'Tangent'
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((72.01412963867188, 17.504592895507812))
    node.invert = True
    # for inp in node.inputs:
    #     if inp.name not in ['Height']:
    #         node.inputs.remove(inp)

    frame = nodes.new('NodeFrame')
    frame.name = 'Node'
    frame.label = 'Normal Map Processing'
    frame.location = Vector((180.0, -260.0))
    frame.hide = False
    frame.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node = nodes.new('NodeGroupInput')
    node.name = 'Group Input'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-400.0, 20.0))
    node = nodes.new('ShaderNodeMixRGB')
    node.name = 'Influence'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.location = Vector((-240.0, 20.0))
    node.inputs['Color1'].default_value = (0.5, 0.5, 1.0, 1.0)  # Color1  [1]
    node = nodes.new('ShaderNodeVectorMath')
    node.name = 'Vector Math.003'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-80.0, 20.0))
    node.operation = 'SUBTRACT'
    node.inputs[0].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs[1].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs['Scale'].default_value = 1.0  # Scale  [2]  (3 in 2.83)
    # node.inputs.remove(node.inputs[1])
    node = nodes.new('ShaderNodeVectorMath')
    node.name = 'Vector Math.004'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((80.0, 20.0))
    node.inputs[0].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs[1].default_value = (0.5, 0.5, 0.5)  # Vector
    node.inputs['Scale'].default_value = 1.0  # Scale  [2]  (3 in 2.83)

    frame = nodes.new('NodeFrame')
    frame.name = 'Transpose Matrix'
    frame.label = 'Transpose Matrix'
    frame.location = Vector((180.0, -80.0))
    frame.hide = False
    frame.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node = nodes.new('ShaderNodeCombineXYZ')
    node.name = 'Combine XYZ.001'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((80.0, 20.0))
    node.inputs['X'].default_value = 0.0  # X  [0]
    node.inputs['Y'].default_value = 0.0  # Y  [1]
    node.inputs['Z'].default_value = 0.0  # Z  [2]
    node = nodes.new('ShaderNodeCombineXYZ')
    node.name = 'Combine XYZ.002'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((80.0, -20.0))
    node.inputs['X'].default_value = 0.0  # X  [0]
    node.inputs['Y'].default_value = 0.0  # Y  [1]
    node.inputs['Z'].default_value = 0.0  # Z  [2]
    node = nodes.new('ShaderNodeCombineXYZ')
    node.name = 'Combine XYZ.003'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((80.0, -60.0))
    node.inputs['X'].default_value = 0.0  # X  [0]
    node.inputs['Y'].default_value = 0.0  # Y  [1]
    node.inputs['Z'].default_value = 0.0  # Z  [2]
    node = nodes.new('ShaderNodeSeparateXYZ')
    node.name = 'Separate XYZ.001'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-80.0, 20.0))
    node.inputs[0].default_value = (0.0, 0.0, 0.0)  # Vector
    node = nodes.new('ShaderNodeSeparateXYZ')
    node.name = 'Separate XYZ.002'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-80.0, -20.0))
    node.inputs[0].default_value = (0.0, 0.0, 0.0)  # Vector
    node = nodes.new('ShaderNodeSeparateXYZ')
    node.name = 'Separate XYZ.003'
    node.label = ''
    node.parent = frame
    node.hide = True
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.location = Vector((-80.0, -60.0))
    node.inputs[0].default_value = (0.0, 0.0, 0.0)  # Vector

    node = nodes.new('NodeGroupOutput')
    node.name = 'Group Output'
    node.label = ''
    node.location = Vector((840.0, -80.0))
    node.hide = False
    node.color = Color((0.6079999804496765, 0.6079999804496765, 0.6079999804496765))
    node.inputs['Normal'].default_value = (0.0, 0.0, 0.0)  # Normal  [0]

    # Connect the nodes
    links.new(nodes['Group Input'].outputs['Strength'], nodes['Influence'].inputs[0])
    links.new(nodes['Group Input'].outputs['Color'], nodes['Influence'].inputs[2])
    links.new(nodes['Influence'].outputs['Color'], nodes['Vector Math.003'].inputs[0])
    links.new(nodes['UV Gradients'].outputs['X'], nodes['Tangent'].inputs['Height'])
    links.new(nodes['UV Gradients'].outputs['Y'], nodes['Bi-Tangent'].inputs['Height'])
    links.new(nodes['UV Map'].outputs['UV'], nodes['UV Gradients'].inputs['Vector'])
    links.new(nodes['Tangent'].outputs['Normal'], nodes['Separate XYZ.001'].inputs[0])
    links.new(nodes['Bi-Tangent'].outputs['Normal'], nodes['Separate XYZ.002'].inputs[0])
    links.new(nodes['Normal'].outputs['Normal'], nodes['Separate XYZ.003'].inputs[0])
    links.new(nodes['Vector Math.004'].outputs['Vector'], nodes['Vector Math'].inputs[1])
    links.new(nodes['Combine XYZ.001'].outputs['Vector'], nodes['Vector Math'].inputs[0])
    links.new(nodes['Vector Math.004'].outputs['Vector'], nodes['Vector Math.001'].inputs[1])
    links.new(nodes['Combine XYZ.002'].outputs['Vector'], nodes['Vector Math.001'].inputs[0])
    links.new(nodes['Vector Math.004'].outputs['Vector'], nodes['Vector Math.002'].inputs[1])
    links.new(nodes['Combine XYZ.003'].outputs['Vector'], nodes['Vector Math.002'].inputs[0])
    links.new(nodes['Vector Math.003'].outputs['Vector'], nodes['Vector Math.004'].inputs[0])
    links.new(nodes['Vector Math.003'].outputs['Vector'], nodes['Vector Math.004'].inputs[1])
    links.new(nodes['Vector Math'].outputs['Value'], nodes['Combine XYZ'].inputs['X'])
    links.new(nodes['Vector Math.001'].outputs['Value'], nodes['Combine XYZ'].inputs['Y'])
    links.new(nodes['Vector Math.002'].outputs['Value'], nodes['Combine XYZ'].inputs['Z'])
    links.new(nodes['Separate XYZ.001'].outputs['X'], nodes['Combine XYZ.001'].inputs['X'])
    links.new(nodes['Separate XYZ.002'].outputs['X'], nodes['Combine XYZ.001'].inputs['Y'])
    links.new(nodes['Separate XYZ.003'].outputs['X'], nodes['Combine XYZ.001'].inputs['Z'])
    links.new(nodes['Separate XYZ.001'].outputs['Y'], nodes['Combine XYZ.002'].inputs['X'])
    links.new(nodes['Separate XYZ.002'].outputs['Y'], nodes['Combine XYZ.002'].inputs['Y'])
    links.new(nodes['Separate XYZ.003'].outputs['Y'], nodes['Combine XYZ.002'].inputs['Z'])
    links.new(nodes['Separate XYZ.001'].outputs['Z'], nodes['Combine XYZ.003'].inputs['X'])
    links.new(nodes['Separate XYZ.002'].outputs['Z'], nodes['Combine XYZ.003'].inputs['Y'])
    links.new(nodes['Separate XYZ.003'].outputs['Z'], nodes['Combine XYZ.003'].inputs['Z'])
    links.new(nodes['Combine XYZ'].outputs['Vector'], nodes['Group Output'].inputs['Normal'])

    return group


@persistent
def custom_normal_load(scn):
    if bpy.ops.zpy.mats_custom_normals.poll():
        bpy.ops.zpy.mats_custom_normals(custom=True)


def register():
    load_post.append(custom_normal_load)


def unregister():
    load_post.remove(custom_normal_load)
