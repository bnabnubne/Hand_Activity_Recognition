# Hand Motion Reconstruction & Synthetic Data Generation (Blender)

This repository provides a Blender-based pipeline for reconstructing real hand motion from the F-PHAB dataset and generating synthetic hand images under multiple camera viewpoints and appearance variations.

The project combines:
- Real hand motion data (F-PHAB skeleton annotations)  
- Inverse kinematics–driven hand rig in Blender  
- Synthetic data generation (multi-view, multi-skin, controlled lighting)  

All scripts are executed inside Blender’s Text Editor, using the provided .blend file.

---

## 📁 Repository Structure

.
├── hand_jan.blend                 
├── RENDER.blend                   # Main working scene (preconfigured)
├── Hand_pose_annotation_v1/       # F-PHAB dataset (skeleton.txt files)
├── camera.py                      # Camera generation (base scene only)
├── empty.py                       # IK empty creation (base scene only)
├── load_skeleton.py               # Load F-PHAB skeleton motion
├── render.py                      # Multi-camera, multi-skin rendering
└── README.md


---

## 🧩 Pipeline Overview

The complete pipeline consists of the following logical steps:
1. Prepare a 3D hand rig with IK constraints in Blender  
2. Create empty objects as IK targets (TIP / PIP / MCP)  
3. Load real hand motion from F-PHAB (skeleton.txt)  
4. Generate multiple cameras around the hand  
5. Render synthetic hand images with different viewpoints and skin colors  

To avoid rig mismatch and animation transfer issues, all steps are performed inside a single Blender scene.

---

## 🛠 Requirements
- Blender 4.x (tested on Blender 4.2 LTS)  
- Apple Silicon with Metal support (for GPU rendering)  
- F-PHAB dataset (placed under Hand_pose_annotation_v1/)  

---

## ▶️ How to Run (Recommended Workflow)

⚠️ **Important**  
- Open `RENDER.blend` first  
- All scripts must be run via  
  `Blender → Scripting → Text Editor`  
- Do not run scripts externally via Python  

---

## ✅ Main Usage (Using RENDER.blend)

The provided `RENDER.blend` file is already preconfigured and includes:
- Hand armature (`Hand`)  
- Hand mesh (`HandMesh`)  
- IK constraints and joint limits  
- IK target empties (`*_TIP`, `*_PIP`, `*_MCP`)  
- Multi-view cameras (`Cam_*`)  
- Lighting and render settings  

👉 For normal use, you only need to run **TWO scripts**.

---

### Step 1 – Load Hand Motion from F-PHAB

Edit the dataset path in `load_skeleton.py`:
```python
FILE_PATH = ".../Subject_1/wash_sponge/1/skeleton.txt"
```
Then run: load_skeleton.py
What this script does:
•	Reads skeleton.txt frame-by-frame
•	Converts coordinates:
	•	World → Camera (Cam_0)
	•	Camera → Blender space
•	Animates:
	•	Wrist (armature object location)
	•	MCP / PIP / TIP empties
	•	Keeps IK constraints unchanged

✅ Result:
	•	The hand performs real motion from the dataset
	•	Motion is temporally consistent

⸻

### Step 2 – Render Synthetic Data

Edit the configuration in render.py:
```python
action_label = "wash_sponge"
base_output_dir = "/path/to/render_output"
```python
Then run: render.py
What this script does:
•	Enables Cycles GPU rendering (Metal)
•	Iterates over:
	•	All cameras (Cam_*)
	•	Multiple skin materials (SkinA, SkinB, SkinC)
	•	All animation frames
	•	Renders images with transparent background

Output structure:
render_output/
└── wash_sponge/
    ├── Cam_1/
    │   ├── SkinA/
    │   ├── SkinB/
    │   └── SkinC/
    ├── Cam_2/
    └── ...

### 🧰 Base Scene Setup (Optional)

The following scripts are NOT required when using RENDER.blend.
They are only used when creating a new base scene from scratch.

empty.py
	•	Creates IK target empties (*_TIP, *_PIP)
	•	Places them at REST pose bone tail positions
	•	Saves base positions for reset

camera.py
	•	Generates multiple cameras (Cam_*)
	•	Places cameras on a circular trajectory
	•	Adds TRACK_TO constraint toward the hand

👉 These scripts should be run once during base scene preparation.

⸻

### 📷 Camera Convention
	•	Cam_0: Original first-person camera of the F-PHAB dataset
	•	Cam_1 … Cam_N: Virtual cameras in Blender for synthetic data generation

Hand motion follows the dataset viewpoint (Cam_0), while rendering uses additional cameras.

⸻

### 🎯 Key Features
	•	Skeleton-driven hand motion reconstruction
	•	Inverse kinematics with bending plane stabilization
	•	Multi-view and multi-skin synthetic data generation
	•	Single-scene pipeline (no FBX import/export)
	•	Suitable for hand pose and hand action recognition research

⸻

### 🚧 Known Limitations
	•	Finger overlap may occur in extreme poses
	•	Anatomical accuracy depends on rig–dataset alignment
	•	No physical collision handling between fingers

⸻

### 📌 Notes
	•	All scripts must be run inside Blender
	•	Do not rerun camera.py or empty.py unless resetting the scene
	•	Ensure object names match the scripts (Hand, HandMesh, Cam_*)