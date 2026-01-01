import os
import subprocess
import sys
import yaml


def get_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.yaml"
    )
    if not os.path.exists(config_path):
        print(
            "Error: config.yaml not found. Please copy config.template.yaml to config.yaml and configure it."
        )
        sys.exit(1)

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_manifest_version():
    """Read version from blender_manifest.toml"""
    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "addon",
        "scripting_nodes",
        "blender_manifest.toml",
    )

    with open(manifest_path, "r") as f:
        for line in f:
            if line.startswith("version"):
                # Parse version = "x.y.z"
                version = line.split("=")[1].strip().strip('"')
                return version
    return None


def update_manifest_version(version: str):
    """Update version in blender_manifest.toml"""
    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "addon",
        "scripting_nodes",
        "blender_manifest.toml",
    )

    with open(manifest_path, "r") as f:
        content = f.read()

    # Replace the version line
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("version"):
            lines[i] = f'version = "{version}"'
            break

    with open(manifest_path, "w") as f:
        f.write("\n".join(lines))


def build(version: str = None):
    """Build the extension using Blender's extension build command"""
    config = get_config()
    blender_executable = config.get("BLENDER_EXECUTABLE")

    if not blender_executable or not os.path.exists(blender_executable):
        print("Error: BLENDER_EXECUTABLE not found or not configured in config.yaml")
        sys.exit(1)

    # Update manifest version if provided
    if version:
        update_manifest_version(version)
        print(f"Updated manifest version to {version}")
    else:
        version = get_manifest_version()
        print(f"Using existing manifest version: {version}")

    # Paths
    repo_root = os.path.dirname(os.path.dirname(__file__))
    source_dir = os.path.join(repo_root, "addon", "scripting_nodes")
    builds_dir = os.path.join(repo_root, "builds")

    # Create builds directory if it doesn't exist
    if not os.path.exists(builds_dir):
        os.makedirs(builds_dir)

    # Build command using Blender's extension build
    cmd = [
        blender_executable,
        "--command",
        "extension",
        "build",
        "--source-dir",
        source_dir,
        "--output-dir",
        builds_dir,
        "--verbose",
    ]

    print(f"Building extension from: {source_dir}")
    print(f"Output directory: {builds_dir}")
    print(f"Running: {' '.join(cmd)}")
    print()

    # Run the build command
    result = subprocess.run(cmd, cwd=repo_root)

    if result.returncode == 0:
        output_file = os.path.join(builds_dir, f"scripting_nodes-{version}.zip")
        print()
        print(f"Build successful!")
        print(f"Output: {output_file}")
    else:
        print()
        print(f"Build failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def validate():
    """Validate the extension manifest using Blender"""
    config = get_config()
    blender_executable = config.get("BLENDER_EXECUTABLE")

    if not blender_executable or not os.path.exists(blender_executable):
        print("Error: BLENDER_EXECUTABLE not found or not configured in config.yaml")
        sys.exit(1)

    source_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "addon", "scripting_nodes"
    )

    cmd = [
        blender_executable,
        "--command",
        "extension",
        "validate",
    ]

    print(f"Validating extension manifest...")
    result = subprocess.run(cmd, cwd=source_dir)

    if result.returncode == 0:
        print("Validation successful!")
    else:
        print(f"Validation failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build Scripting Nodes extension")
    parser.add_argument(
        "--version",
        "-v",
        type=str,
        help="Version to set in the manifest (e.g., 4.0.1). If not provided, uses existing manifest version.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the manifest without building",
    )

    args = parser.parse_args()

    if args.validate_only:
        validate()
    else:
        # If no version argument, prompt interactively
        version = args.version
        if not version and sys.stdin.isatty():
            current_version = get_manifest_version()
            version = input(f"Build Version [{current_version}]: ").strip()
            if not version:
                version = None  # Use existing version

        build(version)
