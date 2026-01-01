import yaml
import subprocess
import os
import psutil
import colorama
import shutil
from threading import Thread
import time
import sys
import tempfile


class BlenderLauncher:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.validate_paths()
        self.files_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "addon", "scripting_nodes"
        )
        self.repo_root = os.path.dirname(os.path.dirname(__file__))

    def _load_config(self, path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def validate_paths(self):
        """Validate the paths from config exist."""
        if not os.path.exists(self.config["BLENDER_EXECUTABLE"]):
            raise FileNotFoundError(
                f"BLENDER_EXECUTABLE does not exist: {self.config['BLENDER_EXECUTABLE']}. Check your config.yaml."
            )

    def _stream_output(self, pipe, prefix, color):
        """Stream output from a pipe with a specified color."""
        for line in iter(pipe.readline, ""):
            print(color + f"[{prefix}] {line.strip()}")
            sys.stdout.flush()
        pipe.close()

    def build_extension(self):
        """Build the extension zip using Blender's extension build command."""
        # Create a temp directory for the build
        build_dir = os.path.join(self.repo_root, ".dev_build")
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.makedirs(build_dir)

        # Build the extension
        cmd = [
            self.config["BLENDER_EXECUTABLE"],
            "--command",
            "extension",
            "build",
            "--source-dir",
            self.files_path,
            "--output-dir",
            build_dir,
        ]

        print(colorama.Fore.CYAN + "Building extension...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(colorama.Fore.RED + f"Build failed: {result.stderr}")
            return None

        # Find the built zip file
        for file in os.listdir(build_dir):
            if file.endswith(".zip"):
                zip_path = os.path.join(build_dir, file)
                print(colorama.Fore.GREEN + f"Built: {zip_path}")
                return zip_path

        return None

    def install_extension(self, zip_path):
        """Install the extension using Blender's install-file command."""
        # First try to remove any existing installation
        remove_cmd = [
            self.config["BLENDER_EXECUTABLE"],
            "--command",
            "extension",
            "remove",
            "--no-prefs",
            "scripting_nodes",
        ]
        subprocess.run(remove_cmd, capture_output=True, text=True)

        # Install the new version (without -e flag, enable manually in Blender preferences)
        install_cmd = [
            self.config["BLENDER_EXECUTABLE"],
            "--command",
            "extension",
            "install-file",
            "-r",
            "user_default",
            zip_path,
        ]

        print(colorama.Fore.CYAN + "Installing extension...")
        result = subprocess.run(install_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(colorama.Fore.RED + f"Install failed: {result.stderr}")
            print(colorama.Fore.RED + f"Output: {result.stdout}")
            return False

        print(
            colorama.Fore.GREEN
            + "Extension installed! Enable it in Blender Preferences > Add-ons if needed."
        )
        return True

    def sync_files(self):
        """Build and install the extension properly."""
        zip_path = self.build_extension()
        if zip_path:
            return self.install_extension(zip_path)
        return False

    def launch_blender(self):
        """Launch Blender with proper environment and output handling."""
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        proc = subprocess.Popen(
            [self.config["BLENDER_EXECUTABLE"], "--python-use-system-env"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            env=env,
            universal_newlines=True,
            bufsize=1,
        )

        # Start output threads
        Thread(
            target=self._stream_output,
            args=(proc.stdout, "BLENDER", colorama.Fore.MAGENTA),
            daemon=True,
        ).start()
        Thread(
            target=self._stream_output,
            args=(proc.stderr, "BLENDER ERROR", colorama.Fore.RED),
            daemon=True,
        ).start()

        return proc

    def quit_blender(self):
        """Terminate any running Blender instances."""
        exe_name = os.path.split(self.config["BLENDER_EXECUTABLE"])[1]
        for proc in psutil.process_iter(["pid", "name"]):
            if exe_name in proc.info["name"].lower():
                proc.terminate()
                proc.wait()
                break

    def check_input(self):
        """Check for user input without blocking."""
        if os.name == "nt":
            import msvcrt

            return msvcrt.getch().decode() if msvcrt.kbhit() else None
        else:
            import select

            if select.select([sys.stdin], [], [], 0.0)[0]:
                return sys.stdin.read(1)
        return None

    def run(self):
        """Main run loop."""
        colorama.init(autoreset=True)

        try:
            while True:
                if not self.sync_files():
                    print(colorama.Fore.RED + "Failed to sync extension. Retrying...")
                    time.sleep(2)
                    continue

                self.launch_blender()
                print(
                    colorama.Fore.GREEN + "Press 'r' to restart Blender or 'q' to quit."
                )

                while True:
                    key = self.check_input()
                    if key:
                        if key.lower() == "r":
                            print(colorama.Fore.GREEN + "Relaunching Blender...")
                            self.quit_blender()
                            break
                        elif key.lower() == "q":
                            print(colorama.Fore.GREEN + "Exiting...")
                            self.quit_blender()
                            return
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print(colorama.Fore.GREEN + "\nExiting...")
            self.quit_blender()


if __name__ == "__main__":
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.yaml"
    )
    launcher = BlenderLauncher(config_path)
    launcher.run()
