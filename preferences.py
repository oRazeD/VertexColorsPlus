import bpy, rna_keymap_ui, colorsys
from bpy.props import BoolProperty, FloatProperty, PointerProperty, FloatVectorProperty, EnumProperty, IntProperty, StringProperty, CollectionProperty
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu


##################################
# Keymapping
##################################


class VCOLORPLUS_addon_keymaps:
    _addon_keymaps = []
    _keymaps = {}

    @classmethod
    def new_keymap(cls, name, kmi_name, kmi_value=None, km_name='3D View',
                   space_type="VIEW_3D", region_type="WINDOW",
                   event_type=None, event_value=None, ctrl=False, shift=False,
                   alt=False, key_modifier="NONE"):

        cls._keymaps.update({name: [kmi_name, kmi_value, km_name, space_type,
                                    region_type, event_type, event_value,
                                    ctrl, shift, alt, key_modifier]
                             })

    @classmethod
    def add_hotkey(cls, kc, keymap_name):

        items = cls._keymaps.get(keymap_name)
        if not items:
            return

        kmi_name, kmi_value, km_name, space_type, region_type = items[:5]
        event_type, event_value, ctrl, shift, alt, key_modifier = items[5:]
        km = kc.keymaps.new(name=km_name, space_type=space_type,
                            region_type=region_type)

        kmi = km.keymap_items.new(kmi_name, event_type, event_value,
                                  ctrl=ctrl,
                                  shift=shift, alt=alt,
                                  key_modifier=key_modifier
                                  )
        if kmi_value:
            kmi.properties.name = kmi_value

        kmi.active = True

        cls._addon_keymaps.append((km, kmi))

    @staticmethod
    def register_keymaps():
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        # In background mode, there's no such thing has keyconfigs.user,
        # because headless mode doesn't need key combos.
        # So, to avoid error message in background mode, we need to check if
        # keyconfigs is loaded.
        if not kc:
            return

        for keymap_name in VCOLORPLUS_addon_keymaps._keymaps.keys():
            VCOLORPLUS_addon_keymaps.add_hotkey(kc, keymap_name)

    @classmethod
    def unregister_keymaps(cls):
        kmi_values = [item[1] for item in cls._keymaps.values() if item]
        kmi_names = [item[0] for item in cls._keymaps.values() if
                     item not in ['wm.call_menu', 'wm.call_menu_pie']]

        for km, kmi in cls._addon_keymaps:
            # remove addon keymap for menu and pie menu
            if hasattr(kmi.properties, 'name'):
                if kmi_values:
                    if kmi.properties.name in kmi_values:
                        km.keymap_items.remove(kmi)

            # remove addon_keymap for operators
            else:
                if kmi_names:
                    if kmi.idname in kmi_names:
                        km.keymap_items.remove(kmi)

        cls._addon_keymaps.clear()

    @staticmethod
    def get_hotkey_entry_item(name, kc, km, kmi_name, kmi_value, col):

        # for menus and pie_menu
        if kmi_value:
            for km_item in km.keymap_items:
                if km_item.idname == kmi_name and km_item.properties.name == kmi_value:
                    col.context_pointer_set('keymap', km)
                    rna_keymap_ui.draw_kmi([], kc, km, km_item, col, 0)
                    return

            col.label(text=f"No hotkey entry found for {name}")
            col.operator(TEMPLATE_OT_restore_hotkey.bl_idname,
                         text="Restore keymap",
                         icon='ADD').km_name = km.name

        # for operators
        else:
            if km.keymap_items.get(kmi_name):
                col.context_pointer_set('keymap', km)
                rna_keymap_ui.draw_kmi([], kc, km, km.keymap_items[kmi_name],
                                       col, 0)

            else:
                col.label(text=f"No hotkey entry found for {name}")
                col.operator(TEMPLATE_OT_restore_hotkey.bl_idname,
                             text="Restore keymap",
                             icon='ADD').km_name = km.name

    @staticmethod
    def draw_keymap_items(wm, layout):
        kc = wm.keyconfigs.user

        for name, items in VCOLORPLUS_addon_keymaps._keymaps.items():
            kmi_name, kmi_value, km_name = items[:3]
            box = layout.box()
            split = box.split()
            col = split.column()
            col.label(text=name)
            col.separator()
            km = kc.keymaps[km_name]
            VCOLORPLUS_addon_keymaps.get_hotkey_entry_item(name, kc, km,
                                                           kmi_name, kmi_value, col)


class TEMPLATE_OT_restore_hotkey(bpy.types.Operator):
    bl_idname = "template.restore_hotkey"
    bl_label = "Restore hotkeys"
    bl_options = {'REGISTER', 'INTERNAL'}

    km_name: StringProperty()

    def execute(self, context):
        context.preferences.active_section = 'KEYMAP'
        wm = context.window_manager
        kc = wm.keyconfigs.addon
        km = kc.keymaps.get(self.km_name)
        if km:
            km.restore_to_default()
            context.preferences.is_dirty = True
        context.preferences.active_section = 'ADDONS'
        return {'FINISHED'}


class VCOLORPLUS_OT_add_hotkey(bpy.types.Operator):
    bl_idname = "vcolor_plus.add_hotkey"
    bl_label = "Add Hotkeys"
    bl_options = {'REGISTER', 'INTERNAL'}

    km_name: StringProperty()

    def execute(self, context):
        context.preferences.active_section = 'KEYMAP'
        wm = context.window_manager
        kc = wm.keyconfigs.addon
        km = kc.keymaps.get(self.km_name)
        if km:
            km.restore_to_default()
            context.preferences.is_dirty = True
        context.preferences.active_section = 'ADDONS'
        return {'FINISHED'}


############################################################
# PROPERTY GROUP
############################################################


class VCOLORPLUS_property_group(bpy.types.PropertyGroup):
    ### UPDATE FUNCTIONS ###

    def update_color_wheel(self, context):
        # Update selected vertices if live color tweak is on
        if self.live_color_tweak and context.mode in ('EDIT_MESH', 'PAINT_VERTEX'):
            bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value='color_wheel')

        # Update draw brush in vertex color mode
        bpy.data.brushes["Draw"].color = (self.color_wheel[0], self.color_wheel[1], self.color_wheel[2])

        # Convert the RGB value to HSV for easy tweaking
        color_wheel_hsv = colorsys.rgb_to_hsv(self.color_wheel[0], self.color_wheel[1], self.color_wheel[2])
        
        # Set value/alpha variation preview
        self.value_var = colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], self.value_var_slider)
        self.alpha_var = (*(colorsys.hsv_to_rgb(color_wheel_hsv[0], color_wheel_hsv[1], color_wheel_hsv[2])), self.alpha_var_slider)

    def update_color_variation(self, context): # extension of update_color_wheel, but using the variation value
        self.update_color_wheel(context)

        # Update selected vertices if live color tweak is on
        if self.live_color_tweak and context.mode in ('EDIT_MESH', 'PAINT_VERTEX'):
            bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value='value_var')

    def update_alpha_variation(self, context): # extension of update_color_wheel, but using the variation value
        self.update_color_wheel(context)

        # Update selected vertices if live color tweak is on
        if self.live_color_tweak and context.mode in ('EDIT_MESH', 'PAINT_VERTEX'):
            bpy.ops.vcolor_plus.edit_color(edit_type='apply', variation_value='alpha_var')

    def palette_update(self, context):
        bpy.ops.vcolor_plus.refresh_palette_outliner()
        
    ### PROPERTIES ###

    live_color_tweak: BoolProperty(
        name="Live Tweak",
        description='If enabled, changing the Active Color will update any vertices that are selected'
    )

    interpolation_type: EnumProperty(
        items=(
            ('smooth', "Smooth", ""),
            ('hard', "Hard", "")
        )
    )

    custom_palette_apply_options: EnumProperty(
        items=(
            ('apply_to_sel', "Fill Selection", ""),
            ('apply_to_col', "Set Active Color", "")
        )
    )

    rgb_hsv_convert_options: EnumProperty(
        items=(
            ('hsv', "HSV", ""),
            ('rgb', "RGBA", "")
        ),
        update=palette_update
    )

    generation_type: EnumProperty(
        items=(
            ('per_uv_shell', "Per UV Shell  (Random Color)", ""),
            ('per_uv_border', "Per UV Border", ""),
            ('per_face', "Per Face", ""),
            ('per_vertex', "Per Vertex", ""),
            ('per_point', "Per Point (Face Corner)", ""),
            ('dirty_color', "Dirty Vertex Colors", "")
        ),
        name='Generation Type'
    )

    generation_per_uv_border_options: EnumProperty(
        items=(
            ('random_col', "Random Color", ""),
            ('active_col', "Active Color", "")
        )
    )

    color_wheel: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1,
        update=update_color_wheel
    )

    alt_color_wheel: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[1, 1, 1, 1],
        size=4,
        min=0,
        max=1
    )

    overlay_color_placeholder: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 0],
        size=4,
        min=0,
        max=1
    )

    value_var_slider: FloatProperty(
        name="",
        description='Applies value variation to the selection without the need to change the Active Color (WARNING: This works with Live Tweak)',
        default=.5,
        min=0,
        max=1,
        subtype='FACTOR',
        update=update_color_variation
    )

    value_var: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[.5, .5, .5],
        min=0,
        max=1
    )

    alpha_var_slider: FloatProperty(
        name="",
        description='Applies alpha variation to the selection without the need to change the Active Color (WARNING: This works with Live Tweak)',
        default=0,
        min=0,
        max=1,
        subtype='FACTOR',
        update=update_alpha_variation
    )

    alpha_var: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, .5],
        size=4,
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
        default=[.75, .75, .75, 1],
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
        default=[.5, .5, .5, 1],
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
        default=[.25, .25, .25, 1],
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
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )


class VCOLORPLUS_collection_property(bpy.types.PropertyGroup):
    def update_palette_color(self, context):
        if [*self.color] != [*self.saved_color]:
            bpy.ops.vcolor_plus.change_outliner_color(saved_id=self.id)

            # This only somewhat fixes the clearing [1,1,1,1] val colors? Strange.
            if [*self.color[:3]] != [1, 1, 1] and [*self.saved_color[:3]] != [1, 1, 1]:
                bpy.ops.vcolor_plus.refresh_palette_outliner(saved_id=self.saved_color)

    id: IntProperty()

    color: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1,
        update=update_palette_color,
        description='Click to change the current color for this layer (WARNING: If the set color matches another color or is pure white it will be merged/removed!)'
    )

    saved_color: FloatVectorProperty(
        name="",
        subtype='COLOR_GAMMA',
        default=[0, 0, 0, 1],
        size=4,
        min=0,
        max=1
    )


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
        "vcolor_plus.color_custom_16"
    ]

    # Where to store the preset
    preset_subdir = "vcolor_plus"


############################################################
# USER PREFERENCES
############################################################


class VCOLORPLUS_MT_addon_prefs(bpy.types.AddonPreferences):
    bl_idname=__package__

    tabs: EnumProperty(
        items=(
            ('general', "General", "Information & Settings"),
            ('keymaps', "Keymaps", "Keymap Customization")
        )
    )

    auto_palette_refresh: BoolProperty(
        name="Auto Palette Refresh",
        description=
        '''If disabled, will stop updating the entire palette outliner whenever you run an operator.

Useful if your scene is slowing down.

Certain items may still be changed if the code interacts with the outliner directly''',
        default=True
    )

    max_outliner_items: IntProperty(
        name="Max Outliner Items",
        description='The maximum amount of items allowed in the Palette Outliner per object',
        default=25,
        min=1,
        max=100
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "tabs", expand=True)

        if self.tabs == 'general':
            col = layout.column()

            box = col.box()
            split = box.split()
            split.label(text='Automatically Refresh Palette Outliner')
            split.prop(self, 'auto_palette_refresh')

            col.separator(factor=.5)

            box = col.box()
            split = box.split()
            split.label(text='Maximum # of Items in Palette Outliner')
            split.prop(self, 'max_outliner_items')

        else: # Keymaps
            VCOLORPLUS_addon_keymaps.draw_keymap_items(context.window_manager, layout)


##################################
# REGISTRATION
##################################


classes = (
    VCOLORPLUS_MT_presets,
    VCOLORPLUS_PT_presets,
    VCOLORPLUS_OT_add_preset,
    VCOLORPLUS_MT_addon_prefs,
    VCOLORPLUS_property_group,
    VCOLORPLUS_collection_property,
    VCOLORPLUS_OT_add_hotkey
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vcolor_plus = PointerProperty(type=VCOLORPLUS_property_group)
    bpy.types.Object.vcolor_plus_palette_coll = CollectionProperty(type=VCOLORPLUS_collection_property)
    bpy.types.Object.vcolor_plus_custom_index = IntProperty(name='R G B A values for the layer (Renaming does not work)')

    # Assign keymaps & register
    VCOLORPLUS_addon_keymaps.new_keymap('Vertex Colors Pie', 'wm.call_menu_pie', 'VCOLORPLUS_MT_pie_menu',
                                        'Mesh', 'EMPTY', 'WINDOW', 'C',
                                        'PRESS', False, True, False)

    VCOLORPLUS_addon_keymaps.new_keymap('Fill Selection', 'vcolor_plus.edit_color', None,
                                        'Mesh', 'EMPTY', 'WINDOW', 'F',
                                        'PRESS', True, True, False, 'NONE')

    VCOLORPLUS_addon_keymaps.new_keymap('Clear Selection', 'vcolor_plus.edit_color_clear', None,
                                        'Mesh', 'EMPTY', 'WINDOW', 'F',
                                        'PRESS', False, True, True, 'NONE')

    VCOLORPLUS_addon_keymaps.register_keymaps()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    VCOLORPLUS_addon_keymaps.unregister_keymaps()

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
