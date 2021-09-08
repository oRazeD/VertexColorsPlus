
import bpy, bmesh
from bpy.types import Operator


class VCOLORPLUS_OT_vcolor_shading(Operator):
    """Saves current shading settings and sets up optimal vertex color shading"""
    bl_idname = "vcolor_plus.vcolor_shading_toggle"
    bl_label = "_VColor Shading Mode"
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

    variation_value: bpy.props.StringProperty(default='0')

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
        else:
            rgb_value = vcolor_plus.color_wheel

        if not context.object.data.vertex_colors:
            color_layer = bm.loops.layers.color.new("col")

            layer = bm.loops.layers.color[color_layer.name]
        else:
            layer = bm.loops.layers.color[context.object.data.vertex_colors.active.name]

        for face in bm.faces:
            if vcolor_plus.smooth_hard_application == 'hard' and face.select:
                for loop in face.loops:
                    self.change_vcolor(context, layer=layer, loop=loop, rgb_value=rgb_value)
            else:
                for loop in face.loops:
                        self.change_vcolor(context, layer=layer, loop=loop, rgb_value=rgb_value)

        bm.to_mesh(context.object.data)

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
        return{'FINISHED'}


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_OT_get_active_color,
    VCOLORPLUS_OT_vcolor_shading,
    VCOLORPLUS_OT_value_variation,
    VCOLORPLUS_OT_edit_color,
    VCOLORPLUS_OT_quick_color_switch
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
