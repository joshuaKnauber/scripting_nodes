import yaml
import subprocess
import os
import psutil
import colorama
import shutil
from threading import Thread
import time
import sys


class BlenderLauncher:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.validate_paths()
        self.files_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "addon", "scripting_nodes"
        )

    def _load_config(self, path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def validate_paths(self):
        """Validate the paths from config exist."""
        for key, path in [
            ("ADDONS_PATH", self.config["ADDONS_PATH"]),
            ("BLENDER_EXECUTABLE", self.config["BLENDER_EXECUTABLE"]),
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Path for {key} does not exist: {path}. Check your config.yaml."
                )

    def _stream_output(self, pipe, prefix, color):
        """Stream output from a pipe with a specified color."""
        for line in iter(pipe.readline, ""):
            print(color + f"[{prefix}] {line.strip()}")
            sys.stdout.flush()
        pipe.close()

    def sync_files(self):
        """Sync addon files to Blender addons directory."""
        target_dir = os.path.join(self.config["ADDONS_PATH"], "scripting_nodes")
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(self.files_path, target_dir)
        print(colorama.Fore.GREEN + f"Synced files to {target_dir}")

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
                self.sync_files()
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
