import os
import subprocess
import sys

def build():
    """
    Builds the Desktop Cleaner application into a single executable using PyInstaller.
    """
    print("Starting build process...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define build command
    # --noconsole: Don't show terminal window
    # --onefile: Bundle into a single EXE
    # --add-data: Include categories.json and assets
    # --name: Executable name
    # --icon: Icon for the EXE
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--add-data", f"src{os.pathsep}src", # Include entire src for safety or specifically files
        "--add-data", f"src/categories.json{os.pathsep}src",
        "--name", "DesktopCleanerHUD",
        "--icon", "src/assets/logo.png" if os.path.exists("src/assets/logo.png") else "NONE",
        "main.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful! The executable can be found in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code: {e.returncode}")

if __name__ == "__main__":
    build()
