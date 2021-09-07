
import bpy, bmesh
from bpy.types import Operator


class VCOLORPLUS_OT_operator(Operator):
    """Operator description"""
    bl_idname = "vcolor_plus.operator"
    bl_label = "Operator Name"

    def execute(self, context):
        return{'FINISHED'}


class VCOLORPLUS_OT_vcolor_shading(Operator):
    """Saves current shading settings and sets up optimal vertex color shading"""
    bl_idname = "vcolor_plus.vcolor_shading_toggle"
    bl_label = "_VColor Shading Mode"

    def execute(self, context):
        return{'FINISHED'}


class VCOLORPLUS_OT_edit_color(Operator):
    """Edits the active vertex color set based on the selected operator"""
    bl_idname = "vcolor_plus.edit_color"
    bl_label = ""

    edit_type: bpy.props.EnumProperty(
        items=(
            ('apply', "Apply", ""),
            ('apply_all', "Apply All", ""),
            ('clear', "Clear", ""),
            ('clear_all', "Clear All", "")
        )
    )

    def execute(self, context):
        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(context.object.data)

        if not context.object.data.vertex_colors:
            color_layer = bm.loops.layers.color.new("col")

            layer = bm.loops.layers.color[color_layer.name]
        else:
            layer = bm.loops.layers.color[context.object.data.vertex_colors.active.name]

        for face in bm.faces:
            for loop in face.loops:
                if self.edit_type == 'apply' and loop.vert.select:
                    loop[layer] = context.scene.vcolor_plus.color_wheel

                elif self.edit_type == 'apply_all':
                    loop[layer] = context.scene.vcolor_plus.color_wheel

                elif self.edit_type == 'clear' and loop.vert.select:
                    loop[layer] = [1,1,1,1]

                elif self.edit_type == 'clear_all':
                    loop[layer] = [1,1,1,1]

        bm.to_mesh(context.object.data)

        bpy.ops.object.mode_set(mode = saved_context_mode)
        return {'FINISHED'}


class VCOLORPLUS_OT_get_active_color(Operator):
    """Set the active color based on the actively selected vertex color"""
    bl_idname = "vcolor_plus.get_active_color"
    bl_label = "Color from Active Vertex"

    def execute(self, context):
        if not context.object.data.vertex_colors:
            self.report({'ERROR'}, "There is no Vertex Color sets on the Active Object")
            return{'CANCELLED'}

        saved_context_mode = context.object.mode

        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm = bmesh.new()
        bm.from_mesh(context.object.data)

        layer = bm.loops.layers.color[context.object.data.vertex_colors.active.name]

        try:
            elem = bm.select_history[-1]

            if not isinstance(elem, bmesh.types.BMVert):
                self.report({'ERROR'}, "There is more than one Active Vertex selected, please select only one active vertex")
                bpy.ops.object.mode_set(mode = saved_context_mode)
                return{'CANCELLED'}
            else:
                for face in bm.faces:
                    for loop in face.loops:
                        if loop.vert.select:
                            if loop.vert.select and loop.vert == elem:
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

    def execute(self, context):
        vcolor_plus = context.scene.vcolor_plus

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
        return{'FINISHED'}


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_OT_operator,
    VCOLORPLUS_OT_get_active_color,
    VCOLORPLUS_OT_vcolor_shading,
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
