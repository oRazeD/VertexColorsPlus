
import bpy, bmesh
from bpy.types import Operator


class VCOLORPLUS_OT_vcolor_shading(Operator):
    """Saves current shading settings and sets up optimal vertex color shading"""
    bl_idname = "vcolor_plus.vcolor_shading_toggle"
    bl_label = "VColor Shading Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return{'FINISHED'}


class VCOLORPLUS_OT_value_variation(Operator):
    """Applies value variation to the selection without needing to change the Active Color"""
    bl_idname = "vcolor_plus.value_variation"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

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

        bpy.ops.vcolor_plus.refresh_active_palette()
        return {'FINISHED'}


class VCOLORPLUS_OT_edit_color(Operator):
    """Edits the active vertex color set based on the selected operator"""
    bl_idname = "vcolor_plus.edit_color"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

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

        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(context.object.data)

        if self.variation_value == '.2':
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
        elif self.variation_value == 'c17':
            rgb_value = vcolor_plus.color_custom_17
        elif self.variation_value == 'c18':
            rgb_value = vcolor_plus.color_custom_18
        elif self.variation_value == 'c19':
            rgb_value = vcolor_plus.color_custom_19
        elif self.variation_value == 'c20':
            rgb_value = vcolor_plus.color_custom_20
        else:
            rgb_value = vcolor_plus.color_wheel

        if not context.object.data.vertex_colors:
            color_layer = bm.loops.layers.color.new("Col")

            layer = bm.loops.layers.color[color_layer.name]
        else:
            layer = bm.loops.layers.color[context.object.data.vertex_colors.active.name]

        for face in bm.faces:
            if vcolor_plus.smooth_hard_application == 'hard':
                if face.select:
                    for loop in face.loops:
                        self.change_vcolor(context, layer=layer, loop=loop, rgb_value=rgb_value)
            else:
                for loop in face.loops:
                        self.change_vcolor(context, layer=layer, loop=loop, rgb_value=rgb_value)

        bm.to_mesh(context.object.data)

        bpy.ops.vcolor_plus.refresh_active_palette()

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_get_active_color(Operator):
    """Set the active color based on the actively selected vertex color"""
    bl_idname = "vcolor_plus.get_active_color"
    bl_label = "Color from Active Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.object.data.vertex_colors:
            context.scene.vcolor_plus.color_wheel = (1, 1, 1, 1)
            return{'FINISHED'}

        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(context.object.data)

        layer = bm.loops.layers.color[context.object.data.vertex_colors.active.name]

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
                            if loop.vert.select and loop.vert == active_selection:
                                context.scene.vcolor_plus.color_wheel = loop[layer]
                        
                bm.to_mesh(context.object.data)

                bpy.ops.object.mode_set(mode = saved_context_mode)
                return {'FINISHED'}
        except IndexError:
            self.report({'ERROR'}, "There is no Active Vertex selected")
            bpy.ops.object.mode_set(mode = saved_context_mode)
            return{'CANCELLED'}


class VCOLORPLUS_OT_custom_color_apply(Operator):
    """Apply the color to your current selection or to your Active Color"""
    bl_idname = "vcolor_plus.custom_color_apply"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

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
            ('c16', "Custom 16", ""),
            ('c17', "Custom 17", ""),
            ('c18', "Custom 18", ""),
            ('c19', "Custom 19", ""),
            ('c20', "Custom 20", ""),
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
            elif self.custom_color_name == 'c17':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_17
            elif self.custom_color_name == 'c18':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_18
            elif self.custom_color_name == 'c19':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_19
            elif self.custom_color_name == 'c20':
                vcolor_plus.color_wheel = vcolor_plus.color_custom_20

        bpy.ops.vcolor_plus.refresh_active_palette()
        return{'FINISHED'}


class VCOLORPLUS_OT_quick_color_switch(Operator):
    """Switch between your main and alternate color"""
    bl_idname = "vcolor_plus.quick_color_switch"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

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

        bpy.ops.vcolor_plus.refresh_active_palette()
        return{'FINISHED'}


class VCOLORPLUS_OT_refresh_active_palette(Operator):
    """Refresh the palette outliner of the Active Object"""
    bl_idname = "vcolor_plus.refresh_active_palette"
    bl_label = "Refresh Palette"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.object.data.vertex_colors:
            self.report({'ERROR'}, "This object has no vertex colors")
            return{'CANCELLED'}

        active_ob = context.object
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

        #vcolor_no_hue = [x for x in vcolor_list if x[0] == 0]

        #for vcolor in vcolor_no_hue:
        #    vcolor_list.remove(vcolor)

        for vcolor in vcolor_list:
            item = active_ob.vcolor_plus_palette_coll.add()
            item.obj_id = len(active_ob.vcolor_plus_palette_coll) - 1
            item.name = f'({round(vcolor[0] * 255)}, {round(vcolor[1] * 255)}, {round(vcolor[2] * 255)}, {round(vcolor[3], 2)})'
            item.color = vcolor
            item.prop_parent = active_ob.name
            active_ob.vcolor_plus_custom_index = len(active_ob.vcolor_plus_palette_coll) - 1

        bm.to_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_delete_outliner_color(Operator):
    """Delete the active vertex color from the Active Object"""
    bl_idname = "vcolor_plus.delete_outliner_color"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_ob = context.object
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                reconstructed_palette_loop = [
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[0],
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[1],
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[2],
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[3],
                ]

                if reconstructed_loop == reconstructed_palette_loop:
                    loop[layer] = [1, 1, 1, 1]

        bm.to_mesh(active_ob.data)

        bpy.ops.vcolor_plus.refresh_active_palette()

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return{'FINISHED'}


class VCOLORPLUS_OT_select_outliner_color(Operator):
    """Select vertices from the active vertex color (DOES NOT REMOVE EXISTING SELECTIONS)"""
    bl_idname = "vcolor_plus.select_outliner_color"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_ob = context.object
        saved_context_mode = active_ob.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(active_ob.data)

        layer = bm.loops.layers.color[active_ob.data.vertex_colors.active.name]

        bpy.context.tool_settings.mesh_select_mode = (True, False, False)

        for face in bm.faces:
            for loop in face.loops:
                reconstructed_loop = [loop[layer][0], loop[layer][1], loop[layer][2], loop[layer][3]]

                reconstructed_palette_loop = [
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[0],
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[1],
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[2],
                    active_ob.vcolor_plus_palette_coll[active_ob.vcolor_plus_custom_index].color[3],
                ]

                if reconstructed_loop == reconstructed_palette_loop:
                    loop.vert.select_set(True)

        bm.to_mesh(active_ob.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return{'FINISHED'}


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_OT_get_active_color,
    VCOLORPLUS_OT_vcolor_shading,
    VCOLORPLUS_OT_value_variation,
    VCOLORPLUS_OT_edit_color,
    VCOLORPLUS_OT_custom_color_apply,
    VCOLORPLUS_OT_quick_color_switch,
    VCOLORPLUS_OT_refresh_active_palette,
    VCOLORPLUS_OT_delete_outliner_color,
    VCOLORPLUS_OT_select_outliner_color
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
