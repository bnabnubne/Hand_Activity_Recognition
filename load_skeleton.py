import bpy
from mathutils import Vector, Matrix

# =========================================================
# CONFIG
# =========================================================
FILE_PATH = "/Users/bnabnubne/PROJECT/HandActivityRecognition/Hand_pose_annotation_v1/Hand_pose_annotation_v1/Subject_1/wash_sponge/1/skeleton.txt"
HAND_OBJ_NAME = "Hand" 
FRAME_OFFSET = 1
SPREAD = 1.0  # >1.0: xòe ngang hơn 

# World -> Camera extrinsic (F-PHAB)
CAM_EXTR = Matrix((
    (0.999988496304,   -0.00468848412856,  0.000982563360594, 25.7),
    (0.00469115935266,  0.999985218048,   -0.00273845880292,  1.22),
    (-0.000969709653873, 0.00274303671904, 0.99999576807,     3.902),
    (0.0,                0.0,              0.0,                1.0),
))

# =========================================================
# F-PHAB joint order:
# [0] Wrist
# [1] TMCP [2] IMCP [3] MMCP [4] RMCP [5] PMCP
# [6] TPIP [7] TDIP [8] TTIP
# [9] IPIP [10] IDIP [11] ITIP
# [12] MPIP [13] MDIP [14] MTIP
# [15] RPIP [16] RDIP [17] RTIP
# [18] PPIP [19] PDIP [20] PTIP
# =========================================================

JOINT_TO_EMPTY = {
    # MCP
    1: "THUMB_MCP",
    2: "INDEX_MCP",
    3: "MIDDLE_MCP",
    4: "RING_MCP",
    5: "PINKY_MCP",

    # PIP
    6:  "THUMB_PIP",
    9:  "INDEX_PIP",
    12: "MIDDLE_PIP",
    15: "RING_PIP",
    18: "PINKY_PIP",

    # TIP
    8:  "THUMB_TIP",
    11: "INDEX_TIP",
    14: "MIDDLE_TIP",
    17: "RING_TIP",
    20: "PINKY_TIP",
}

# =========================================================
# HELPERS
# =========================================================

def load_fphab_skeleton(path: str):
    """
    Each line: t x1 y1 z1 ... x21 y21 z21   (world coords, mm)
    Return: frames[frame] = [(x,y,z)*21]
    """
    frames = []
    with open(path, "r") as f:
        for ln, line in enumerate(f, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            vals = list(map(float, parts[1:]))
            if len(vals) != 63:
                print(f"[WARN] line {ln}: expected 63 floats, got {len(vals)} -> skip")
                continue
            joints = []
            for j in range(21):
                joints.append((vals[3*j], vals[3*j+1], vals[3*j+2]))
            frames.append(joints)
    print(f"Loaded {len(frames)} frames from {path}")
    return frames

def world_to_cam(v_world):
    v4 = CAM_EXTR @ Vector((v_world[0], v_world[1], v_world[2], 1.0))
    return Vector((v4.x, v4.y, v4.z))  # still mm

def cam_to_blender(v_cam_mm: Vector):
    """
    F-PHAB camera coords:
        x: right
        y: down
        z: forward
    Blender:
        X right, Y forward, Z up
    """
    v = v_cam_mm * 0.001  # mm -> m
    return Vector((SPREAD * v.x, v.z, -v.y))

def clear_anim(obj):
    if obj and obj.animation_data:
        obj.animation_data_clear()

# =========================================================
# MAIN BAKE
# =========================================================

def bake():
    frames_world = load_fphab_skeleton(FILE_PATH)

    hand = bpy.data.objects.get(HAND_OBJ_NAME)
    if not hand:
        raise RuntimeError(f"Armature '{HAND_OBJ_NAME}' not found")

    # Clear animation for hand + empties only
    clear_anim(hand)
    for name in JOINT_TO_EMPTY.values():
        clear_anim(bpy.data.objects.get(name))

    scene = bpy.context.scene
    scene.frame_start = FRAME_OFFSET
    scene.frame_end = FRAME_OFFSET + len(frames_world) - 1

    # ensure object mode for setting object locations
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # sanity: warn missing empties
    for idx, ename in JOINT_TO_EMPTY.items():
        if bpy.data.objects.get(ename) is None:
            print(f"[WARN] Missing empty '{ename}' (joint {idx})")

    for f_idx, joints_world in enumerate(frames_world):
        frame_no = FRAME_OFFSET + f_idx
        scene.frame_set(frame_no)

        # world -> cam -> blender
        joints_bl = []
        for j in joints_world:
            jc = world_to_cam(j)
            jb = cam_to_blender(jc)
            joints_bl.append(jb)

        # wrist drives whole armature object location
        hand.location = joints_bl[0]
        hand.keyframe_insert("location", frame=frame_no)

        # set empties for MCP/PIP/TIP
        for j_idx, empty_name in JOINT_TO_EMPTY.items():
            obj = bpy.data.objects.get(empty_name)
            if not obj:
                continue
            obj.location = joints_bl[j_idx]
            obj.keyframe_insert("location", frame=frame_no)

    print(" DONE: Loaded Wrist + MCP/PIP/TIP empties (IK/pole untouched).")

# RUN
bake()