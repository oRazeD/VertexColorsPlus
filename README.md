# Introduction
Vertex Colors Plus is a tool for easily applying Vertex Color to your mesh without needing to use the built-in painting tools.

# Features
- An "Active Color" system with many core advantages over the basic color swatch
	- Live Tweak option for changing colors live on your mesh while in the color swatch
	- Smooth/Hard vertex color application interpolation for more precise control
	- A second color swatch that can be used to quickly switch between colors on the fly
	- Get new Active Color based on selected vertices
- A full featured Palette Outliner for viewing and managing all vertex colors on your Active Object
	- Apply outliner VColor to selected geometry
	- Set outliner VColor as Active Color
	- Select all geometry that use the corresponding outliner vertex color
	- Delete outliner VColor from entire object
	- Convert outliner VColor to VGroup for manipulation with things like modifiers
	- HSV/RGB values preview switch
- Many alternative methods of applying vertex color
	- Apply with value or alpha variation
	- Apply only RGB or A channel(s)
	- Apply to Inner/Outer Selection Border
- Generate random vertex color
	- Per UV Shell
	- Per UV Border
	- Per Face
	- Per Vertex
	- Per Point (Face Corner)
	- Extended Dirty Vertex Colors
- A large customizable color palette with any color
	- Includes a preset import/exporter for generating & managing color palettes on the fly (useful for teams)
	- Ability to apply each color to the Active Color or to just fill the current selection
- Compatibility with the vertex painting workflows
- Integration with Vertex Paint Mode for uninterrupted workflow
- Integration with Daniel Bystedt's [Bake to Vertex Color](https://3dbystedt.gumroad.com/l/zdgxg) add-on.
- Several keymaps and a custom pie menu
- ...and more!

# TODO / Future Update Paths
- [ ] Multiple vertex color to vertex group methods
	- [x] Vertex color to single vertex group
	- [ ] Vertex color to R G B A separated vertex groups
	- [ ] Batch options for either listed above
- [ ] Convert vertex group to vertex color
- [ ] Import/export palette presets to/from a custom format

# Known Issues
Most known issues are with the undo stack and palette outliner. These 2 things were... Difficult to fully control. I wish to someday know more about these features to provide better solutions to these problems:

- If you match a color in the palette outliner to another color while "live tweaking" it will merge the colors. This also happens if the color value is pure white.
  - SOLUTION: Avoid dragging the color swatch around arbitrarily, preferring the input fields to change colors from within the Palette Outliner.
- The Palette Outliner will desync if you undo in Edit Mode, but is not the case in other Context Modes.
  - SOLUTION: The Manual Refresh Palette button fixes this, as well as using any operators that cues a resync of the outliner.
- Sometimes the mesh goes pure black after an undo. This doesn't seem to happen after working on a mesh for a while.
  - SOLUTION: This is a visual bug only, your mesh isn't actually colored black. Adding another color or playing with UI elements fixes this.
