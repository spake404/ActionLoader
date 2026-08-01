import importlib.util
import pathlib
import sys

import bpy


ADDON_PATH = pathlib.Path(__file__).resolve().parents[1] / "ActionLoader.py"


def load_addon():
    module_name = "action_loader_compat_test"
    spec = importlib.util.spec_from_file_location(module_name, ADDON_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    module.register()
    return module


def create_object(name):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    return obj


def add_location_curves(action, obj, start, end):
    obj.animation_data_create().action = action
    for index in range(3):
        curve = action.fcurve_ensure_for_datablock(
            obj,
            "location",
            index=index,
        )
        curve.keyframe_points.insert(start, 0.0)
        curve.keyframe_points.insert(end, 1.0)
    return obj.animation_data.action_slot.identifier


def main():
    addon = load_addon()
    tool = create_object("Tool")
    rig = create_object("Rig")

    multi_slot_action = bpy.data.actions.new("A_MultiSlot")
    tool_slot = add_location_curves(multi_slot_action, tool, 1, 10)
    rig_slot = add_location_curves(multi_slot_action, rig, 5, 20)
    assert tool_slot == "OBTool"
    assert rig_slot == "OBRig"

    current_action = bpy.data.actions.new("B_Current")
    assert add_location_curves(current_action, rig, 30, 40) == "OBRig"

    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    assert rig.animation_data.action == current_action
    assert rig.animation_data.action_slot.identifier == "OBRig"

    scene = bpy.context.scene
    scene.actionloader_rangemode = "1"
    scene.actionloader_autorange = True
    scene.actionloader_1stFrame = True
    scene.actionloader_autoplay = False

    target_index = list(bpy.data.actions).index(multi_slot_action)
    rig.action_list_index = target_index

    assert rig.animation_data.action == multi_slot_action
    assert rig.animation_data.action_slot.identifier == "OBRig"
    assert len(addon.action_fcurves(multi_slot_action, rig)) == 3
    assert scene.frame_start == 1
    assert scene.frame_end == 20
    assert scene.frame_current == 1

    rig_curves = addon.location_fcurves(multi_slot_action, rig)
    tool_curves = addon.action_fcurves(multi_slot_action, tool)
    assert len(rig_curves) == 3
    assert len(tool_curves) == 3

    result = bpy.ops.muteloc.action()
    assert result == {"FINISHED"}
    assert all(curve.mute and curve.hide and curve.lock for curve in rig_curves)
    assert all(not curve.mute for curve in tool_curves)

    result = bpy.ops.muteloc.action()
    assert result == {"FINISHED"}
    assert all(not curve.mute and not curve.hide and not curve.lock for curve in rig_curves)

    addon.unregister()
    assert not hasattr(bpy.types.Scene, "actionloader_autoplay")
    assert not hasattr(bpy.types.Scene, "actionloader_rangemode")
    print("ACTION_LOADER_5_1_COMPAT_TEST_OK")


if __name__ == "__main__":
    main()
