# Vertex Colors Plus Introduction

Vertex Colors Plus is a tool for easily generating Vertex Color on your mesh without needing to actually paint. VColors Plus integrates well with the painting workflow as well, so your workflow will not see any downtime from tasks that lend themselves better to painting.


# Feature Set

(VColor = Vertex Color)

- An "Active Color" system with many core advantages over the basic color swatch
	- Live Tweak option for changing colors live on your mesh while in the color swatch
	- Smooth/Hard vcolor application interpolation for more precise control
	- A second color swatch that can be quickly switched to on the fly
	- Get new Active Color based on the actively selected Vertexes VColor
- A full featured Palette Outliner for viewing and managing all VColors on your Active Object
	- Apply outliner VColor to selected geometry
	- Set outliner VColor as Active Color
	- Select all geometry that use the corresponding outliner VColor
	- Delete outliner VColor from entire object
	- Convert outliner VColor to VGroup for manipulation with things like modifiers
	- HSV/RGB values preview switch
- Many alternative methods of applying VColor
	- Apply with Value or Alpha Variation without changing the Active Color
	- Apply only RGB or A without changing the Active Color
	- Apply to Inner/Outer Selection Border
- Generate random VColor based on many contexts
	- Per UV Shell
	- Per UV Border
	- Per Face
	- Per Vertex
	- Per Point (Face Corner)
	- Extended Dirty Vertex Colors
- A large customizable color palette with any color
	- Includes a preset import/exporter for generating & managing color palettes on the fly (useful for teams)
	- Ability to apply each color to the Active Color or to just fill the current selection
- Integration with Vertex Paint Mode for uninterrupted workflow
- Integration with Daniel Bystedt's [Bake to Vertex Color](https://3dbystedt.gumroad.com/l/zdgxg) add-on.
- Several keymaps and a custom pie menu
- ...and more!

# Installation Guide

1. Click the **Code** button in the top right of the repo & click **Download ZIP** in the dropdown (Do not unpack the ZIP file)
2. Follow this video for the rest of the simple instructions

https://user-images.githubusercontent.com/31065180/137642217-d51470d3-a243-438f-8c49-1e367a8972ab.mp4


# TODO / Future Update Paths

- [ ] Multiple VColor to VGroup methods
	- [x] VColor to single VGroup
	- [ ] VColor to R G B A separated VGroups
	- [ ] Batch options for either listed above
- [ ] VGroup to VColor
- [ ] Import/Export palette presets to/from a custom format


# Known Issues

Most known issues are with the undo stack and palette outliner. These 2 things were... Difficult to fully control. I wish to someday know more about these features to provide better solutions to these problems:

- If you match a color in the palette outliner to another color while "live tweaking" it will merge the colors. This also happens if the color value is pure white.
  - SOLUTION: Avoid dragging the color swatch around arbitrarily, preferring the input fields to change colors from within the Palette Outliner.
- The Palette Outliner will desync if you undo in Edit Mode, but is not the case in other Context Modes.
  - SOLUTION: The Manual Refresh Palette button fixes this, as well as using any operators that cues a resync of the outliner.
- Sometimes the mesh goes pure black after an undo. This doesn't seem to happen after working on a mesh for a while.
  - SOLUTION: This is a visual bug only, your mesh isn't actually colored black. Adding another color or playing with UI elements fixes this.
