
import bpy, bmesh, colorsys
from bpy.props import IntProperty
from bpy.types import Operator


################################################################################################################
# FUNCTIONS & OPERATORS
################################################################################################################


class OpInfo: # Mix-in class
    bl_options = {'REGISTER', 'UNDO'}


class VCOLORPLUS_OT_vcolor_shading(OpInfo, Operator):
    """Saves current shading settings and sets up optimal vertex color shading"""
    bl_idname = "vcolor_plus.vcolor_shading_toggle"
    bl_label = "VColor Shading Mode"

    def execute(self, context):
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

    variation_value: bpy.props.StringProperty(default='0', options={'HIDDEN'})

    def change_vcolor(self, context, layer, loop, rgb_value):
        if self.edit_type == 'apply' and loop.vert.select:
            loop[layer] = rgb_value

        elif self.edit_type == 'apply_all':
            loop[layer] = rgb_value

        elif self.edit_type == 'clear' and loop.vert.select:
            loop[layer] = [1,1,1,1]

        elif self.edit_type == 'clear_all':
            loop[layer] = [1,1,1,1]

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus
        active_ob = context.object
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        if self.variation_value == 'p1':
            rgb_value = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color
        elif self.variation_value == '.2':
            rgb_value = (vcolor_plus.color_var_1[0], vcolor_plus.color_var_1[1], vcolor_plus.color_var_1[2], vcolor_plus.color_wheel[3])
        elif self.variation_value == '.4':
            rgb_value = (vcolor_plus.color_var_2[0], vcolor_plus.color_var_2[1], vcolor_plus.color_var_2[2], vcolor_plus.color_wheel[3])
        elif self.variation_value == '.6':
            rgb_value = (vcolor_plus.color_var_3[0], vcolor_plus.color_var_3[1], vcolor_plus.color_var_3[2], vcolor_plus.color_wheel[3])
        elif self.variation_value == '.8':
            rgb_value = (vcolor_plus.color_var_4[0], vcolor_plus.color_var_4[1], vcolor_plus.color_var_4[2], vcolor_plus.color_wheel[3])
        elif self.variation_value == '1':
            rgb_value = (vcolor_plus.color_var_5[0], vcolor_plus.color_var_5[1], vcolor_plus.color_var_5[2], vcolor_plus.color_wheel[3])
        elif self.variation_value == 'c1':
            rgb_value = vcolor_plus.color_custom_1
        elif self.variation_value == 'c2':
            rgb_value = vcolor_plus.color_custom_2
        elif self.variation_value == 'c3':
            rgb_value = vcolor_plus.color_custom_3
        elif self.variation_value == 'c4':
            rgb_value = vcolor_plus.color_custom_4
        elif self.variation_value == 'c5':
            rgb_value = vcolor_plus.color_custom_5
        elif self.variation_value == 'c6':
            rgb_value = vcolor_plus.color_custom_6
        elif self.variation_value == 'c7':
            rgb_value = vcolor_plus.color_custom_7
        elif self.variation_value == 'c8':
            rgb_value = vcolor_plus.color_custom_8
        elif self.variation_value == 'c9':
            rgb_value = vcolor_plus.color_custom_9
        elif self.variation_value == 'c10':
            rgb_value = vcolor_plus.color_custom_10
        elif self.variation_value == 'c11':
            rgb_value = vcolor_plus.color_custom_11
        elif self.variation_value == 'c12':
            rgb_value = vcolor_plus.color_custom_12
        elif self.variation_value == 'c13':
            rgb_value = vcolor_plus.color_custom_13
        elif self.variation_value == 'c14':
            rgb_value = vcolor_plus.color_custom_14
        elif self.variation_value == 'c15':
            rgb_value = vcolor_plus.color_custom_15
        elif self.variation_value == 'c16':
            rgb_value = vcolor_plus.color_custom_16
        else:
            rgb_value = vcolor_plus.color_wheel

        if not active_ob.data.vertex_colors:
            color_layer = bm.loops.layers.color.new("Col")

            layer = bm.loops.layers.color[color_layer.name]
        else:
            layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        for face in bm.faces:
            if vcolor_plus.smooth_hard_application == 'hard':
                if face.select:
                    for loop in face.loops:
                        self.change_vcolor(context, layer=layer, loop=loop, rgb_value=rgb_value)
            else:
                for loop in face.loops:
                        self.change_vcolor(context, layer=layer, loop=loop, rgb_value=rgb_value)

        bm.to_mesh(active_ob.data)

        bpy.ops.vcolor_plus.refresh_palette_outliner()

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_quick_color_switch(OpInfo, Operator):
    """Switch between your main and alternate color"""
    bl_idname = "vcolor_plus.quick_color_switch"
    bl_label = ""

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

        saved_color_tweak = vcolor_plus.live_color_tweak
        vcolor_plus.live_color_tweak = False

        saved_main_color = (
            vcolor_plus.color_wheel[0],
            vcolor_plus.color_wheel[1],
            vcolor_plus.color_wheel[2],
            vcolor_plus.color_wheel[3]
        )

        saved_alt_color = (
            vcolor_plus.alt_color_wheel[0],
            vcolor_plus.alt_color_wheel[1],
            vcolor_plus.alt_color_wheel[2],
            vcolor_plus.alt_color_wheel[3]
        )

        vcolor_plus.color_wheel = saved_alt_color
        vcolor_plus.alt_color_wheel = saved_main_color

        vcolor_plus.live_color_tweak = saved_color_tweak

        if vcolor_plus.live_color_tweak:
            bpy.ops.vcolor_plus.edit_color(edit_type='apply')
        return {'FINISHED'}


class VCOLORPLUS_OT_get_active_color(OpInfo, Operator):
    """Set the Active Color based on the selected vertex color on the mesh"""
    bl_idname = "vcolor_plus.get_active_color"
    bl_label = "Color from Active Vertex"

    def execute(self, context):
        active_ob = context.object

        if not active_ob.data.vertex_colors:
            context.scene.vcolor_plus.color_wheel = (1, 1, 1, 1)
            return {'FINISHED'}

        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        try:
            active_selection = bm.select_history[-1]

            if not isinstance(active_selection, bmesh.types.BMVert):
                self.report({'ERROR'}, "There is more than one Active Vertex selected, please select only one active vertex")
                bpy.ops.object.mode_set(mode = saved_context_mode)
                return{'CANCELLED'}
            else:
                for face in bm.faces:
                    for loop in face.loops:
                        if loop.vert.select:
                            if loop.vert == active_selection:
                                context.scene.vcolor_plus.color_wheel = loop[layer]

                bpy.ops.object.mode_set(mode = saved_context_mode)
                return {'FINISHED'}
        except IndexError:
            self.report({'ERROR'}, "There is no Active Vertex selected")
            bpy.ops.object.mode_set(mode = saved_context_mode)
            return{'CANCELLED'}


class VCOLORPLUS_OT_value_variation(OpInfo, Operator):
    """Applies value variation to the selection without needing to change the Active Color"""
    bl_idname = "vcolor_plus.value_variation"
    bl_label = ""

    variation_value: bpy.props.EnumProperty(
        items=(
            ('.2', ".2", ""),
            ('.4', ".4", ""),
            ('.6', ".6", ""),
            ('.8', ".8", ""),
            ('1', "1", "")
        ),
        options={'HIDDEN'}
    )

    def execute(self, context):
        bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value=self.variation_value)
        return {'FINISHED'}


class VCOLORPLUS_OT_refresh_palette_outliner(OpInfo, Operator):
    """Refresh the palette outliner of the Active Object"""
    bl_idname = "vcolor_plus.refresh_palette_outliner"
    bl_label = "Refresh Palette"

    def execute(self, context):
        active_ob = context.object

        if not active_ob.data.vertex_colors:
            self.report({'ERROR'}, "This object has no vertex colors")
            return{'CANCELLED'}

        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        # Clear VColor list
        active_ob.vcolor_plus_palette_coll.clear()

        # Create a new list
        vcolor_list = []

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                if reconstructed_loop not in vcolor_list and reconstructed_loop != [1,1,1,1]:
                    vcolor_list.append(reconstructed_loop)

        # TODO Order palette outliner based on hue, and then value
        #vcolor_no_hue = [x for x in vcolor_list if x[0] == 0]

        #for vcolor in vcolor_no_hue:
        #    vcolor_list.remove(vcolor)

        for vcolor in vcolor_list:
            item = active_ob.vcolor_plus_palette_coll.add()
            item.obj_id = len(active_ob.vcolor_plus_palette_coll) - 1
            item.saved_color = vcolor
            item.color = vcolor

            if context.scene.vcolor_plus.rgb_hsv_convert_options == 'rgb':
                item.name = f'({round(vcolor[0] * 255)}, {round(vcolor[1] * 255)}, {round(vcolor[2] * 255)}, {round(vcolor[3], 2)})'
            else:
                vcolor_hsv = colorsys.rgb_to_hsv(vcolor[0], vcolor[1], vcolor[2])

                item.name = f'({round(vcolor_hsv[0], 2)}, {round(vcolor_hsv[1], 2)}, {round(vcolor_hsv[2], 2)}, {round(vcolor[3], 2)})'

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_change_outliner_color(OpInfo, Operator):
    """Change the selected outliner color"""
    bl_idname = "vcolor_plus.change_outliner_color"
    bl_label = ""
    bl_options = {'INTERNAL'}

    id: IntProperty()

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[self.id]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                if reconstructed_loop == [active_palette.saved_color[0], active_palette.saved_color[1], active_palette.saved_color[2], active_palette.saved_color[3]]:
                    loop[layer] = [active_palette.color[0], active_palette.color[1], active_palette.color[2], active_palette.color[3]]

        active_palette.name = f'({round(active_palette.color[0] * 255)}, {round(active_palette.color[1] * 255)}, {round(active_palette.color[2] * 255)}, {round(active_palette.color[3], 2)})'

        bm.to_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_get_active_outliner_color(OpInfo, Operator):
    """Apply the Outliner Color to the Active Color"""
    bl_idname = "vcolor_plus.get_active_outliner_color"
    bl_label = "Set as Active Color"

    def execute(self, context):
        return {'FINISHED'}


class VCOLORPLUS_OT_apply_outliner_color(OpInfo, Operator):
    """Apply the Outliner Color to the selected geometry"""
    bl_idname = "vcolor_plus.apply_outliner_color"
    bl_label = "Apply Outliner Color"

    def execute(self, context):
        bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value='p1')
        return {'FINISHED'}


class VCOLORPLUS_OT_select_outliner_color(OpInfo, Operator):
    """Select vertices from the Active Color (DOES NOT REMOVE EXISTING SELECTIONS)"""
    bl_idname = "vcolor_plus.select_outliner_color"
    bl_label = "Select Geometry from Outliner Color"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]
        
        context.tool_settings.mesh_select_mode = (True, False, False)

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                reconstructed_palette_loop = [
                    active_palette.color[0],
                    active_palette.color[1],
                    active_palette.color[2],
                    active_palette.color[3]
                ]

                if reconstructed_loop == reconstructed_palette_loop:
                    loop.vert.select_set(True)

        bm.to_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_delete_outliner_color(OpInfo, Operator):
    """Remove the Outliner Color from the Palette Outliner and geomety"""
    bl_idname = "vcolor_plus.delete_outliner_color"
    bl_label = "Delete Outliner Color"

    def execute(self, context):
        active_ob = context.object
        active_palette = active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index]
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                reconstructed_palette_loop = [
                    active_palette.color[0],
                    active_palette.color[1],
                    active_palette.color[2],
                    active_palette.color[3]
                ]

                if reconstructed_loop == reconstructed_palette_loop:
                    loop[layer] = [1, 1, 1, 1]

        bm.to_mesh(active_ob.data)

        bpy.ops.vcolor_plus.refresh_palette_outliner()

        bpy.ops.object.mode_set(mode = saved_context_mode)
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

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        vertex_list = []

        # Get vertices with the corresponding color value
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.index not in vertex_list:
                    reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                    reconstructed_palette_loop = [
                        active_palette.color[0],
                        active_palette.color[1],
                        active_palette.color[2],
                        active_palette.color[3]
                    ]

                    if reconstructed_loop == reconstructed_palette_loop:
                        vertex_list.append(loop.vert.index)

        converted_vgroup = active_ob.vertex_groups.new(name=active_palette.name)
        converted_vgroup.add(vertex_list, 1.0, 'ADD')

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_custom_color_apply(OpInfo, Operator):
    """Apply the color to your current selection or to your Active Color"""
    bl_idname = "vcolor_plus.custom_color_apply"
    bl_label = ""

    custom_color_name: bpy.props.EnumProperty(
        items=(
            ('c1', "Custom 1", ""),
            ('c2', "Custom 2", ""),
            ('c3', "Custom 3", ""),
            ('c4', "Custom 4", ""),
            ('c5', "Custom 5", ""),
            ('c6', "Custom 6", ""),
            ('c7', "Custom 7", ""),
            ('c8', "Custom 8", ""),
            ('c9', "Custom 9", ""),
            ('c10', "Custom 10", ""),
            ('c11', "Custom 11", ""),
            ('c12', "Custom 12", ""),
            ('c13', "Custom 13", ""),
            ('c14', "Custom 14", ""),
            ('c15', "Custom 15", ""),
            ('c16', "Custom 16", "")
        ),
        options={'HIDDEN'}
    )

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

        if vcolor_plus.custom_palette_apply_options == 'apply_to_sel':
            bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value=self.custom_color_name)
        else: # Apply to Active Color
            if self.custom_color_name == 'c1':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_1
            elif self.custom_color_name == 'c2':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_2
            elif self.custom_color_name == 'c3':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_3
            elif self.custom_color_name == 'c4':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_4
            elif self.custom_color_name == 'c5':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_5
            elif self.custom_color_name == 'c6':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_6
            elif self.custom_color_name == 'c7':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_7
            elif self.custom_color_name == 'c8':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_8
            elif self.custom_color_name == 'c9':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_9
            elif self.custom_color_name == 'c10':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_10
            elif self.custom_color_name == 'c11':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_11
            elif self.custom_color_name == 'c12':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_12
            elif self.custom_color_name == 'c13':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_13
            elif self.custom_color_name == 'c14':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_14
            elif self.custom_color_name == 'c15':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_15
            elif self.custom_color_name == 'c16':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_16

            bpy.ops.vcolor_plus.refresh_palette_outliner()
        return {'FINISHED'}


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_OT_vcolor_shading,
    VCOLORPLUS_OT_edit_color,
    VCOLORPLUS_OT_quick_color_switch,
    VCOLORPLUS_OT_get_active_color,
    VCOLORPLUS_OT_value_variation,
    VCOLORPLUS_OT_refresh_palette_outliner,
    VCOLORPLUS_OT_change_outliner_color,
    VCOLORPLUS_OT_get_active_outliner_color,
    VCOLORPLUS_OT_apply_outliner_color,
    VCOLORPLUS_OT_select_outliner_color,
    VCOLORPLUS_OT_delete_outliner_color,
    VCOLORPLUS_OT_convert_to_vgroup,
    VCOLORPLUS_OT_custom_color_apply
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
