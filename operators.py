import colorsys
from operator import itemgetter
from random import random

import bpy
import bpy_extras
import bmesh
from bpy.types import (
    Operator,
    Object,
    Context
)
from bmesh.types import BMesh

from .functions import (
    convert_to_plain_array,
    create_bmesh_color,
    get_bmesh_active_color_layer
)
from .constants import BLANK_ARRAY


#########################################
# OPERATORS
#########################################


class DefaultsOperator(Operator): # Mix-in class
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = ""


class COLORPLUS_OT_switch_to_paint_or_edit(DefaultsOperator):
    """Switch to vertex painting, this option automates some scene settings and links the active color with the brush color"""
    bl_idname = "color_plus.switch_to_paint_or_edit"

    def execute(self, context: Context):
        color_plus = context.scene.color_plus

        context.space_data.shading.type = 'SOLID'
        context.space_data.shading.color_type = 'VERTEX'

        # NOTE: Poor way to sync these values but is what it is
        if context.mode == 'PAINT_VERTEX':
            brush_color = bpy.data.brushes["Draw"].color
            color_plus.color_wheel = (
                brush_color[0], brush_color[1],
                brush_color[2], color_plus.color_wheel[3]
            )
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            bpy.data.brushes["Draw"].color = (
                color_plus.color_wheel[0],
                color_plus.color_wheel[1],
                color_plus.color_wheel[2]
            )
            bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        return {'FINISHED'}


class COLORPLUS_OT_edit_color(DefaultsOperator):
    """Edits the active vertex color set based on the selected operator"""
    bl_idname = "color_plus.edit_color"
    bl_label = "Paint Selection"

    edit_type: bpy.props.EnumProperty(
        items=(
            ('apply', "Apply", ""),
            ('apply_all', "Apply All", ""),
            ('clear', "Clear", ""),
            ('clear_all', "Clear All", "")
        ),
        options={'HIDDEN'}
    ) # type: ignore

    variation_value: bpy.props.StringProperty(options={'HIDDEN'})

    def change_color(self, component, layer, rgba_value) -> None:
        """Change a vert/loop components color attribute."""
        if self.edit_type in ('clear', 'clear_all'):
            component[layer] = BLANK_ARRAY
            return

        for idx, value in enumerate(rgba_value):
            if value is None:
                rgba_value[idx] = component[layer][idx]

        if self.variation_value == 'alpha_only':
            component[layer] = (
                component[layer][0], component[layer][1],
                component[layer][2], rgba_value[3]
            )
        elif self.variation_value == 'color_only':
            component[layer] = (
                rgba_value[0], rgba_value[1],
                rgba_value[2], component[layer][3]
            )
        else:
            component[layer] = rgba_value

    def change_color_hard(self, bm: BMesh, layer, rgba_value) -> None:
        """Change color using hard face-based interpolation."""
        # NOTE: if not using `_all` edit type restrict to selected only
        if self.edit_type in ('apply', 'clear'):
            faces = [face for face in bm.faces if face.select]
        else:
            faces = bm.faces
        for face in faces:
            for loop in face.loops:
                self.change_color(loop, layer, rgba_value)

    def change_color_smooth(self, bm: BMesh, layer, rgba_value) -> None:
        """Change color using smooth vertex-based interpolation."""
        # NOTE: if not using `_all` edit type restrict to selected only
        if self.edit_type in ('apply', 'clear'):
            verts = [vert for vert in bm.verts if vert.select]
        else:
            verts = bm.verts
        for vert in verts:
            for loop in vert.link_loops:
                self.change_color(loop, layer, rgba_value)

    def execute(self, context: Context):
        color_plus = context.scene.color_plus

        saved_context=context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        context.object.select_set(True)

        selected_mesh_objects = \
            [ob for ob in context.selectable_objects if ob.type == 'MESH']
        for ob in selected_mesh_objects:
            bm = bmesh.new()
            bm.from_mesh(ob.data)

            # Get the RGB value based on the property given
            rgba_value = BLANK_ARRAY
            if self.variation_value:
                try:
                    rgba_value = getattr(color_plus, self.variation_value)
                except AttributeError:
                    rgba_value = getattr(color_plus, 'color_wheel')
                if self.variation_value == 'value_var':
                    rgba_value = \
                        [rgba_value[0], rgba_value[1], rgba_value[2], None]
                elif self.variation_value == 'alpha_var':
                    rgba_value = [None, None, None, rgba_value[3]]

            layer = create_bmesh_color(bm, ob)
            if color_plus.interpolation_type == "hard":
                self.change_color_hard(bm, layer, rgba_value)
            else: # Smooth
                self.change_color_smooth(bm, layer, rgba_value)
            bm.to_mesh(ob.data)

        bpy.ops.object.mode_set(mode=saved_context)
        preferences = \
            context.preferences.addons[__package__].preferences
        if preferences.auto_palette_refresh:
            bpy.ops.color_plus.refresh_palette_outliner()
        return {'FINISHED'}


class COLORPLUS_OT_edit_color_keymap_placeholder(DefaultsOperator):
    bl_idname = "color_plus.edit_color_clear"
    bl_label = "Clear Selection"
    bl_options = {'INTERNAL'}

    def execute(self, context: Context):
        bpy.ops.color_plus.edit_color(edit_type='clear')
        return {'FINISHED'}


class COLORPLUS_OT_quick_color_switch(DefaultsOperator):
    """Switch between your main and alternate color"""
    bl_idname = "color_plus.quick_color_switch"

    def execute(self, context: Context):
        color_plus = context.scene.color_plus

        saved_color_tweak = color_plus.live_color_tweak
        color_plus.live_color_tweak = False

        saved_main_color = convert_to_plain_array(
            array_object=color_plus.color_wheel
        )
        saved_alt_color = convert_to_plain_array(
            array_object=color_plus.alt_color_wheel
        )

        color_plus.color_wheel = saved_alt_color
        color_plus.alt_color_wheel = saved_main_color

        color_plus.live_color_tweak = saved_color_tweak
        if color_plus.live_color_tweak:
            bpy.ops.color_plus.edit_color(
                edit_type='apply',
                variation_value='color_wheel'
            )
        return {'FINISHED'}


class COLORPLUS_OT_quick_interpolation_switch(DefaultsOperator):
    """Switch the shading interpolation between smooth and hard"""
    bl_idname = "color_plus.quick_interpolation_switch"
    bl_label = "Smooth/Hard Switch"

    def execute(self, context: Context):
        color_plus = context.scene.color_plus
        if color_plus.interpolation_type == 'smooth':
            color_plus.interpolation_type = 'hard'
        else:
            color_plus.interpolation_type = 'smooth'
        return {'FINISHED'}


class COLORPLUS_OT_get_active_color(DefaultsOperator):
    """Set the Active Color based on the actively selected vertex color on the mesh"""
    bl_idname = "color_plus.get_active_color"
    bl_label = "Color from Active Vertex"

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context: Context):
        ob = context.object
        saved_context=ob.mode

        bpy.ops.object.mode_set(mode='EDIT')

        if not ob.data.vertex_colors:
            context.scene.color_plus.color_wheel = (1, 1, 1, 1)
            return {'FINISHED'}

        bm = bmesh.from_edit_mesh(ob.data)

        try:
            active_selection = bm.select_history[-1]
        except IndexError:
            self.report({'ERROR'}, "There is no Active Vertex selected")
            return {'CANCELLED'}

        # TODO: Haven't actually tested what this is for, maybe instancing?
        if not isinstance(active_selection, bmesh.types.BMVert):
            self.report(
                {'ERROR'}, "Please select only one active vertex at a time"
            )
            return {'CANCELLED'}

        # Get active vertex color
        layer = get_bmesh_active_color_layer(bm, ob)
        for face in bm.faces:
            for loop in face.loops:
                # TODO Make a list of the vert colors in this
                # list, choose the first one that isn't pure white?
                if loop.vert.select and loop.vert == active_selection:
                    context.scene.color_plus.color_wheel = loop[layer]
                    break

        bpy.ops.object.mode_set(mode=saved_context)
        return {'FINISHED'}


class COLORPLUS_OT_vcolor_shading(DefaultsOperator):
    """Sets the current viewport shading to something more suitable for vertex painting (WARNING: This operation is destructive and won't save existing shading settings)"""
    bl_idname = "color_plus.vcolor_shading"
    bl_label = "Apply Attribute Shading"

    def execute(self, context: Context):
        context.space_data.shading.type = 'SOLID'
        context.space_data.shading.color_type = 'VERTEX'
        return {'FINISHED'}


class COLORPLUS_OT_refresh_palette_outliner(DefaultsOperator):
    """Manual refresh for the palette outliner of the Active Object as sometimes it doesn't update correctly on its own"""
    bl_idname = "color_plus.refresh_palette_outliner"
    bl_label = "Refresh Palette"

    saved_active_idx: bpy.props.IntProperty(default=-1)

    def get_bmesh_colors(self, bm: BMesh, layer) -> list:
        preferences = \
            bpy.context.preferences.addons[__package__].preferences
        color_list = []
        message_sent = False
        for face in bm.faces:
            if message_sent:
                break
            for loop in face.loops:
                if len(color_list) > preferences.max_outliner_items:
                    message_sent = True
                    self.report({'WARNING'}, f"Maximum amount of Palette Outliner vertex colors reached ({preferences.max_outliner_items})")
                    break

                converted_loop = \
                    convert_to_plain_array(array_object=loop[layer])

                if converted_loop not in color_list \
                and converted_loop != BLANK_ARRAY:
                    color_list.append(converted_loop)
        return color_list

    def sort_colors(self, colors: list) -> tuple[list, list]:
        # Convert to HSV, sort list by value
        colors_hsv = []
        for color in colors:
            colors_hsv.append([*colorsys.rgb_to_hsv(*color[:3]), color[3]])

        # Separate and sort
        hsv_sep = [color for color in colors_hsv if color[0] == 0]
        hsv_values_sorted = sorted(hsv_sep, key=itemgetter(2))
        hsv_hues = [color for color in colors_hsv if color not in hsv_sep]
        hsv_hues_sorted = sorted(hsv_hues, key=itemgetter(0))
        colors_hsv = hsv_values_sorted + hsv_hues_sorted

        # Convert back to RGB
        colors_rgb = []
        for color in colors_hsv:
            colors_rgb.append(
                [*colorsys.hsv_to_rgb(*color[:3]), color[3]]
            )
        return colors_hsv, colors_rgb

    def generate_palette(self, ob: Object, colors: list) -> None:
        for idx, color in enumerate(colors):
            item = ob.color_palette.add()
            item.id = len(ob.color_palette) - 1
            item.saved_color = color
            item.color = color

            if idx == self.saved_active_idx:
                item.id = self.saved_active_idx
            else:
                item.id = len(ob.color_palette) - 1

            if bpy.context.scene.color_plus.rgb_hsv_convert_options == 'rgb':
                item.name = \
                    f'({round(color[0] * 255)}, {round(color[1] * 255)}, {round(color[2] * 255)}, {round(color[3], 2)})'
            else:
                color_hsv = \
                    colorsys.rgb_to_hsv(color[0], color[1], color[2])
                item.name = \
                    f'({round(color_hsv[0], 2)}, {round(color_hsv[1], 2)}, {round(color_hsv[2], 2)}, {round(color[3], 2)})'

    def execute(self, context: Context):
        saved_context=context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')

        selected_mesh_objects = \
            [ob for ob in context.selectable_objects if ob.type == 'MESH']
        for ob in selected_mesh_objects:
            ob.color_palette.clear()

            bm = bmesh.from_edit_mesh(ob.data)
            layer = create_bmesh_color(bm, ob)

            # Preserve the original index color value
            if len(ob.color_palette):
                palette = ob.color_palette[ob.color_palette_active]
                saved_color = \
                    convert_to_plain_array(array_object=palette.color)

            colors = self.get_bmesh_colors(bm, layer)
            # TODO Unused sorting method, currently breaks the
            # outliner in odd ways that I cannot currently solve
            #colors = self.sort_colors(colors)

            self.generate_palette(ob, colors)

            # Reconfigure the active color palette
            # based on previously saved color info
            #if ob.color_palette_active != 0:
            #    ob.color_palette_active += -1

            if not 'saved_color' in locals():
                continue
            for color in ob.color_palette:
                converted_color = \
                    convert_to_plain_array(array_object=color.color)
                if converted_color == saved_color:
                    ob.color_palette_active = color.id
                    del saved_color
                    break
                del saved_color

        bpy.ops.object.mode_set(mode=saved_context)
        return {'FINISHED'}


class COLORPLUS_OT_change_outliner_color(DefaultsOperator):
    bl_idname = "color_plus.change_outliner_color"
    bl_options = {'INTERNAL'}

    saved_active_idx: bpy.props.IntProperty()

    def execute(self, context: Context):
        ob = context.object
        palette = ob.color_palette[self.saved_active_idx]
        saved_context=ob.mode

        bpy.ops.object.mode_set(mode='EDIT')

        palette_saved_color = \
            convert_to_plain_array(array_object=palette.saved_color)

        bm = bmesh.from_edit_mesh(ob.data)
        layer = get_bmesh_active_color_layer(bm, ob)
        for face in bm.faces:
            for loop in face.loops:
                converted_loop = \
                    convert_to_plain_array(array_object=loop[layer])
                if converted_loop == palette_saved_color:
                    loop[layer] = palette.color

        palette.name = f'({round(palette.color[0] * 255)}, {round(palette.color[1] * 255)}, {round(palette.color[2] * 255)}, {round(palette.color[3], 2)})'

        bmesh.update_edit_mesh(ob.data)

        bpy.ops.object.mode_set(mode=saved_context)
        return {'FINISHED'}


class COLORPLUS_OT_get_active_outliner_color(DefaultsOperator):
    """Apply the Outliner Color to the Active Color"""
    bl_idname = "color_plus.get_active_outliner_color"
    bl_label = "Set as Active Color"

    def execute(self, context: Context):
        ob = context.object
        context.scene.color_plus.color_wheel = \
            ob.color_palette[ob.color_palette_active]
        return {'FINISHED'}


class COLORPLUS_OT_apply_outliner_color(DefaultsOperator):
    """Apply the Outliner Color to the selected geometry"""
    bl_idname = "color_plus.apply_outliner_color"
    bl_label = "Apply Outliner Color"

    def execute(self, context: Context):
        # Set the temporary property
        ob = context.object
        context.scene.color_plus.overlay_color_placeholder = \
            ob.color_palette[ob.color_palette_active].color

        # TODO: This still uses selected_objects
        bpy.ops.color_plus.edit_color(
            edit_type='apply',
            variation_value='overlay_color_placeholder'
        )
        return {'FINISHED'}


class COLORPLUS_OT_select_outliner_color(DefaultsOperator):
    """Select vertices based on the Outliner Color (WARNING: This does not remove your existing selection)"""
    bl_idname = "color_plus.select_outliner_color"
    bl_label = "Select Geometry from Outliner Color"

    def execute(self, context: Context):
        ob = context.object
        saved_context=ob.mode

        bpy.ops.object.mode_set(mode='OBJECT')

        # Object mode BMesh correct mesh update
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        context.tool_settings.mesh_select_mode=(True, False, False)

        palette = ob.color_palette[ob.color_palette_active]
        converted_palette_loop = \
            convert_to_plain_array(array_object=palette.color)

        layer = get_bmesh_active_color_layer(bm, ob)
        for face in bm.faces:
            for loop in face.loops:
                converted_loop = \
                    convert_to_plain_array(array_object=loop[layer])

                if converted_loop == converted_palette_loop:
                    loop.vert.select_set(True)

        bm.to_mesh(ob.data)

        bpy.ops.object.mode_set(mode=saved_context)
        return {'FINISHED'}


class COLORPLUS_OT_delete_outliner_color(DefaultsOperator):
    """Remove the Outliner Color from the Palette Outliner and geometry"""
    bl_idname = "color_plus.delete_outliner_color"
    bl_label = "Delete Outliner Color"

    def execute(self, context: Context):
        ob = context.object
        saved_context=ob.mode
        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(ob.data)
        layer = get_bmesh_active_color_layer(bm, ob)

        palette = ob.color_palette[ob.color_palette_active]
        converted_palette_loop = \
            convert_to_plain_array(array_object=palette.color)

        for face in bm.faces:
            for loop in face.loops:
                converted_loop = convert_to_plain_array(array_object=loop[layer])

                if converted_loop == converted_palette_loop:
                    loop[layer] = BLANK_ARRAY

        bmesh.update_edit_mesh(ob.data)

        bpy.ops.object.mode_set(mode=saved_context)

        if context.preferences.addons[__package__].preferences.auto_palette_refresh:
            bpy.ops.color_plus.refresh_palette_outliner()
        return {'FINISHED'}


class COLORPLUS_OT_convert_to_vertex_group(DefaultsOperator):
    """Convert the Outliner Color to a single Vertex Group"""
    bl_idname = "color_plus.convert_to_vertex_group"
    bl_label = "Convert to Vertex Group"

    def execute(self, context: Context):
        ob = context.object
        saved_context=ob.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Object mode BMesh for vgroup add (only works in ob mode)
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        palette = ob.color_palette[ob.color_palette_active]
        converted_palette_loop = \
            convert_to_plain_array(array_object=palette.color)

        # Get vertices with the corresponding color value
        layer = get_bmesh_active_color_layer(bm, ob)
        vertex_list = []
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.index not in vertex_list:
                    converted_loop = \
                        convert_to_plain_array(array_object=loop[layer])

                    if converted_loop == converted_palette_loop:
                        vertex_list.append(loop.vert.index)

        converted_vgroup = ob.vertex_groups.new(name=palette.name)
        converted_vgroup.add(vertex_list, 1.0, 'ADD')

        bpy.ops.object.mode_set(mode=saved_context)
        return {'FINISHED'}


class COLORPLUS_OT_custom_color_apply(DefaultsOperator):
    """Apply the color to your current selection/Active Color"""
    bl_idname = "color_plus.custom_color_apply"

    custom_color_name: bpy.props.StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'EDIT_MESH' or context.mode != 'EDIT_MESH' and context.scene.color_plus.custom_palette_apply_options == 'apply_to_col'

    def execute(self, context: Context):
        color_plus = context.scene.color_plus
        if color_plus.custom_palette_apply_options == 'apply_to_sel':
            bpy.ops.color_plus.edit_color(edit_type='apply', variation_value=self.custom_color_name)
        else: # Apply to Active Color
            color_plus.color_wheel = getattr(color_plus, self.custom_color_name)

            if context.preferences.addons[__package__].preferences.auto_palette_refresh:
                bpy.ops.color_plus.refresh_palette_outliner()
        return {'FINISHED'}


class COLORPLUS_OT_apply_color_to_border(DefaultsOperator):
    """Apply a VColor to the border or bounds of your current selection"""
    bl_idname = "color_plus.apply_color_to_border"
    bl_label = "Apply to Selection Border"

    border_type: bpy.props.EnumProperty(
        items=(
            ('inner', "Inner", ""),
            ('outer', "Outer", "")
        )
    )

    @classmethod
    def poll(cls, context: Context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context: Context):
        color_plus = context.scene.color_plus
        saved_context=context.object.mode

        bpy.ops.object.mode_set(mode='OBJECT')
        context.object.select_set(True)

        selected_mesh_objects = \
            [ob for ob in context.selectable_objects if ob.type == 'MESH']
        for ob in selected_mesh_objects:
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            layer = create_bmesh_color(bm, ob)

            # Get border vertices & linked faces
            border_vertices = set([])
            linked_faces = []

            edges = [edge for edge in bm.edges if edge.select]
            for edge in edges:
                if edge.is_boundary \
                or edge.link_faces[0].select != edge.link_faces[1].select:
                    for vert in edge.verts:
                        if vert.index not in border_vertices:
                            border_vertices.add(vert.index)
                    linked_faces.extend(list(edge.link_faces))

            # Search linked faces for loops on
            # the correct sides of the vertices
            if self.border_type == 'inner':
                for face in linked_faces:
                    if not face.select:
                        continue
                    for loop in face.loops:
                        if loop.vert.index in border_vertices:
                            loop[layer] = color_plus.color_wheel
                bm.to_mesh(ob.data)
                continue
            for face in linked_faces: # NOTE: Outer
                if face.select:
                    continue
                for loop in face.loops:
                    if loop.vert.index in border_vertices:
                        loop[layer] = color_plus.color_wheel
            bm.to_mesh(ob.data)

        bpy.ops.object.mode_set(mode=saved_context)
        if context.preferences.addons[__package__].preferences.auto_palette_refresh:
            bpy.ops.color_plus.refresh_palette_outliner()
        return {'FINISHED'}


class COLORPLUS_OT_dirty_vertex_color(DefaultsOperator):
    """Generate dirty vertex color"""
    bl_idname = "color_plus.dirty_vertex_color"
    bl_label = "Generate VColor"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    blur_strength: bpy.props.FloatProperty(default=1.0, name='Blur Strength')
    blur_iterations: bpy.props.IntProperty(default=1, name='Blur Iterations')
    clean_angle: bpy.props.FloatProperty(default=3.14159, name='Clean Angle', subtype='ANGLE')
    dirt_angle: bpy.props.FloatProperty(default=0.0, name='Dirt Angle')
    dirt_only: bpy.props.BoolProperty(default=False, name='Dirt Only')
    normalize: bpy.props.BoolProperty(default=True, name='Normalize')
    selection_only: bpy.props.BoolProperty(default=False, name='Use Selection')

    def execute(self, context: Context):
        if not bpy.ops.paint.vertex_paint_toggle.poll():
            self.report(
                {'ERROR'}, "Something went wrong, could not run operator"
            )
            return {'CANCELLED'}

        saved_context=context.mode

        context.object.data.use_paint_mask = self.selection_only

        if context.mode != 'PAINT_VERTEX':
            bpy.ops.paint.vertex_paint_toggle()

        bpy.ops.paint.vertex_color_dirt(
            blur_strength=self.blur_strength,
            blur_iterations=self.blur_iterations,
            clean_angle=self.clean_angle,
            dirt_angle=self.dirt_angle,
            dirt_only=self.dirt_only,
            normalize=self.normalize
        )

        if saved_context != 'PAINT_VERTEX':
            bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class COLORPLUS_OT_generate_vcolor(DefaultsOperator):
    """Generate a VColor mask based on the settings below"""
    bl_idname = "color_plus.generate_vcolor"
    bl_label = "Generate Vertex Color"

    def execute(self, context: Context):
        color_plus = context.scene.color_plus
        saved_context=context.object.mode

        bpy.ops.object.mode_set(mode='OBJECT')
        context.object.select_set(True)

        no_uv_obs = []
        selected_mesh_objects = \
            [ob for ob in context.selectable_objects if ob.type == 'MESH']
        for ob in selected_mesh_objects:
            if color_plus.generate in ('per_uv_shell', 'per_uv_border'):
                try:
                    uv_islands = \
                        bpy_extras.mesh_utils.mesh_linked_uv_islands(ob.data)
                except AttributeError:
                    no_uv_obs.append(ob.name)
                    continue

            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bm.faces.ensure_lookup_table()
            layer = create_bmesh_color(bm, ob)

            if color_plus.generate == 'per_uv_shell':
                for island_idxs in uv_islands:
                    random_color = [random(), random(), random(), 1]

                    for face_idx in island_idxs:
                        face = bm.faces[face_idx]

                        for loop in face.loops:
                            loop[layer] = random_color

            elif color_plus.generate == 'per_uv_border':
                for island_idxs in uv_islands:
                    if color_plus.generate_per_uv_border == 'random_col':
                        random_color = [random(), random(), random(), 1]

                    # Get border vertices & linked faces
                    border_vertices = set([])
                    linked_faces = set([])
                    for edge in bm.edges:
                        if edge.is_boundary \
                        or (edge.link_faces[0].index in island_idxs \
                        and edge.link_faces[1].index not in island_idxs) \
                        or (edge.link_faces[0].index not in island_idxs \
                        and edge.link_faces[1].index in island_idxs):
                            for vert in edge.verts:
                                if vert.index in border_vertices:
                                    continue
                                border_vertices.add(vert.index)

                        for vert in edge.verts:
                            if vert.index not in border_vertices:
                                continue
                            for face in edge.link_faces:
                                if face in linked_faces:
                                    continue
                                linked_faces.add(face)

                    # Assign a color to interior loops of linked faces
                    for face in linked_faces:
                        if face.index not in island_idxs:
                            continue
                        for loop in face.loops:
                            if loop.vert.index not in border_vertices:
                                continue
                            if color_plus.generate_per_uv_border == 'random_col':
                                loop[layer] = random_color
                            else: # Apply active color
                                loop[layer] = color_plus.color_wheel

            elif color_plus.generate == 'per_face':
                for face in bm.faces:
                    random_color = [random(), random(), random(), 1]
                    for loop in face.loops:
                        loop[layer] = random_color

            elif color_plus.generate == 'per_vertex':
                for vert in bm.verts:
                    random_color = [random(), random(), random(), 1]
                    for loop in vert.link_loops:
                        loop[layer] = random_color

            elif color_plus.generate == 'per_point':
                for face in bm.faces:
                    for loop in face.loops:
                        random_color = [random(), random(), random(), 1]
                        loop[layer] = random_color
            bm.to_mesh(ob.data)

        if color_plus.generate in ('per_uv_shell', 'per_uv_border') \
        and no_uv_obs:
            self.report({'INFO'}, f"UVs not found for: {no_uv_obs}")

        bpy.ops.object.mode_set(mode=saved_context)

        preferences = \
            context.preferences.addons[__package__].preferences
        if preferences.auto_palette_refresh:
            bpy.ops.color_plus.refresh_palette_outliner()
        return {'FINISHED'}


#######################################
# REGISTRATION
#######################################


classes = (
    COLORPLUS_OT_switch_to_paint_or_edit,
    COLORPLUS_OT_edit_color,
    COLORPLUS_OT_edit_color_keymap_placeholder,
    COLORPLUS_OT_quick_color_switch,
    COLORPLUS_OT_quick_interpolation_switch,
    COLORPLUS_OT_get_active_color,
    COLORPLUS_OT_vcolor_shading,
    COLORPLUS_OT_refresh_palette_outliner,
    COLORPLUS_OT_change_outliner_color,
    COLORPLUS_OT_get_active_outliner_color,
    COLORPLUS_OT_apply_outliner_color,
    COLORPLUS_OT_select_outliner_color,
    COLORPLUS_OT_delete_outliner_color,
    COLORPLUS_OT_convert_to_vertex_group,
    COLORPLUS_OT_custom_color_apply,
    COLORPLUS_OT_apply_color_to_border,
    COLORPLUS_OT_dirty_vertex_color,
    COLORPLUS_OT_generate_vcolor
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
