import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from pupil_labs.neon_usb import IMU


def quaternion_to_rotation_matrix(q):
    """Convert quaternion to rotation matrix."""
    # Handle Quaternion object with x, y, z, w attributes
    if hasattr(q, "x") and hasattr(q, "y") and hasattr(q, "z") and hasattr(q, "w"):
        x, y, z, w = q.x, q.y, q.z, q.w
    elif len(q) == 4:
        w, x, y, z = q
    else:
        raise ValueError(f"Expected quaternion with 4 elements, got {len(q)}")

    # Normalize quaternion
    norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
    if norm == 0:
        return np.eye(3)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

    # Calculate rotation matrix
    R = np.array([
        [1 - 2 * (y**2 + z**2), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x**2 + z**2), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x**2 + y**2)],
    ])

    return R


def main():
    # Initialize IMU
    imu = IMU()

    # Set up the figure and 3D axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Create device axes
    device_axes = {
        "x": np.array([[0, 2], [0, 0], [0, 0]]),
        "y": np.array([[0, 0], [0, 2], [0, 0]]),
        "z": np.array([[0, 0], [0, 0], [0, 2]]),
    }

    # Set up the plot
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_zlim([-5, 5])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Orientation Visualization")

    # reference axes
    ax.plot([0, 3], [0, 0], [0, 0], "r-", alpha=0.3, linewidth=1)
    ax.plot([0, 0], [0, 3], [0, 0], "g-", alpha=0.3, linewidth=1)
    ax.plot([0, 0], [0, 0], [0, 3], "b-", alpha=0.3, linewidth=1)

    # device axes
    device_lines = {}
    colors = {"x": "red", "y": "green", "z": "blue"}
    for axis_name, axis_coords in device_axes.items():
        (line,) = ax.plot(*axis_coords, color=colors[axis_name], linewidth=3, alpha=1.0)
        device_lines[axis_name] = line

    def update(frame):
        # Get IMU data
        try:
            imu_datum = imu.get_imu_data()
            quaternion = imu_datum.quaternion

            # Convert quaternion to rotation matrix
            R = quaternion_to_rotation_matrix(quaternion)

            # Update existing device axes lines instead of recreating them
            for axis_name, axis_coords in device_axes.items():
                # axis_coords has shape (3, 2), transpose to (2, 3) for rotation
                rotated_axis = (axis_coords.T @ R.T).T
                device_lines[axis_name].set_data_3d(*rotated_axis)

        except Exception as e:
            print(f"Error reading IMU data: {e}")

    # Create animation
    _ = FuncAnimation(fig, update, interval=10, blit=False)

    plt.show()


if __name__ == "__main__":
    main()
