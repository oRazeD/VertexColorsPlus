import bpy
from bpy.types import Panel


################################################################################################################
# UI
################################################################################################################


class PanelInfo:
    bl_category = 'VColor Plus'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class VCOLORPLUS_PT_ui(PanelInfo, Panel):
    bl_label = 'Vertex Colors Plus'

    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_MESH', 'PAINT_VERTEX'}

    def draw(self, context):
        vcolor_plus = context.scene.vcolor_plus

        layout = self.layout

        row = layout.row()
        row.scale_y = 1.5
        row.operator("vcolor_plus.vcolor_shading_toggle", icon='VPAINT_HLT')

        col = layout.column(align=True)
        box = col.box()

        col2 = box.column(align=True)
        
        split = col2.split()
        split.scale_y = 1.3
        split.label(text='Active Color')

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_wheel')
        row.operator("vcolor_plus.quick_color_switch", icon='LOOP_FORWARDS')

        split = col2.split()
        split.scale_y = 1.3
        split.separator()

        split_row = split.split(factor=.25)
        split_row.separator()
        split_row.prop(vcolor_plus, 'alt_color_wheel')

        split = col2.split()
        split.separator()
        split.prop(vcolor_plus, 'live_color_tweak')

        split = col.split(factor=.65, align=True)
        split.scale_y = 1.3
        split.operator("vcolor_plus.edit_color", text='Apply to Selection', icon='CHECKMARK').edit_type = 'apply'
        split.operator("vcolor_plus.edit_color", text='Clear', icon='X').edit_type = 'clear'

        row = col.row()
        row.prop(vcolor_plus, 'smooth_hard_application', expand=True)

        if vcolor_plus.smooth_hard_application == 'hard':
            box = col.box()
            box.label(text='Only works with face selections', icon='INFO')

        layout.separator()

        layout.operator("vcolor_plus.edit_color", text='Apply to All').edit_type = 'apply_all'
        layout.operator("vcolor_plus.edit_color", text='Clear All').edit_type = 'clear_all'

        layout.operator("vcolor_plus.get_active_color")


class VCOLORPLUS_PT_vcolor_sets(PanelInfo, Panel):
    bl_label = 'Vertex Color Sets'
    bl_parent_id = 'VCOLORPLUS_PT_ui'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        try:
            row = layout.row()
            col = row.column()

            col.template_list("MESH_UL_vcols", "vcols", context.object.data, "vertex_colors", context.object.data.vertex_colors, "active_index", rows=2)

            col = row.column(align=True)
            col.operator("mesh.vertex_color_add", icon='ADD', text="")
            col.operator("mesh.vertex_color_remove", icon='REMOVE', text="")
        except AttributeError:
            layout.label(text='No Active Object is selected', icon='ERROR')


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_PT_ui,
    VCOLORPLUS_PT_vcolor_sets
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
