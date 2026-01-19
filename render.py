import bpy
import os
import re

# =========================
# CONFIG
# =========================
action_label = "wash_sponge"
base_output_dir = "/Users/bnabnubne/PROJECT/HandActivityRecognition/render_output"

CAM_PREFIX = "Cam_"                 # lấy tất cả camera bắt đầu bằng Cam_
skin_names = ["SkinA", "SkinB","SkinC"]

HAND_MESH_NAME = "HandMesh"

FRAME_START = None
FRAME_END   = None
FRAME_STEP  = 1

FILE_FORMAT = "PNG"
USE_TRANSPARENT_BG = True

# =========================
# GPU on Apple Silicon (Metal)
# =========================
def enable_gpu_metal():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'

    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences

    cprefs.compute_device_type = 'METAL'
    try:
        cprefs.get_devices()
    except:
        pass

    for d in cprefs.devices:
        d.use = True

    scene.cycles.device = 'GPU'
    print("✅ Cycles GPU enabled (METAL). Devices:", [d.name for d in cprefs.devices if d.use])

# =========================
# Helpers
# =========================
def get_cameras_by_prefix(prefix: str):
    """Lấy tất cả object CAMERA có tên bắt đầu bằng prefix (bao gồm .001, .002...) và sort hợp lý."""
    cams = [obj for obj in bpy.data.objects if obj.type == 'CAMERA' and obj.name.startswith(prefix)]

    # sort theo số sau Cam_ và theo suffix .xxx
    def cam_sort_key(name: str):
        # ví dụ: Cam_6.001 -> main=6, sub=1
        m = re.match(rf"^{re.escape(prefix)}(\d+)(?:\.(\d+))?$", name)
        if m:
            main = int(m.group(1))
            sub = int(m.group(2)) if m.group(2) else 0
            return (main, sub, name)
        return (10**9, 10**9, name)

    cams.sort(key=lambda o: cam_sort_key(o.name))
    return cams

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

# =========================
# MAIN RENDER
# =========================
def render_animation_multi_cam():
    enable_gpu_metal()
    scene = bpy.context.scene

    # Transparent background
    scene.render.film_transparent = bool(USE_TRANSPARENT_BG)

    # Output settings
    scene.render.image_settings.file_format = FILE_FORMAT
    if FILE_FORMAT == "PNG":
        scene.render.image_settings.color_mode = 'RGBA' if USE_TRANSPARENT_BG else 'RGB'

    # hand mesh
    hand_obj = bpy.data.objects.get(HAND_MESH_NAME)
    if not hand_obj:
        raise Exception(f"❌ Không tìm thấy object '{HAND_MESH_NAME}'")

    # frame range
    fs = FRAME_START if FRAME_START is not None else scene.frame_start
    fe = FRAME_END   if FRAME_END   is not None else scene.frame_end

    # folder output theo action
    out_dir = os.path.join(base_output_dir, action_label)
    ensure_dir(out_dir)

    # auto cameras
    cameras = get_cameras_by_prefix(CAM_PREFIX)
    if not cameras:
        raise Exception(f"❌ Không tìm thấy camera nào bắt đầu bằng '{CAM_PREFIX}'")
    print("✅ Cameras found:", [c.name for c in cameras])

    # render loops
    for skin in skin_names:
        mat = bpy.data.materials.get(skin)
        if not mat:
            print(f"⚠️ Không thấy material '{skin}', bỏ qua.")
            continue

        hand_obj.active_material = mat

        for cam in cameras:
            scene.camera = cam

            cam_dir = os.path.join(out_dir, cam.name, skin)
            ensure_dir(cam_dir)

            for fr in range(fs, fe + 1, FRAME_STEP):
                scene.frame_set(fr)

                filename = f"{action_label}_{cam.name}_{skin}_f{fr:05d}.png"
                scene.render.filepath = os.path.join(cam_dir, filename)

                bpy.ops.render.render(write_still=True)
                print("Render:", filename)

    print(" DONE: rendered all cameras with prefix, multi-skin, BG OFF, GPU ON.")

# RUN
render_animation_multi_cam()