
import bpy, bmesh, colorsys, bpy_extras
from bpy.types import Operator
from random import random
#from operator import itemgetter


################################################################################################################
# FUNCTIONS & OPERATORS
################################################################################################################


class OpInfo: # Mix-in class
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = ""


def convert_to_plain_array(array_object) -> list:
    '''Convert custom datatypes to plain 4-size arrays'''
    converted_array = [array_object[0], array_object[1], array_object[2], array_object[3]]
    return converted_array


def find_or_create_vcolor_set(bm, active_ob: bpy.types.Object) -> bmesh.types.BMLayerItem:
    '''Get VColor Set/Layer or generate one if it doesn't already exist'''
    if not active_ob.data.vertex_colors:
        color_layer = bm.loops.layers.color.new("Col")

        layer = bm.loops.layers.color[color_layer.name]
    else:
        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]
    return layer


class VCOLORPLUS_OT_switch_to_paint_or_edit(OpInfo, Operator):
    """Switch to vertex painting, this option automates some scene settings and links the active color with the brush color"""
    bl_idname = "vcolor_plus.switch_to_paint_or_edit"

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

        context.space_data.shading.type = 'SOLID'
        context.space_data.shading.color_type = 'VERTEX'

        if context.mode == 'PAINT_VERTEX':
            brush_color = bpy.data.brushes["Draw"].color # Poor way to sync these values but is what it is

            vcolor_plus.color_wheel = (brush_color[0], brush_color[1], brush_color[2], vcolor_plus.color_wheel[3])

            bpy.ops.object.mode_set(mode = 'EDIT')
        else:
            bpy.data.brushes["Draw"].color = (vcolor_plus.color_wheel[0], vcolor_plus.color_wheel[1], vcolor_plus.color_wheel[2])

            bpy.ops.object.mode_set(mode = 'VERTEX_PAINT')
        return {'FINISHED'}


class VCOLORPLUS_OT_edit_color(OpInfo, Operator):
    """Edits the active vertex color set based on the selected operator"""
    bl_idname = "vcolor_plus.edit_color"
    bl_label = "Fill Selection"

    edit_type: bpy.props.EnumProperty(
        items=(
            ('apply', "Apply", ""),
            ('apply_all', "Apply All", ""),
            ('clear', "Clear", ""),
            ('clear_all', "Clear All", "")
        ),
        options={'HIDDEN'}
    )

    variation_value: bpy.props.StringProperty(options={'HIDDEN'})
    
    def change_vcolor(self, layer, loop, rgb_value):
        if self.edit_type == 'apply' and loop.vert.select or self.edit_type == 'apply_all':
            if self.variation_value == 'alpha_only':
                loop[layer] = (loop[layer][0], loop[layer][1], loop[layer][2], rgb_value[3])
            elif self.variation_value == 'color_only':
                loop[layer] = (rgb_value[0], rgb_value[1], rgb_value[2], loop[layer][3])
            else:
                loop[layer] = rgb_value

        elif self.edit_type == 'clear' and loop.vert.select or self.edit_type == 'clear_all':
            loop[layer] = [1, 1, 1, 1]

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus
        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        context.object.select_set(True)

        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            bm = bmesh.new()
            bm.from_mesh(ob.data)

            # Get the RGB value based on the property given
            rgb_value = [1, 1, 1, 1]
            if self.variation_value:
                try:
                    rgb_value = getattr(vcolor_plus, self.variation_value)
                except AttributeError:
                    rgb_value = getattr(vcolor_plus, 'color_wheel')

                if self.variation_value == 'value_var':
                    rgb_value = (rgb_value[0], rgb_value[1], rgb_value[2], vcolor_plus.color_wheel[3])
                elif self.variation_value == 'alpha_var':
                    rgb_value = (vcolor_plus.color_wheel[0], vcolor_plus.color_wheel[1], vcolor_plus.color_wheel[2], rgb_value[3])

            layer = find_or_create_vcolor_set(bm, ob)

            # Get application type (smooth/hard) and then apply to the corresponding geometry
            if vcolor_plus.interpolation_type == 'hard':
                for face in bm.faces:
                    if face.select or self.edit_type == 'clear_all':
                        for loop in face.loops:
                            self.change_vcolor(layer=layer, loop=loop, rgb_value=rgb_value)
            else: # Smooth
                for face in bm.faces:
                    for loop in face.loops:
                        self.change_vcolor(layer=layer, loop=loop, rgb_value=rgb_value)

            bm.to_mesh(ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)

        if context.preferences.addons[__package__].preferences.auto_palette_refresh:
            bpy.ops.vcolor_plus.refresh_palette_outliner()
        return {'FINISHED'}


class VCOLORPLUS_OT_edit_color_keymap_placeholder(OpInfo, Operator):
    bl_idname = "vcolor_plus.edit_color_clear"
    bl_label = "Clear Selection"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.vcolor_plus.edit_color(edit_type='clear')
        return {'FINISHED'}


class VCOLORPLUS_OT_quick_color_switch(OpInfo, Operator):
    """Switch between your main and alternate color"""
    bl_idname = "vcolor_plus.quick_color_switch"

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

        saved_color_tweak = vcolor_plus.live_color_tweak
        vcolor_plus.live_color_tweak = False

        saved_main_color = convert_to_plain_array(array_object=vcolor_plus.color_wheel)
        saved_alt_color = convert_to_plain_array(array_object=vcolor_plus.alt_color_wheel)

        vcolor_plus.color_wheel = saved_alt_color
        vcolor_plus.alt_color_wheel = saved_main_color

        vcolor_plus.live_color_tweak = saved_color_tweak

        if vcolor_plus.live_color_tweak:
            bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value='color_wheel')
        return {'FINISHED'}


class VCOLORPLUS_OT_quick_interpolation_switch(OpInfo, Operator):
    """Switch the shading interpolation between smooth and hard"""
    bl_idname = "vcolor_plus.quick_interpolation_switch"
    bl_label = "Smooth/Hard Switch"

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

        if vcolor_plus.interpolation_type == 'smooth':
            vcolor_plus.interpolation_type = 'hard'
        else:
            vcolor_plus.interpolation_type = 'smooth'
        return {'FINISHED'}


class VCOLORPLUS_OT_get_active_color(OpInfo, Operator):
    """Set the Active Color based on the actively selected vertex color on the mesh"""
    bl_idname = "vcolor_plus.get_active_color"
    bl_label = "Color from Active Vertex"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        active_ob = context.object
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'EDIT')

        if not active_ob.data.vertex_colors:
            context.scene.vcolor_plus.color_wheel = (1, 1, 1, 1)
            return {'FINISHED'}

        bm = bmesh.from_edit_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        # Search select_history for the active vertex
        try:
            active_selection = bm.select_history[-1]
        except IndexError:
            self.report({'ERROR'}, "There is no Active Vertex selected")
            return{'CANCELLED'}

        # Haven't actually tested what this is for, maybe instancing?
        if not isinstance(active_selection, bmesh.types.BMVert):
            self.report({'ERROR'}, "There is more than one Active Vertex selected, please select only one active vertex")
            return{'CANCELLED'}

        # Get active vertex's color
        for face in bm.faces:
            for loop in face.loops:
                # TODO Make a list of the vert colors in this list, choose the first one that isn't pure white?

                if loop.vert.select and loop.vert == active_selection:
                    context.scene.vcolor_plus.color_wheel = loop[layer]

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_vcolor_shading(OpInfo, Operator):
    """Sets the current viewport shading to something more suitable for vertex painting (WARNING: This operation is destructive and won't save existing shading settings)"""
    bl_idname = "vcolor_plus.vcolor_shading"
    bl_label = "Apply VColor Shading"

    def execute(self, context):
        context.space_data.shading.type = 'SOLID'
        context.space_data.shading.color_type = 'VERTEX'
        return {'FINISHED'}


class VCOLORPLUS_OT_refresh_palette_outliner(OpInfo, Operator):
    """Manual refresh for the palette outliner of the Active Object as sometimes it doesn't update correctly on its own"""
    bl_idname = "vcolor_plus.refresh_palette_outliner"
    bl_label = "Refresh Palette"

    saved_id: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        saved_context_mode = context.object.mode
        vcolor_prefs = context.preferences.addons[__package__].preferences

        bpy.ops.object.mode_set(mode = 'EDIT')

        for ob in context.selected_objects:
            if ob.type == 'MESH':
                
                # Clear palette outliner list
                ob.vcolor_plus_palette_coll.clear()

                bm = bmesh.from_edit_mesh(ob.data)

                layer = find_or_create_vcolor_set(bm, ob)

                # Preserve the original index color value
                if len(ob.vcolor_plus_palette_coll):
                    saved_color = convert_to_plain_array(array_object=ob.vcolor_plus_palette_coll[ob.vcolor_plus_custom_index].color)

                vcolor_list = []

                message_sent = False

                for face in bm.faces:
                    if message_sent:
                        break

                    for loop in face.loops:
                        if len(vcolor_list) == vcolor_prefs.max_outliner_items:
                            message_sent = True
                            self.report({'WARNING'}, f"Maximum amount of Palette Outliner vertex colors reached ({vcolor_prefs.max_outliner_items})")
                            break

                        reconstructed_loop = convert_to_plain_array(array_object=loop[layer])

                        if reconstructed_loop not in vcolor_list and reconstructed_loop != [1, 1, 1, 1]:
                            vcolor_list.append(reconstructed_loop)

                # TODO Unused sorting method, currently breaks the outliner in odd ways that I cannot solve

                # Convert to HSV, sort list by value
                #vcolor_list_hsv = []
                #for vcolor in vcolor_list:
                #    vcolor_list_hsv.append([*colorsys.rgb_to_hsv(*vcolor[:3]), vcolor[3]])
#
                ## Separate the values to sort them properly
                #vcolor_list_hsv_values = [vcolor for vcolor in vcolor_list_hsv if vcolor[0] == 0]
                #vcolor_list_hsv_values_sorted = sorted(vcolor_list_hsv_values, key=itemgetter(2))
#
                #vcolor_list_hsv_hues = [vcolor for vcolor in vcolor_list_hsv if vcolor not in vcolor_list_hsv_values]
                #vcolor_list_hsv_hues_sorted = sorted(vcolor_list_hsv_hues, key=itemgetter(0))
#
                ## Merge the 2 lists
                #vcolor_list_hsv_sorted = vcolor_list_hsv_values_sorted + vcolor_list_hsv_hues_sorted
#
                ## Convert back to RGB
                #vcolor_list_rgb = []
                #for vcolor in vcolor_list_hsv_sorted:
                #    vcolor_list_rgb.append([*colorsys.hsv_to_rgb(*vcolor[:3]), vcolor[3]])

                # Generate palette outliner properties
                for index, vcolor in enumerate(vcolor_list):
                    item = ob.vcolor_plus_palette_coll.add()
                    item.id = len(ob.vcolor_plus_palette_coll) - 1
                    item.saved_color = vcolor
                    item.color = vcolor

                    if index == self.saved_id:
                        item.id = self.saved_id
                    else:
                        item.id = len(ob.vcolor_plus_palette_coll) - 1

                    if context.scene.vcolor_plus.rgb_hsv_convert_options == 'rgb':
                        item.name = f'({round(vcolor[0] * 255)}, {round(vcolor[1] * 255)}, {round(vcolor[2] * 255)}, {round(vcolor[3], 2)})'
                    else:
                        vcolor_hsv = colorsys.rgb_to_hsv(vcolor[0], vcolor[1], vcolor[2])

                        item.name = f'({round(vcolor_hsv[0], 2)}, {round(vcolor_hsv[1], 2)}, {round(vcolor_hsv[2], 2)}, {round(vcolor[3], 2)})'

                # Reconfigure the active color palette based on previously saved color info
                #if ob.vcolor_plus_custom_index != 0:
                #    ob.vcolor_plus_custom_index += -1

                if 'saved_color' in locals():
                    for vcolor in ob.vcolor_plus_palette_coll:
                        converted_vcolor = convert_to_plain_array(array_object=vcolor.color)

                        if converted_vcolor == saved_color:
                            ob.vcolor_plus_custom_index = vcolor.id
                            break

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_change_outliner_color(OpInfo, Operator):
    bl_idname = "vcolor_plus.change_outliner_color"
    bl_options = {'INTERNAL'}

    saved_id: bpy.props.IntProperty()

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[self.saved_id]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'EDIT')

        bm = bmesh.from_edit_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        palette_saved_color = convert_to_plain_array(array_object=active_palette.saved_color)

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = convert_to_plain_array(array_object=loop[layer])

                if reconstructed_loop == palette_saved_color:
                    loop[layer] = active_palette.color

        active_palette.name = f'({round(active_palette.color[0] * 255)}, {round(active_palette.color[1] * 255)}, {round(active_palette.color[2] * 255)}, {round(active_palette.color[3], 2)})'

        bmesh.update_edit_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_get_active_outliner_color(OpInfo, Operator):
    """Apply the Outliner Color to the Active Color"""
    bl_idname = "vcolor_plus.get_active_outliner_color"
    bl_label = "Set as Active Color"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color

        context.scene.vcolor_plus.color_wheel = active_palette
        return {'FINISHED'}


class VCOLORPLUS_OT_apply_outliner_color(OpInfo, Operator):
    """Apply the Outliner Color to the selected geometry"""
    bl_idname = "vcolor_plus.apply_outliner_color"
    bl_label = "Apply Outliner Color"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color

        # Set the temporary property
        context.scene.vcolor_plus.overlay_color_placeholder = active_palette

        bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value='overlay_color_placeholder') # TODO This still uses selected_objects
        return {'FINISHED'}


class VCOLORPLUS_OT_select_outliner_color(OpInfo, Operator):
    """Select vertices based on the Outliner Color (WARNING: This does not remove your existing selection)"""
    bl_idname = "vcolor_plus.select_outliner_color"
    bl_label = "Select Geometry from Outliner Color"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Object mode BMesh correct mesh update
        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]
        
        context.tool_settings.mesh_select_mode = (True, False, False)

        reconstructed_palette_loop = convert_to_plain_array(array_object=active_palette.color)

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = convert_to_plain_array(array_object=loop[layer])

                if reconstructed_loop == reconstructed_palette_loop:
                    loop.vert.select_set(True)

        bm.to_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_delete_outliner_color(OpInfo, Operator):
    """Remove the Outliner Color from the Palette Outliner and geometry"""
    bl_idname = "vcolor_plus.delete_outliner_color"
    bl_label = "Delete Outliner Color"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'EDIT')

        bm = bmesh.from_edit_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        reconstructed_palette_loop = convert_to_plain_array(array_object=active_palette.color)

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = convert_to_plain_array(array_object=loop[layer])

                if reconstructed_loop == reconstructed_palette_loop:
                    loop[layer] = [1, 1, 1, 1]

        bmesh.update_edit_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)

        if context.preferences.addons[__package__].preferences.auto_palette_refresh:
            bpy.ops.vcolor_plus.refresh_palette_outliner()
        return {'FINISHED'}


class VCOLORPLUS_OT_convert_to_vgroup(OpInfo, Operator):
    """Convert the Outliner Color to a single Vertex Group"""
    bl_idname = "vcolor_plus.convert_to_vgroup"
    bl_label = "Convert to Vertex Group"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Object mode BMesh for vgroup add (only works in ob mode)
        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        vertex_list = []

        reconstructed_palette_loop = convert_to_plain_array(array_object=active_palette.color)

        # Get vertices with the corresponding color value
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.index not in vertex_list:
                    reconstructed_loop = convert_to_plain_array(array_object=loop[layer])

                    if reconstructed_loop == reconstructed_palette_loop:
                        vertex_list.append(loop.vert.index)

        converted_vgroup = active_ob.vertex_groups.new(name=active_palette.name)
        converted_vgroup.add(vertex_list, 1.0, 'ADD')

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_custom_color_apply(OpInfo, Operator):
    """Apply the color to your current selection/Active Color"""
    bl_idname = "vcolor_plus.custom_color_apply"

    custom_color_name: bpy.props.StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' or context.mode != 'EDIT_MESH' and context.scene.vcolor_plus.custom_palette_apply_options == 'apply_to_col'

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

        if vcolor_plus.custom_palette_apply_options == 'apply_to_sel':
            bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value=self.custom_color_name)
        else: # Apply to Active Color
            vcolor_plus.color_wheel = getattr(vcolor_plus, self.custom_color_name)

            if context.preferences.addons[__package__].preferences.auto_palette_refresh:
                bpy.ops.vcolor_plus.refresh_palette_outliner()
        return {'FINISHED'}


class VCOLORPLUS_OT_apply_color_to_border(OpInfo, Operator):
    """Apply a VColor to the border or bounds of your current selection"""
    bl_idname = "vcolor_plus.apply_color_to_border"
    bl_label = "Apply to Selection Border"

    border_type: bpy.props.EnumProperty(
        items=(
            ('inner', "Inner", ""),
            ('outer', "Outer", "")
        )
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        context.object.select_set(True)

        for ob in context.selected_objects:
            if ob.type == 'MESH':
                bm = bmesh.new()
                bm.from_mesh(ob.data)

                layer = find_or_create_vcolor_set(bm, ob)

                # Get border vertices & linked faces
                border_vertices = set([])
                linked_faces = []

                for edge in bm.edges:
                    if edge.select:
                        if edge.is_boundary or edge.link_faces[0].select != edge.link_faces[1].select:
                            for vert in edge.verts:
                                if vert.index not in border_vertices:
                                    border_vertices.add(vert.index)

                            linked_faces.extend(list(edge.link_faces))

                # Search linked faces for loops on the correct sides of the vertices
                if self.border_type == 'inner':
                    for face in linked_faces:
                        if face.select:
                            for loop in face.loops:
                                if loop.vert.index in border_vertices:
                                    loop[layer] = context.scene.vcolor_plus.color_wheel
                else:
                    for face in linked_faces:
                        if not face.select:
                            for loop in face.loops:
                                if loop.vert.index in border_vertices:
                                    loop[layer] = context.scene.vcolor_plus.color_wheel

                bm.to_mesh(ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)

        if context.preferences.addons[__package__].preferences.auto_palette_refresh:
            bpy.ops.vcolor_plus.refresh_palette_outliner()
        return {'FINISHED'}


class VCOLORPLUS_OT_dirty_vertex_color(OpInfo, Operator):
    """Generate dirty vertex color"""
    bl_idname = "vcolor_plus.dirty_vertex_color"
    bl_label = "Generate VColor"
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    blur_strength : bpy.props.FloatProperty(default=1.0, name='Blur Strength')
    blur_iterations : bpy.props.IntProperty(default=1, name='Blur Iterations')
    clean_angle : bpy.props.FloatProperty(default=3.14159, name='Clean Angle', subtype='ANGLE')
    dirt_angle : bpy.props.FloatProperty(default=0.0, name='Dirt Angle')
    dirt_only : bpy.props.BoolProperty(default=False, name='Dirt Only')
    normalize : bpy.props.BoolProperty(default=True, name='Normalize')
    selection_only : bpy.props.BoolProperty(default=False, name='Use Selection')

    def execute(self, context):
        if not bpy.ops.paint.vertex_paint_toggle.poll():
            self.report({'ERROR'}, "Something went wrong, could not run operator")
            return {'CANCELLED'}

        saved_context_mode = context.mode

        context.object.data.use_paint_mask = True if self.selection_only else False 

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

        if saved_context_mode != 'PAINT_VERTEX':
            bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class VCOLORPLUS_OT_generate_vcolor(OpInfo, Operator):
    """Generate a VColor mask based on the settings below"""
    bl_idname = "vcolor_plus.generate_vcolor"
    bl_label = "Generate VColor"

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus
        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        no_uv_obs = []

        context.object.select_set(True)

        for ob in context.selected_objects:
            if ob.type == 'MESH':
                if vcolor_plus.generation_type in ('per_uv_shell', 'per_uv_border'):
                    try:
                        uv_islands = bpy_extras.mesh_utils.mesh_linked_uv_islands(ob.data)
                    except AttributeError:
                        no_uv_obs.append(ob.name)
                        continue

                bm = bmesh.new()
                bm.from_mesh(ob.data)
                bm.faces.ensure_lookup_table()

                layer = find_or_create_vcolor_set(bm, ob)

                if vcolor_plus.generation_type == 'per_uv_shell':
                    for island_idxs in uv_islands:
                        random_color = [random(), random(), random(), 1]

                        for face_idx in island_idxs:
                            face = bm.faces[face_idx]

                            for loop in face.loops:
                                loop[layer] = random_color

                elif vcolor_plus.generation_type == 'per_uv_border':
                    for island_idxs in uv_islands:
                        if vcolor_plus.generation_per_uv_border_options == 'random_col':
                            random_color = [random(), random(), random(), 1]
                            
                        # Get border vertices & linked faces
                        border_vertices = set([]) # Set is generally faster than list if you don't need it to be ordered
                        linked_faces = set([])

                        for edge in bm.edges:
                            if (
                                edge.is_boundary
                                or (edge.link_faces[0].index in island_idxs and edge.link_faces[1].index not in island_idxs)
                                or (edge.link_faces[0].index not in island_idxs and edge.link_faces[1].index in island_idxs)
                            ):
                                for vert in edge.verts:
                                    if vert.index not in border_vertices:
                                        border_vertices.add(vert.index)

                            for vert in edge.verts:
                                if vert.index in border_vertices:
                                    for face in edge.link_faces:
                                        if face not in linked_faces:
                                            linked_faces.add(face)

                        # Assign a color to interior loops of linked faces
                        for face in linked_faces:
                            if face.index in island_idxs:
                                for loop in face.loops:
                                    if loop.vert.index in border_vertices:
                                        if vcolor_plus.generation_per_uv_border_options == 'random_col':
                                            loop[layer] = random_color
                                        else: # Apply active color
                                            loop[layer] = context.scene.vcolor_plus.color_wheel

                elif vcolor_plus.generation_type == 'per_face':
                    for face in bm.faces:
                        random_color = [random(), random(), random(), 1]

                        for loop in face.loops:
                            loop[layer] = random_color

                elif vcolor_plus.generation_type == 'per_vertex':
                    for vert in bm.verts:
                        random_color = [random(), random(), random(), 1]

                        for loop in vert.link_loops:
                            loop[layer] = random_color

                elif vcolor_plus.generation_type == 'per_point':
                    for face in bm.faces:
                        for loop in face.loops:
                            random_color = [random(), random(), random(), 1]

                            loop[layer] = random_color

                bm.to_mesh(ob.data)

        if len(no_uv_obs) and vcolor_plus.generation_type in ('per_uv_shell', 'per_uv_border'):
            self.report({'INFO'}, f"UVs not found for: {no_uv_obs}")

        bpy.ops.object.mode_set(mode = saved_context_mode)

        if context.preferences.addons[__package__].preferences.auto_palette_refresh:
            bpy.ops.vcolor_plus.refresh_palette_outliner()
        return {'FINISHED'}


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_OT_switch_to_paint_or_edit,
    VCOLORPLUS_OT_edit_color,
    VCOLORPLUS_OT_edit_color_keymap_placeholder,
    VCOLORPLUS_OT_quick_color_switch,
    VCOLORPLUS_OT_quick_interpolation_switch,
    VCOLORPLUS_OT_get_active_color,
    VCOLORPLUS_OT_vcolor_shading,
    VCOLORPLUS_OT_refresh_palette_outliner,
    VCOLORPLUS_OT_change_outliner_color,
    VCOLORPLUS_OT_get_active_outliner_color,
    VCOLORPLUS_OT_apply_outliner_color,
    VCOLORPLUS_OT_select_outliner_color,
    VCOLORPLUS_OT_delete_outliner_color,
    VCOLORPLUS_OT_convert_to_vgroup,
    VCOLORPLUS_OT_custom_color_apply,
    VCOLORPLUS_OT_apply_color_to_border,
    VCOLORPLUS_OT_dirty_vertex_color,
    VCOLORPLUS_OT_generate_vcolor
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
