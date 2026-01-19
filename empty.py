import bpy
from mathutils import Vector

ARM_NAME = "Hand"

# Map finger -> (TIP bone, PIP bone) theo tên rig của mày
MAP = {
    "THUMB":  ("finger1-3.R", "finger1-2.R"),
    "INDEX":  ("finger2-3.R", "finger2-2.R"),
    "MIDDLE": ("finger3-3.R", "finger3-2.R"),
    "RING":   ("finger4-3.R", "finger4-2.R"),
    "PINKY":  ("finger5-3.R", "finger5-2.R"),
}

EMPTY_SIZE = 0.015

arm = bpy.data.objects.get(ARM_NAME)
if not arm or arm.type != "ARMATURE":
    raise RuntimeError(f"Armature '{ARM_NAME}' not found or not an armature.")

def delete_if_exists(name: str):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)

def create_empty(name: str, loc_world: Vector):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'SPHERE'
    empty.empty_display_size = EMPTY_SIZE
    bpy.context.collection.objects.link(empty)
    empty.location = loc_world
    # save base right away
    empty["base_location"] = loc_world.copy()
    return empty

# 1) delete old empties
for f in MAP.keys():
    delete_if_exists(f + "_TIP")
    delete_if_exists(f + "_PIP")

# 2) create empties at REST pose bone tails
for f, (tip_bone_name, pip_bone_name) in MAP.items():
    tip_b = arm.data.bones.get(tip_bone_name)
    pip_b = arm.data.bones.get(pip_bone_name)

    if not tip_b or not pip_b:
        print(f"[WARN] missing bone for {f}: {tip_bone_name} or {pip_bone_name}")
        continue

    # bone.tail_local is in armature local space; convert to world
    tip_world = arm.matrix_world @ tip_b.tail_local
    pip_world = arm.matrix_world @ pip_b.tail_local

    create_empty(f + "_TIP", tip_world)
    create_empty(f + "_PIP", pip_world)

print(" Empties recreated from REST pose + base_location saved.")