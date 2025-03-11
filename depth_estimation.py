import cv2
import numpy as np
from openvino.runtime import Core
import os
import time

# Initialize OpenVINO model
core = Core()
model_path = "openvino_midas_v21_small_256.xml"
compiled_model = core.compile_model(model_path, "CPU")


def estimate_depth(image_path):
    """Estimate depth from an image."""
    try:
        original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        original_size = (original_image.shape[1], original_image.shape[0])

        # Resize for model input
        input_image = cv2.resize(original_image, (256, 256))
        input_image = input_image.astype(np.float32) / 255.0
        input_image = input_image.transpose(2, 0, 1)  # Convert to (C, H, W)
        input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension

        print("🚀 Running inference...")
        start_time = time.time()

        # Run inference
        results = compiled_model.infer_new_request({compiled_model.inputs[0]: input_image})
        depth_map = list(results.values())[0]  # Extract depth map
        depth_map = np.squeeze(depth_map)  # Remove extra dimensions

        # Resize back to original size
        depth_map_resized = cv2.resize(depth_map, original_size, interpolation=cv2.INTER_CUBIC)

        # Normalize for better visualization
        depth_map_resized = (depth_map_resized - depth_map_resized.min()) / (depth_map_resized.max() - depth_map_resized.min())

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        print(f"✅ Depth map generated in {processing_time} seconds")

        return depth_map_resized

    except Exception as e:
        print(f"❌ Error in depth estimation: {e}")
        return None


def save_depth_map(depth_map, output_path):
    """Save the depth map in PNG or JPEG format."""
    ext = os.path.splitext(output_path)[-1].lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        cv2.imwrite(output_path, (depth_map * 255).astype(np.uint8))
        print(f"✅ Depth map saved: {output_path}")
    else:
        print(f"❌ Unsupported format: {ext}")
