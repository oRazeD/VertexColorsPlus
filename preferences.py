import bpy
from bpy.props import BoolProperty, PointerProperty, FloatVectorProperty, EnumProperty
import colorsys

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

    color_wheel: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[1, 1, 1, 1],
        size=4,
        min=0,
        max=1,
        update=update_color_wheel
    )

    alt_color_wheel: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )

    color_var_1: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[0, 0, 0],
        min=0,
        max=1
    )

    color_var_2: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[0, 0, 0],
        min=0,
        max=1
    )

    color_var_3: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[0, 0, 0],
        min=0,
        max=1
    )

    color_var_4: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[0, 0, 0],
        min=0,
        max=1
    )

    color_var_5: FloatVectorProperty(
        name="",
        subtype='COLOR',
        default=[0, 0, 0],
        min=0,
        max=1
    )


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


##################################
# REGISTRATION
##################################


classes = (
    VCOLORPLUS_property_group,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vcolor_plus = PointerProperty(type=VCOLORPLUS_property_group)


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
