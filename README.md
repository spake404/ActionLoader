# Action Loader for Blender 5.1

Action Loader is a Blender add-on for browsing every Action in the current
`.blend`, assigning an Action to the active object, and previewing animation
sets without repeatedly opening the Action Editor menu.

This fork updates the add-on for Blender 5.1's layered Actions and Action
Slots. It is based on
[vaner-org/ActionLoader](https://github.com/vaner-org/ActionLoader), which in
turn is a fork of the original
[frederico4d/ActionLoader](https://github.com/frederico4d/ActionLoader).

## Blender 5.1 changes

- Supports layered Actions and reads F-Curves from the active Action Slot.
- Preserves the matching Action Slot when switching Actions. This is important
  when one Action contains slots for both a rig and a weapon.
- Updates the object-location mute control for channel bags.
- Adds Play/Pause and frame-jump controls to the Action Loader panel.
- Adds optional Auto Play when selecting an Action.
- Adds guards for missing objects, animation data, Actions, and invalid list
  indices.
- Cleans up all registered properties when the add-on is disabled.

## Install

1. Download `ActionLoader.py`.
2. In Blender 5.1, open `Edit > Preferences > Add-ons`.
3. Choose `Install from Disk` and select `ActionLoader.py`.
4. Enable `Animation: Action Loader`.
5. Open the 3D View sidebar with `N`, then select the `Animation` tab.

Select an object or armature and click an Action in the list to assign it.
Use the search field in the list to filter names such as `ryu_idle`.

## Preview controls

- `Play/Pause`: preview the current Action.
- `Auto Play`: start playback whenever an Action is selected.
- `Set Auto Range`: update the scene range for the selected Action.
- `Jump to first Frame`: return to the Action's first frame after switching.
- `Custom/Keyframes`: choose stored custom ranges or the Action's keyframe
  range.

## Compatibility test

Run the test with Blender 5.1:

```powershell
blender.exe --factory-startup --background --python tests/blender_compat_test.py
```

The test creates a layered Action with separate rig and tool slots, switches
Actions, verifies slot preservation and frame range updates, and checks that
location muting only affects the active slot.

## License

GPL-3.0, inherited from the upstream project.
