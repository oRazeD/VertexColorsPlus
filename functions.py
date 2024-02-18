from typing import Iterable

from bpy.types import (
    Object,
    Mesh,
    FloatColorAttribute
)
from bmesh.types import BMesh, BMLayerItem


def convert_to_plain_array(array_object: Iterable) -> list:
    """Convert custom datatypes to plain 4-size arrays."""
    converted_list = [
        array_object[0], array_object[1],
        array_object[2], array_object[3]
    ]
    return converted_list


def create_mesh_color_attribute(data: Mesh) -> FloatColorAttribute:
    """Gets color attribute from object mode
    or generates one if it doesn't exist."""
    if data.color_attributes:
        return data.color_attributes[0]
    attribute = data.color_attributes.new(
        # TODO: Make the default color
        # attribute name editable
        name="Color",
        type='FLOAT_COLOR',
        domain='POINT',
    )
    for v_index in range(len(data.vertices)):
        attribute.data[v_index].color = [0, 0, 0, 1]
    # NOTE: Alternatively, using foreach_set
    # cols = []
    # for v_index in range(len(data.vertices)):
    #    cols += [0, 0, 0, 1]
    # attribute.data.foreach_set("color", cols)
    return attribute


def create_bmesh_color(bm: BMesh, ob: Object) -> BMLayerItem:
    """Get color attribute layer from `BMesh`
    or generate one if it doesn't exist."""
    if ob.data.color_attributes:
        return bm.loops.layers.float_color[0]
    # TODO: Make the default color
    # attribute name editable
    return bm.loops.layers.float_color.new("Color")


def get_bmesh_active_color_layer(bm: BMesh, ob: Object) -> BMLayerItem:
    """Get the active color attribute layer from `BMesh`."""
    if not ob.data.color_attributes:
        # TODO: Make the default color
        # attribute name editable
        bm.loops.layers.float_color.new("Color")
        ob.data.color_attributes.active_index = 0
    active_color_idx = ob.data.color_attributes.active_index
    layer = bm.loops.layers.float_color[active_color_idx]
    return layer
