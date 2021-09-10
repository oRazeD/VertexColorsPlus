import bpy
from bpy.props import BoolProperty, PointerProperty, FloatVectorProperty, EnumProperty, IntProperty, StringProperty, CollectionProperty
import colorsys
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu


################################################################################################################
# PRESETS
################################################################################################################


class VCOLORPLUS_MT_presets(Menu):
    bl_label = ""
    preset_subdir = "vcolor_plus"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class VCOLORPLUS_PT_presets(PresetPanel, Panel):
    bl_label = 'VColor Plus Presets'
    preset_subdir = 'vcolor_plus'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'vcolor_plus.preset_add'


class VCOLORPLUS_OT_add_preset(AddPresetBase, bpy.types.Operator):
    bl_idname = "vcolor_plus.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "VCOLORPLUS_MT_presets"

    # Variable used for all preset values
    preset_defines = ["vcolor_plus=bpy.context.scene.vcolor_plus"]

    # Properties to store in the preset
    preset_values = [
        "vcolor_plus.color_custom_1",
        "vcolor_plus.color_custom_2",
        "vcolor_plus.color_custom_3",
        "vcolor_plus.color_custom_4",
        "vcolor_plus.color_custom_5",
        "vcolor_plus.color_custom_6",
        "vcolor_plus.color_custom_7",
        "vcolor_plus.color_custom_8",
        "vcolor_plus.color_custom_9",
        "vcolor_plus.color_custom_10",
        "vcolor_plus.color_custom_11",
        "vcolor_plus.color_custom_12",
        "vcolor_plus.color_custom_13",
        "vcolor_plus.color_custom_14",
        "vcolor_plus.color_custom_15",
        "vcolor_plus.color_custom_16",
        "vcolor_plus.color_custom_17",
        "vcolor_plus.color_custom_18",
        "vcolor_plus.color_custom_19",
        "vcolor_plus.color_custom_20",
    ]

    # Where to store the preset
    preset_subdir = "vcolor_plus"


############################################################
# USER PREFERENCES
############################################################


class VCOLORPLUS_MT_addon_prefs(bpy.types.AddonPreferences):
    bl_idname=__package__

    def draw(self, context):
        layout=self.layout

        layout.label(text='Keymaps TODO')


############################################################
# PROPERTY GROUP
############################################################


class VCOLORPLUS_property_group(bpy.types.PropertyGroup):
    ### UPDATE FUNCTIONS ###

    def update_color_wheel(self, context):
        # Update selected vertices if live color tweak is on
        if self.live_color_tweak:
            bpy.ops.vcolor_plus.edit_color(edit_type='apply')

        # Update draw brush in vertex color mode
        bpy.data.brushes["Draw"].color = (self.color_wheel[0], self.color_wheel[1], self.color_wheel[2])

        # Convert the RGB value to HSV for easy tweaking
        color_wheel_hsv = colorsys.rgb_to_hsv(self.color_wheel[0], self.color_wheel[1], self.color_wheel[2])
        
        # Set value of color variation previews
        self.color_var_1 = colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], .2)
        self.color_var_2 = colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], .4)
        self.color_var_3 = colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], .6)
        self.color_var_4 = colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], .8)
        self.color_var_5 = colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], 1)

    ### PROPERTIES ###

    live_color_tweak: BoolProperty(
        name="Live Tweak",
        description='If enabled, changing the Active Color will update any vertices that are selected'
    )

    smooth_hard_application: EnumProperty(
        items=(
            ('smooth', "Smooth", ""),
            ('hard', "Hard", "")
        )
    )

    custom_palette_apply_options: EnumProperty(
        items=(
            ('apply_to_sel', "Fill Selection", ""),
            ('apply_to_col', "Apply Active Color", "")
        )
    )

    vcolor_convert_options: EnumProperty(
        items=(
            ('vgroup_per_color', "VGroup per Color", ""),
            ('vgroup_to_rgba', "VColor to RGBA", "")
        )
    )

    color_wheel: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[1, 1, 1, 1],
        size=4,
        min=0,
        max=1,
        update=update_color_wheel
    )

    alt_color_wheel: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_var_1: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.2, .2, .2],
        min=0,
        max=1
    )

    color_var_2: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.4, .4, .4],
        min=0,
        max=1
    )

    color_var_3: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.6, .6, .6],
        min=0,
        max=1
    )

    color_var_4: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.8, .8, .8],
        min=0,
        max=1
    )

    color_var_5: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[1, 1, 1],
        min=0,
        max=1
    )

    color_custom_1: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[1, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_2: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 1, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_3: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 1, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_4: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[1, 1, 1, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_5: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.75, .75, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_6: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, .75, .75, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_7: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.75, 0, .75, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_8: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.75, .75, .75, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_9: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.5, .75, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_10: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, .5, .75, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_11: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.75, 0, .5, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_12: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.5, .5, .5, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_13: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.25, .5, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_14: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, .5, .25, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_15: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.25, 0, .5, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_16: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.25, .25, .25, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_17: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.1, .25, .1, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_18: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.25, .1, .1, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_19: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.1, .1, .25, 1],
        size=4,
        min=0,
        max=1
    )

    color_custom_20: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )


class VCOLORPLUS_collection_property(bpy.types.PropertyGroup):
    name: StringProperty()
    obj_id: IntProperty()
    color: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )


##################################
# REGISTRATION
##################################


classes = (
    VCOLORPLUS_MT_presets,
    VCOLORPLUS_PT_presets,
    VCOLORPLUS_OT_add_preset,
    VCOLORPLUS_MT_addon_prefs,
    VCOLORPLUS_property_group,
    VCOLORPLUS_collection_property
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vcolor_plus = PointerProperty(type=VCOLORPLUS_property_group)
    bpy.types.Object.vcolor_plus_palette_coll = CollectionProperty(type=VCOLORPLUS_collection_property)
    bpy.types.Object.vcolor_plus_custom_index = IntProperty()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.vcolor_plus
    del bpy.types.Object.vcolor_plus_palette_coll
    del bpy.types.Object.vcolor_plus_custom_index


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
