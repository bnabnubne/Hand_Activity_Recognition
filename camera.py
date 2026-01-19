import bpy
import math

N = 8
radius = 0.7
heights = [0.1, 0.5]
target_object_name = "Hand"

for h_idx, height in enumerate(heights):
    for i in range(N):
        angle = (2 * math.pi / N) * i
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = height
        bpy.ops.object.camera_add(location=(x, y, z))
        cam = bpy.context.active_object
        cam.name = f"Cam_{i+1}"
        cam.data.display_size = 0.05
        constraint = cam.constraints.new(type='TRACK_TO')
        constraint.target = bpy.data.objects[target_object_name]
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'