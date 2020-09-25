import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, IntProperty
from zpy import Is


data_path_iter = StringProperty(
    description="The data path relative to the context, must point to an iterable")

data_path_item = StringProperty(
    description="The data path from each iterable to the value (int or float)")


def operator_value_is_undo(value):
    if value in {None, Ellipsis}:
        return False

    # typical properties or objects
    id_data = getattr(value, "id_data", Ellipsis)

    if id_data is None:
        return False
    elif id_data is Ellipsis:
        # handle mathutils types
        id_data = getattr(getattr(value, "owner", None), "id_data", None)

        if id_data is None:
            return False

    # return True if its a non window ID type
    return (isinstance(id_data, bpy.types.ID) and
            (not isinstance(id_data, (bpy.types.WindowManager,
                                      bpy.types.Screen,
                                      bpy.types.Brush,
                                      ))))


def operator_value_undo_return(value):
    return {'FINISHED'} if operator_value_is_undo(value) else {'CANCELLED'}


class WM_SINGLE_OT_context_modal_mouse(bpy.types.Operator):
    bl_description = """Adjust arbitrary values with mouse input"""
    bl_idname = 'zpy.context_modal_mouse'
    bl_label = "Context Modal Mouse"
    bl_options = {'GRAB_CURSOR', 'BLOCKING', 'UNDO', 'INTERNAL'}

    data_path_iter: data_path_iter
    data_path_item: data_path_item
    header_text: StringProperty(
        name="Header Text",
        description="Text to display in header during scale",
    )

    input_scale: FloatProperty(
        description="Scale the mouse movement by this value before applying the delta",
        default=0.01,
    )
    invert: BoolProperty(
        description="Invert the mouse input",
        default=False,
    )
    initial_x: IntProperty(options={'HIDDEN'})

    def _values_store(self, context):
        data_path_iter = self.data_path_iter
        data_path_item = self.data_path_item

        self._values = values = {}

        iters = getattr(context, data_path_iter)
        if not Is.iterable(iters):
            iters = [iters]

        for item in iters:
            try:
                value_orig = eval("item." + data_path_item)
            except:
                continue

            # check this can be set, maybe this is library data.
            try:
                exec("item.%s = %s" % (data_path_item, value_orig))
            except:
                continue

            values[item] = value_orig

    def _values_delta(self, delta):
        delta *= self.input_scale
        if self.invert:
            delta = - delta

        data_path_item = self.data_path_item
        for item, value_orig in self._values.items():
            if type(value_orig) == int:
                exec("item.%s = int(%d)" % (data_path_item, round(value_orig + delta)))
            else:
                exec("item.%s = %f" % (data_path_item, value_orig + delta))

    def _values_restore(self):
        data_path_item = self.data_path_item
        for item, value_orig in self._values.items():
            exec("item.%s = %s" % (data_path_item, value_orig))

        self._values.clear()

    def _values_clear(self):
        self._values.clear()

    def invoke(self, context, event):
        self._values_store(context)

        if not self._values:
            self.report({'WARNING'}, "Nothing to operate on: %s[ ].%s" %
                        (self.data_path_iter, self.data_path_item))

            return {'CANCELLED'}
        else:
            self.initial_x = event.mouse_x

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        event_type = event.type

        if event_type == 'MOUSEMOVE':
            delta = event.mouse_x - self.initial_x
            self._values_delta(delta)
            header_text = self.header_text
            if header_text:
                if len(self._values) == 1:
                    (item, ) = self._values.keys()
                    header_text = header_text % eval("item.%s" % self.data_path_item)
                else:
                    header_text = (self.header_text % delta) + " (delta)"
                context.area.header_text_set(header_text)

        elif 'LEFTMOUSE' == event_type:
            item = next(iter(self._values.keys()))
            self._values_clear()
            context.area.header_text_set(None)
            return operator_value_undo_return(item)

        elif event_type in {'RIGHTMOUSE', 'ESC'}:
            self._values_restore()
            context.area.header_text_set(None)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
