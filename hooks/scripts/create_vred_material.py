import os
import time
from pathlib import Path

def load_material(input_path):
    """Load materials from the input path."""

    # Load the materials from the input file path
    materials = vrMaterialService.loadMaterials([input_path])
    material = materials[0] if materials else None

    # Sanity check the material was loaded
    if not material:
        msg = f"No materials found in file {input_path}"
        return (False, None, msg)
    
    return (True, material, None)

def save_material(material, output_path):
    """Save the material to the output path as .osb file."""

    # Ensure the output path exists before calling save material function
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Get the path to save the .osb VRED Material to
    material_name = material.getName()

    output_file_path = os.path.join(
        output_path,
        f"{material_name}.osb",
    )
    if os.path.exists(output_file_path):
        msg = f"Material already exists: {output_file_path}"
        return (False, None, msg)

    # Save the loaded material to a .osb file
    success = vrMaterialService.saveMaterials([material], output_path)
    if not success:
        msg = f"Failed to save material to {output_file_path}"
        return (False, None, msg)
    
    return (True, output_file_path, None)


def create_material_asset(material, output_path):
    """
    Create a VRED Material Asset from the given material.
    """

    # NOTE this requires VRED to have the material assets directory to point to ShotGrid storage

    def __create_material_asset(path):
        # Ensure the Asset Manager knows about the path
        vrAssetsModule.reloadAssetDirectory(os.path.dirname(path))
        success = vrAssetsModule.createMaterialAsset(material_ptr, path)
        if not success:
            # Try one more time by reloading all directories
            vrAssetsModule.reloadAllAssetDirectories()
            success = vrAssetsModule.createMaterialAsset(material_ptr, path)
        return success

    errors = []
    material_name = material.getName()
    material_ptr = findMaterial(material_name)
    material_asset_path = str(Path(output_path).resolve())
    success = __create_material_asset(material_asset_path)
    if not success:
        # First record the error 
        errors.append(f"Attempt failed to save material asset to {material_asset_path}")
        # Try formatting the path ourselves
        # FIXME format this more robustly
        material_asset_path = output_path.replace(os.sep, "/")
        # Ensure the network drive is capitalized (e.g. "Z:/" instead of "z:/")
        material_asset_path = material_asset_path[0].capitalize() + material_asset_path[1:]
        success = __create_material_asset(material_asset_path)

    if not success:
        errors.append(f"Attempt failed to save material asset to {material_asset_path}")
        error = "\n".join(errors)
        return (False, error)

    return (True, None)


def terminate_vred(error=None, sleep=5):
    """Terminate the VRED process. Sleep time before closing to allow chance to view console output."""

    if error:
        print(error)

    time.sleep(sleep)
    vrController.terminateVred()

    if error:
        exit(-1)
    exit(0)


# 
# Python script to generate a VRED Material (.osb) from input material (e.g. X-Rite)
#   - Optional: create render of material
# 
print(f"Running Python script: create_vred_material.py {__name__}")

# Get script params from environment
# NOTE can we pass arguments to Python script when executed with VRED?
input_path = os.environ.get("VRED_MATERIAL_AXF_PATH")
output_path = os.environ.get("VRED_MATERIAL_OSB_PATH")
render_name = os.environ.get("VRED_MATERIAL_RENDER_NAME", "render")
render_path = os.environ.get("VRED_MATERIAL_RENDER_PATH")
render_geometry_path = os.environ.get("VRED_MATERIAL_RENDER_GEOMETRY_PATH")
create_asset = os.environ.get("VRED_MATERIAL_CREATE_ASSET") in ("1", "true", "True")
print(f"Input Material Path: {input_path}")
print(f"Output Material Path: {output_path}")
print(f"Create VRED Asset: {create_asset}")
print(f"Render Name: {render_name}")
print(f"Render Path: {render_path}")
print(f"Render Geometry Path: {render_geometry_path}")

if not input_path:
    # Opened the saved project file?
    raise Exception("Why are we executing this python?")

# Load the materials from the input file path 
success, material, error = load_material(input_path)
if not success:
    terminate_vred(error)
print(f"Loaded material: {material.getName()}")

# Save the material to .osb file (if it is not already an .osb)
if os.path.splitext(os.path.basename(input_path))[1] != ".osb":
    success, output_file_path, error = save_material(material, output_path)
    if not success:
        terminate_vred(error)
    print(f"Saved material: {output_file_path}")

if create_asset:
    success, error = create_material_asset(material, output_path)
    if not success:
        print(error)

# If rendering is not requested, exit here
if not render_path:
    terminate_vred(error)

# 
# Create a VRED rendering of the material applied to some geometry
# 
# FIXME loading a file destroys our current execution scope. For now, we just set up the script again
# 
create_geometry = True
if render_geometry_path:
    # Load geometry from file to apply material to
    success = vrFileIO.load(
        [render_geometry_path],
        vrScenegraph.getRootNode(),
        newFile=True,
        showImportOptions=False,
    )
    # After loading the new file, our scope is gone. Need to reimport and set up again
    import os
    import time
    try:
        from PySide6 import QtGui
    except Exception as e:
        from PySide2 import QtGui
    input_path = os.environ.get("VRED_MATERIAL_AXF_PATH")
    output_path = os.environ.get("VRED_MATERIAL_OSB_PATH")
    render_name = os.environ.get("VRED_MATERIAL_RENDER_NAME", "render")
    render_path = os.environ.get("VRED_MATERIAL_RENDER_PATH")
    render_geometry_path = os.environ.get("VRED_MATERIAL_RENDER_GEOMETRY_PATH")
    create_asset = os.environ.get("VRED_MATERIAL_CREATE_ASSET") in ("1", "true", "True")
    print(f"Input Material Path: {input_path}")
    print(f"Output Material Path: {output_path}")
    print(f"Create VRED Asset: {create_asset}")
    print(f"Render Name: {render_name}")
    print(f"Render Path: {render_path}")
    print(f"Render Geometry Path: {render_geometry_path}")
    materials = vrMaterialService.loadMaterials([input_path])
    material = materials[0] if materials else None
    if not material:
        print(f"Failed to reload material to scene from path {input_path}")

    if success:
        # Need to reload the material to the new scene
        # Get all geometry nodes and apply the material to it
        nodes = vrNodeService.findNodes(lambda node: node.isType(vrdGeometryNode))
        vrMaterialService.applyMaterialToNodes(material, nodes)
        create_geometry = False
    else:
        msg = f"Failed to load geometry from file {render_geometry_path}"

if create_geometry:
    # Create the geometry to apply the material to
    cone = vrNodeUtils.createCone(
        1000.0, 250.0, 25,
        True, True,
        1.0, 1.0, 1.0
    )
    cone = vrNodeService.getNodeFromId(cone.getID())
    cone.applyMaterial(material)

#
# FIXME do a proper turn table
# 
# Get the Perspective Camera to create a track and viewpoints from
persp_cam_node = vrNodeService.findNode("Perspective", root=vrCameraService.getCameraRoot())
persp_cam_node.activate()
# Create the Camera Track to create viewpoints
camera_track_name = "MaterialTrack"
track_node = vrCameraService.createCameraTrack(camera_track_name, cameraNode=persp_cam_node)
# Create initial viewpoint from the current Perspective Camera
view_point0 = vrCameraService.createViewpoint(f"Viewpoint 0", cameraTrack=track_node)
# Rotate the camera .0 around until back to initial position
rotation = persp_cam_node.getRotationAsEuler()
n = 1
increment = 180.0
final_rotation = rotation.y() + increment
while rotation.y() < final_rotation:
    # Rotate the camera
    rotation.setY(rotation.y() + increment)
    persp_cam_node.setWorldRotatePivot(QtGui.QVector3D(0,0,0))
    persp_cam_node.setRotationAsEuler(rotation)
    # Create the viewpoint
    view_point_name = f"Viewpoint {n}"
    vp = vrCameraService.createViewpoint(view_point_name, cameraTrack=track_node)
    vp.setTrackPauseDurationOverride(0.0)
    # Get the next rotation
    rotation = persp_cam_node.getRotationAsEuler()
    n += 1

# Jump to the first viewpoint of the selected track to start camera animation from there,
# otherwise, it will first fly from th current view t the first view point
view_point0.activate(True)
# Configure the track animation settings
# Disable transition for first viewpoint, as we are already there.
view_point0.setTrackTransitionDurationOverride(0.0)
view_point0.setTrackPauseDurationOverride(0.0)
view_point0.setTrackFadeInDurationOverride(0.0)
view_point0.setOverrideTrackSettings(True)
# Time in seconds to fly from one viewpoint to the next
track_node.setTransitionDuration(3.0)
# Time in second the camera stays still at each viewpoint
track_node.setPauseDuration(1.0)
track_node.setFadeInDuration(0.0)

# Get the render folder and file path
render_file_path = os.path.join(
    render_path,
    f"{render_name}.vpb",
)

    ## Save the project file first (for debug)
vrFileIO.save(render_file_path)

# Render setting options
overwrite_files = True
# Render animation images (0) or movie (1)
animation_format = 1
# animation_format = 0

if animation_format == 0:
    render_file_name = os.path.join(
        render_path,
        f"{render_name}.png",
    )
    # For images, width must be 240 for ShotGrid filmstrip thumbnail (aspect ratio HD 16:9)
    vrRenderSettings.setRenderPixelResolution(240, 135, 72)
else:
    render_file_name = os.path.join(
        render_path,
        f"{render_name}.avi",
    )
vrRenderSettings.setRenderView(camera_track_name)
vrRenderSettings.setRenderFilename(render_file_name)
vrRenderSettings.setRenderAnimationFormat(animation_format)
vrRenderSettings.setRenderAnimation(True)
vrRenderSettings.startRenderToFile(overwrite_files)

vrController.terminateVred()
exit(0)
