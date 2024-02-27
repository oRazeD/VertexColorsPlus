from typing import Iterable

from bpy.types import Mesh, Attribute
from bmesh.types import BMesh, BMLayerItem


def convert_to_plain_array(array_object: Iterable) -> list:
    """Convert custom datatypes to plain 4-size arrays."""
    converted_list = [
        array_object[0], array_object[1],
        array_object[2], array_object[3]
    ]
    return converted_list


def public_color_exists(data: Mesh) -> bool:
    """Check if any public color attributes exist.

    A private color attribute is classified as an
    attribute with a `_` name prefix."""
    public_attributes = []
    for attribute in data.color_attributes:
        if attribute.name.startswith("_"):
            continue
        public_attributes.append(attribute)
    if not public_attributes:
        return False
    return True


def create_color(data: Mesh, name: str="Color") -> Attribute:
    """Create color attribute from object mode."""
    color_attributes = data.color_attributes
    attribute = color_attributes.new(
        name, type='BYTE_COLOR', domain='CORNER'
    )
    color_attributes.active_color_index = \
    color_attributes.render_color_index = len(color_attributes)-1
    for idx in range(len(data.vertices)):
        attribute.data[idx].color = [1, 1, 1, 1]
    # NOTE: Alternatively, using foreach_set
    #cols = []
    #for idx in range(len(data.vertices)):
    #   cols += [1, 1, 1, 1]
    #attribute.data.foreach_set("color", cols)
    return attribute


def get_active_color(data: Mesh) -> Attribute | None:
    """Get the active color attribute from a given `Mesh`."""
    color_attributes = data.color_attributes
    if not color_attributes or not public_color_exists(data):
        return None

    idx = color_attributes.active_color_index
    if idx == -1:
        color_attributes.active_color_index = idx = 0

    try:
        return color_attributes[idx]
    except IndexError:
        return None


def get_bmesh_active_color(bm: BMesh, data: Mesh) -> BMLayerItem | None:
    """Get the active color attribute layer from `BMesh`."""
    color_attributes = data.color_attributes
    if not color_attributes or not public_color_exists(data):
        return None

    idx = color_attributes.active_color_index
    if idx == -1:
        color_attributes.active_color_index = idx = 0

    try:
        attribute = color_attributes[idx]
    except IndexError:
        return None
    if attribute.domain == 'CORNER':
        if attribute.data_type == 'FLOAT_COLOR':
            return bm.loops.layers.float_color.get(attribute.name)
        return bm.loops.layers.color.get(attribute.name)
    if attribute.domain == 'POINT':
        if attribute.data_type == 'FLOAT_COLOR':
            return bm.verts.layers.float_color.get(attribute.name)
        return bm.verts.layers.color.get(attribute.name)
    return None
