import bpy
from bpy.types import Panel, UIList
from .preferences import VCOLORPLUS_PT_presets


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
        row.enabled = False
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

        col2.separator(factor=.3)
                
        split = col.split(factor=.7, align=True)
        split.scale_y = 1.3
        split.operator("vcolor_plus.edit_color", text='Fill Selection', icon='CHECKMARK').edit_type = 'apply'
        split.operator("vcolor_plus.edit_color", text='Clear', icon='X').edit_type = 'clear'

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(vcolor_plus, 'smooth_hard_application', expand=True)
        
        if vcolor_plus.smooth_hard_application == 'hard':
            box = col.box()
            box.scale_y = .8
            box.label(text='Only works with face selections', icon='INFO')

        layout.operator("vcolor_plus.get_active_color")


class VCOLORPLUS_PT_quick_apply(PanelInfo, Panel):
    bl_label = 'Quick Apply'
    bl_parent_id = 'VCOLORPLUS_PT_ui'

    def draw(self, context):
        vcolor_plus = context.scene.vcolor_plus

        layout = self.layout

        col = layout.column(align=True)
        col.operator("vcolor_plus.edit_color", text='Apply to All').edit_type = 'apply_all'
        col.operator("vcolor_plus.edit_color", text='Clear All').edit_type = 'clear_all'

        box = layout.box()
        col = box.column(align=True)

        split = col.split(align=True)
        split.label(text='Value Variation')

        row = col.row(align=True)
        row.operator("vcolor_plus.value_variation", text='.2').variation_value = '.2'
        row.operator("vcolor_plus.value_variation", text='.4').variation_value = '.4'
        row.operator("vcolor_plus.value_variation", text='.6').variation_value = '.6'
        row.operator("vcolor_plus.value_variation", text='.8').variation_value = '.8'
        row.operator("vcolor_plus.value_variation", text='1').variation_value = '1'

        row = col.row(align=True)
        row.enabled = False
        row.prop(vcolor_plus, 'color_var_1')
        row.prop(vcolor_plus, 'color_var_2')
        row.prop(vcolor_plus, 'color_var_3')
        row.prop(vcolor_plus, 'color_var_4')
        row.prop(vcolor_plus, 'color_var_5')


class VCOLORPLUS_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.scale_x = .35
        row.enabled = False
        row.prop(item, 'color')

        split = layout.split(factor=.075)
        split.label(text="")
        split.label(text=item.name)


class VCOLORPLUS_PT_palette_outliner(PanelInfo, Panel):
    bl_label = 'Palette Outliner'
    bl_parent_id = 'VCOLORPLUS_PT_ui'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("vcolor_plus.refresh_active_palette", text='Refresh Palette', icon='FILE_REFRESH')

        row = layout.row()

        col = row.column(align=True)
        col.template_list("VCOLORPLUS_UL_items", "", context.object, "vcolor_plus_palette_coll", context.object, "vcolor_plus_custom_index", rows=4)
        
        if len(context.selected_objects) > 1:
            box = col.box()
            box.scale_y = .8
            box.label(text = 'Only uses Active Object', icon='INFO')

        col = row.column()
        col.operator("vcolor_plus.select_outliner_color", icon='RESTRICT_SELECT_OFF', text="")
        col.separator(factor=2)
        col.operator("vcolor_plus.delete_outliner_color", icon='TRASH', text="")


class VCOLORPLUS_PT_custom_palette(PanelInfo, Panel):
    bl_label = 'Customizable Palette'
    bl_parent_id = 'VCOLORPLUS_PT_ui'

    def draw_header_preset(self, context):
        VCOLORPLUS_PT_presets.draw_panel_header(self.layout)

    def draw(self, context):
        vcolor_plus = context.scene.vcolor_plus

        layout = self.layout

        col = layout.column(align=True)

        row = col.row()
        row.prop(vcolor_plus, 'custom_palette_apply_options', expand=True)

        col.separator()

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_1')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c1'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_2')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c2'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_3')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c3'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_4')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c4'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_5')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c5'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_6')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c6'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_7')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c7'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_8')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c8'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_9')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c9'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_10')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c10'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_11')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c11'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_12')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c12'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_13')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c13'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_14')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c14'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_15')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c15'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_16')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c16'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_17')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c17'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_18')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c18'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_19')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c19'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_20')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'c20'


class VCOLORPLUS_PT_bake_to_vertex_color(PanelInfo, Panel):
    bl_label = 'Bake to Vertex Color'
    bl_parent_id = 'VCOLORPLUS_PT_ui'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        if 'bakeToVertexColor_1_0_8' in bpy.context.preferences.addons:
            row = layout.row()
            row.label(text="Bake Type")
            row.prop(scene.bake_to_vertex_color_props, "bake_pass", text="")

            row = layout.row()
            row.label(text="Bake UV")
            row.prop(scene.bake_to_vertex_color_props, "bake_uv_type", text="")

            row = layout.row()
            row.label(text="Lightmap Resolution")
            row.prop(scene.bake_to_vertex_color_props, "resolution", text="")

            row = layout.row()
            row.label(text="Samples")
            row.prop(scene.bake_to_vertex_color_props, "samples", text="")

            row = layout.row()
            row.label(text="Smooth VColors")
            row.prop(scene.bake_to_vertex_color_props, "smooth_vertex_colors", text="")

            row = layout.row()
            row.label(text="Delete Bake Image")
            row.prop(scene.bake_to_vertex_color_props, "delete_bake_image", text="")

            row = layout.row()
            row.label(text="VColor Name")
            row.prop(scene.bake_to_vertex_color_props, "vertex_color_name", text="")

            row = layout.row()
            row.scale_y = 1.5
            row.separator(factor=.25)

            row = layout.row()
            row.scale_y = 1.5
            bake_to_vcolor_op = row.operator('object.bake_to_vertex_col', text='Bake Pass to Vertex Color', icon='RENDER_STILL')
            bake_to_vcolor_op.resolution = int(scene.bake_to_vertex_color_props.resolution)
            bake_to_vcolor_op.samples = scene.bake_to_vertex_color_props.samples
            bake_to_vcolor_op.vertex_color_name = scene.bake_to_vertex_color_props.vertex_color_name
            bake_to_vcolor_op.smooth_vertex_colors = scene.bake_to_vertex_color_props.smooth_vertex_colors
            bake_to_vcolor_op.bake_uv_type = scene.bake_to_vertex_color_props.bake_uv_type
            bake_to_vcolor_op.delete_bake_image = scene.bake_to_vertex_color_props.delete_bake_image
            bake_to_vcolor_op.bake_pass = scene.bake_to_vertex_color_props.bake_pass
        else:
            box = layout.box()
            box.operator("wm.url_open", text="Bake to Vertex Color on Gumroad").url = "https://3dbystedt.gumroad.com/l/zdgxg"
            box.label(text='You do not have Bake to', icon='ERROR')
            box.label(text='Vertex Color installed & enabled')
            box.label(text='or you do not have the latest version')


class VCOLORPLUS_PT_vcolor_sets(PanelInfo, Panel):
    bl_label = 'Vertex Color Sets'
    bl_parent_id = 'VCOLORPLUS_PT_ui'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.enabled = False
        col.scale_y = 1.3
        col.operator("vcolor_plus.vcolor_shading_toggle", text='Convert VColor to VGroups')

        row = col.row(align=True)
        row.scale_y = .7
        row.prop(context.scene.vcolor_plus, "vcolor_convert_options", expand=True)

        try:
            row = layout.row()

            col = row.column()
            col.template_list("MESH_UL_vcols", "vcols", context.object.data, "vertex_colors", context.object.data.vertex_colors, "active_index", rows=4)

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
    VCOLORPLUS_PT_quick_apply,
    VCOLORPLUS_PT_palette_outliner,
    VCOLORPLUS_PT_custom_palette,
    VCOLORPLUS_UL_items,
    VCOLORPLUS_PT_bake_to_vertex_color,
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
