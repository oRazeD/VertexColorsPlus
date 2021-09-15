import bpy
from bpy.types import Panel, UIList, Menu
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

        col = layout.column(align=True)

        split = col.split(factor=.6, align=True)
        split.scale_y = 1.3
        edit_color_op = split.operator("vcolor_plus.edit_color", text='Fill Selection', icon='CHECKMARK')
        edit_color_op.edit_type = 'apply'
        edit_color_op.variation_value = 'color_wheel'
        split.operator("vcolor_plus.edit_color", text='Clear Sel', icon='X').edit_type = 'clear'

        box = col.box()

        col2 = box.column(align=True)
        
        split = col2.split()
        split.scale_y = 1.3
        split.label(text='Active Color', icon='COLOR')

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

        col = layout.column(align=True)

        split = col.split(factor=.3)
        split.label(text=' Blending')

        row = split.row()
        row.prop(vcolor_plus, 'smooth_hard_application', expand=True)
        
        if vcolor_plus.smooth_hard_application == 'hard':
            box = col.box()
            box.scale_y = .8
            box.label(text='Only works with face selections', icon='INFO')

        layout.operator("vcolor_plus.get_active_color", icon='RESTRICT_COLOR_ON')

        layout.operator("vcolor_plus.vcolor_shading", icon='SHADING_TEXTURE')


class VCOLORPLUS_PT_quick_apply(PanelInfo, Panel):
    bl_label = 'Quick Apply'
    bl_parent_id = 'VCOLORPLUS_PT_ui'

    def draw(self, context):
        vcolor_plus = context.scene.vcolor_plus

        layout = self.layout

        col = layout.column(align=True)
        col.scale_y = 1.1
        edit_color_op = col.operator("vcolor_plus.edit_color", text='Apply to All', icon='CHECKMARK')
        edit_color_op.edit_type = 'apply_all'
        edit_color_op.variation_value = 'color_wheel'
        col.operator("vcolor_plus.edit_color", text='Clear All', icon='X').edit_type = 'clear_all'

        box = layout.box()
        col = box.column(align=True)
        col.label(text=' Apply to Selection Border')

        row = col.row(align=True)
        row.operator('vcolor_plus.apply_color_to_border', text='Inner', icon='CLIPUV_HLT').border_type = 'inner'
        row.operator('vcolor_plus.apply_color_to_border', text='Outer', icon='CLIPUV_DEHLT').border_type = 'outer'

        box = layout.box()
        col = box.column(align=True)
        col.label(text=' Value Variation')

        row = col.row(align=True)
        row.operator("vcolor_plus.value_variation", text='.2').variation_value = 'color_var_1'
        row.operator("vcolor_plus.value_variation", text='.4').variation_value = 'color_var_2'
        row.operator("vcolor_plus.value_variation", text='.6').variation_value = 'color_var_3'
        row.operator("vcolor_plus.value_variation", text='.8').variation_value = 'color_var_4'
        row.operator("vcolor_plus.value_variation", text='1').variation_value = 'color_var_5'

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
        row.scale_x = 0.325
        row.prop(item, 'color')

        split = layout.split(factor=.025)
        split.label(text="")
        split.label(text=item.name)


class VCOLORPLUS_PT_palette_outliner(PanelInfo, Panel):
    bl_label = 'Palette Outliner'
    bl_parent_id = 'VCOLORPLUS_PT_ui'

    def draw(self, context):
        layout = self.layout

        disable_ui = False

        try:
            idx_check = context.object.vcolor_plus_palette_coll[context.object.vcolor_plus_custom_index]
        except (IndexError, ValueError):
            disable_ui = True

        if not len(context.object.vcolor_plus_palette_coll):
            disable_ui = True

        col = layout.column()
        col.operator("vcolor_plus.refresh_palette_outliner", text='Refresh Palette', icon='FILE_REFRESH')

        row = layout.row()

        col = row.column(align=True)
        col.template_list("VCOLORPLUS_UL_items", "", context.object, "vcolor_plus_palette_coll", context.object, "vcolor_plus_custom_index", rows=4)
        
        if len(context.selected_objects) > 1:
            box = col.box()
            box.scale_y = .8
            box.label(text = 'Only uses Active Object', icon='INFO')

        row2 = col.row(align=True)
        row2.enabled = not disable_ui
        row2.prop(context.scene.vcolor_plus, 'rgb_hsv_convert_options', expand=True)

        col = row.column()
        col.enabled = not disable_ui

        col.operator("vcolor_plus.apply_outliner_color", icon='CHECKMARK', text="")
        col.separator(factor = .49)
        col.operator("vcolor_plus.get_active_outliner_color", icon='RESTRICT_COLOR_ON', text="")
        col.separator(factor = .49)
        col.operator("vcolor_plus.select_outliner_color", icon='RESTRICT_SELECT_OFF', text="")
        col.separator(factor = .49)
        col.operator("vcolor_plus.delete_outliner_color", icon='TRASH', text="")
        col.separator(factor = .49)
        col.operator("vcolor_plus.convert_to_vgroup", icon='GROUP_VERTEX', text="")


class VCOLORPLUS_PT_custom_palette(PanelInfo, Panel):
    bl_label = 'Customizable Palette'
    bl_parent_id = 'VCOLORPLUS_PT_ui'

    def draw_header_preset(self, context):
        VCOLORPLUS_PT_presets.draw_panel_header(self.layout)

    def draw(self, context):
        vcolor_plus = context.scene.vcolor_plus

        layout = self.layout

        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(vcolor_plus, 'custom_palette_apply_options', expand=True)

        col.separator(factor=.5)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_1')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_1'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_2')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_2'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_3')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_3'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_4')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_4'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_5')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_5'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_6')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_6'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_7')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_7'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_8')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_8'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_9')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_9'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_10')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_10'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_11')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_11'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_12')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_12'

        col = layout.column(align=True)

        split = col.split(align=True)
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_13')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_13'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_14')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_14'
        
        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_15')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_15'

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_custom_16')
        split.operator("vcolor_plus.custom_color_apply", icon='CHECKMARK').custom_color_name = 'color_custom_16'


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

        row = layout.row()

        col = row.column()
        col.template_list("MESH_UL_vcols", "vcols", context.object.data, "vertex_colors", context.object.data.vertex_colors, "active_index", rows=4)

        col = row.column(align=True)
        col.operator("mesh.vertex_color_add", icon='ADD', text="")
        col.operator("mesh.vertex_color_remove", icon='REMOVE', text="")


class VCOLORPLUS_PT_vcolor_generation(PanelInfo, Panel):
    bl_label = 'Generate Vertex Color'
    bl_parent_id = 'VCOLORPLUS_PT_ui'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        vcolor_plus = context.scene.vcolor_plus

        layout = self.layout

        col = layout.column(align=True)
        col.scale_y = 1.3
        col.operator('vcolor_plus.generate_vcolor', text='Generate VColor', icon='GROUP_VCOL')

        row = col.row(align=True)
        row.scale_y = .8
        row.prop(vcolor_plus, 'generation_type', text='')


class VCOLORPLUS_MT_pie_menu(Menu):
    bl_idname = "VCOLORPLUS_MT_pie_menu"
    bl_label = "Vertex Colors Plus"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        vcolor_plus = context.scene.vcolor_plus

        #4 - LEFT
        col = pie.column()

        box = col.box().column(align=True)

        box2 = box.box()
        col2 = box2.column(align=True)
        
        split = col2.split(align=True)
        split.scale_y = 1.3
        split.label(text='Active Color', icon='COLOR')

        row = split.row(align=True)
        row.prop(vcolor_plus, 'color_wheel')
        row.operator("vcolor_plus.quick_color_switch", icon='LOOP_FORWARDS')

        split = col2.split(factor=.65)
        split.scale_y = 1.3
        split.separator()
        split.prop(vcolor_plus, 'alt_color_wheel')

        split = col2.split()
        split.separator()
        split.prop(vcolor_plus, 'live_color_tweak')

        col3 = box.column()

        col3.separator(factor=.5)

        split = col3.split(align=True)
        split.scale_y = 1.25
        split.label(text=' Blending')
        split.prop(vcolor_plus, 'smooth_hard_application', expand=True)

        col3.separator(factor=.5)

        row = col3.row()
        row.scale_y = 1.25
        row.operator("vcolor_plus.get_active_color", icon='RESTRICT_COLOR_ON')
        #6 - RIGHT
        col = pie.column()

        col.scale_x = .5

        box = col.box().column(align=True)

        col2 = box.column(align=True)   
        col2.scale_y = 1.25

        edit_color_op = col2.operator("vcolor_plus.edit_color", text='Apply to All')
        edit_color_op.edit_type = 'apply_all'
        edit_color_op.variation_value = 'color_wheel'
        col2.operator("vcolor_plus.edit_color", text='Clear All').edit_type = 'clear_all'
        col2.separator(factor=.5)

        box = col2.box()
        col = box.column(align=True)
        col.label(text=' Value Variation')
        
        row = col.row(align=True) # Painfully inefficient execution but for some reason pies cut off random items elsewise
        col3 = row.column(align=True)
        col3.operator("vcolor_plus.value_variation", text='.2').variation_value = 'color_var_1'

        col4 = col3.column(align=True)
        col4.enabled = False
        col4.prop(vcolor_plus, 'color_var_1')

        col3 = row.column(align=True)
        col3.operator("vcolor_plus.value_variation", text='.4').variation_value = 'color_var_2'

        col4 = col3.column(align=True)
        col4.enabled = False
        col4.prop(vcolor_plus, 'color_var_2')

        col3 = row.column(align=True)
        col3.operator("vcolor_plus.value_variation", text='.6').variation_value = 'color_var_3'

        col4 = col3.column(align=True)
        col4.enabled = False
        col4.prop(vcolor_plus, 'color_var_3')

        col3 = row.column(align=True)
        col3.operator("vcolor_plus.value_variation", text='.8').variation_value = 'color_var_4'

        col4 = col3.column(align=True)
        col4.enabled = False
        col4.prop(vcolor_plus, 'color_var_4')

        col3 = row.column(align=True)
        col3.operator("vcolor_plus.value_variation", text='1').variation_value = 'color_var_5'

        col4 = col3.column(align=True)
        col4.enabled = False
        col4.prop(vcolor_plus, 'color_var_5')
        #2 - BOTTOM
        pie.operator("vcolor_plus.edit_color", text='Clear Selection', icon='PANEL_CLOSE').edit_type = 'clear'
        #8 - TOP
        edit_color_op = pie.operator("vcolor_plus.edit_color", text='Fill Selection', icon='CHECKMARK')
        edit_color_op.edit_type = 'apply'
        edit_color_op.variation_value = 'color_wheel'
        #7 - TOP - LEFT
        pie.separator()
        #9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


################################################################################################################
# REGISTRATION
################################################################################################################


classes = (
    VCOLORPLUS_PT_ui,
    VCOLORPLUS_PT_quick_apply,
    VCOLORPLUS_UL_items,
    VCOLORPLUS_PT_palette_outliner,
    VCOLORPLUS_PT_custom_palette,
    VCOLORPLUS_PT_vcolor_generation,
    VCOLORPLUS_PT_bake_to_vertex_color,
    VCOLORPLUS_PT_vcolor_sets,
    VCOLORPLUS_MT_pie_menu
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
