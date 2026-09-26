import os
import sys
import subprocess
import shutil
from PIL import Image

def convert_icon():
    print("\n--- [STEP 1] Generating high-quality sweeply_icon.ico ---")
    src = os.path.join("images", "sweply_circle.webp")
    if os.path.exists(src):
        try:
            img = Image.open(src)
            # Crop to bounding box to remove transparent whitespace padding
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Save as ICO with standard multi-resolution sizes
            img.save("sweeply_icon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            print("Successfully created sweeply_icon.ico")
            return "sweeply_icon.ico"
        except Exception as e:
            print(f"Error converting icon: {e}")
    else:
        print("Warning: images/sweply_circle.webp not found. Proceeding without custom icon.")
    return "NONE"

def install_deps(python_exe):
    print(f"\n--- Installing dependencies for: {python_exe} ---")
    try:
        # Upgrade pip
        subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        # Install package dependencies
        deps = ["pyinstaller", "Pillow", "pystray", "uiautomation", "pywin32", "comtypes"]
        subprocess.check_call([python_exe, "-m", "pip", "install"] + deps)
        print("Dependencies installed successfully.")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        raise e

def build_exe(python_exe, suffix, icon_path):
    print(f"\n--- [STEP 2] Compiling Executable ({suffix}) ---")
    exe_name = f"DesktopCleanerHUD_{suffix}"
    
    # Clean up previous build directories for this target
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"Cleaned directory: {folder}")
            except Exception as e:
                print(f"Warning: Could not remove directory {folder}: {e}")
                
    cmd = [
        python_exe, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        # Bundle core files, custom categories database, images, and splash screens inside the single EXE
        "--add-data", f"src{os.pathsep}src",
        "--add-data", f"src/categories.json{os.pathsep}src",
        "--add-data", f"images{os.pathsep}images",
        "--add-data", f"splash3.webp{os.pathsep}.",
        "--add-data", f"best2.webp{os.pathsep}.",
        "--name", exe_name,
    ]
    if icon_path != "NONE":
        cmd += ["--icon", icon_path]
        
    cmd += ["main.py"]
    
    print(f"Running PyInstaller command:\n{' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    built_path = os.path.join("dist", f"{exe_name}.exe")
    if os.path.exists(built_path):
        os.makedirs("releases", exist_ok=True)
        dest_path = os.path.join("releases", f"{exe_name}.exe")
        shutil.copy(built_path, dest_path)
        print(f"SUCCESS: Executable built at: {dest_path}")
        return dest_path
    else:
        raise Exception(f"Failed to build executable {exe_name}.exe")

def generate_iss(suffix, exe_path, icon_path):
    print(f"\n--- [STEP 3] Generating Inno Setup Script ({suffix}) ---")
    iss_content = f"""; Script generated programmatically by Sweeply Builder
[Setup]
AppId={{{{3B2C6D1F-7A9B-4D1C-8E2F-0C4B5D6E7F8A}}}}
AppName=Sweeply Desktop Cleaner
AppVersion=1.0b
AppPublisher=VirtuArch
AppPublisherURL=https://github.com/Devilynpl/Sweeply
AppSupportURL=https://github.com/Devilynpl/Sweeply
AppUpdatesURL=https://github.com/Devilynpl/Sweeply
DefaultDirName={{autopf}}\\Sweeply
DefaultGroupName=Sweeply
DisableProgramGroupPage=yes
OutputDir=releases
OutputBaseFilename=Sweeply_Setup_{suffix}
SetupIconFile={icon_path}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
"""
    if suffix == "x64":
        iss_content += """ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
"""
    else:
        iss_content += """ArchitecturesAllowed=x86 x64
"""

    iss_content += f"""
[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{{{cm:CreateDesktopIcon}}}}"; GroupDescription: "{{{{cm:AdditionalIcons}}}}"; Flags: unchecked

[Files]
Source: "{exe_path}"; DestDir: "{{app}}"; DestName: "Sweeply.exe"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\Sweeply"; Filename: "{{app}}\\Sweeply.exe"
Name: "{{group}}\\Uninstall Sweeply"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\Sweeply"; Filename: "{{app}}\\Sweeply.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\Sweeply.exe"; Description: "{{{{cm:LaunchProgram,Sweeply}}}}"; Flags: nowait postinstall skipifsilent
"""
    
    iss_file = f"setup_{suffix}.iss"
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_content)
    print(f"Inno Setup script saved to: {iss_file}")
    return iss_file

def compile_installer(iscc_path, iss_file):
    print(f"\n--- [STEP 4] Compiling Windows Setup Installer via Inno Setup ---")
    cmd = [iscc_path, iss_file]
    print(f"Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print(f"SUCCESS: Setup Installer created successfully from {iss_file}")

def main():
    PYTHON_64 = sys.executable  # Current Python interpreter (64-bit)
    PYTHON_32 = r"C:\Users\rakpa\AppData\Local\Programs\Python\Python311-32\python.exe"
    ISCC = r"C:\Users\rakpa\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    
    # 1. Convert WebP logo to Windows ICO format
    icon_path = convert_icon()
    
    # 2. Build 64-bit Executable
    install_deps(PYTHON_64)
    exe_64 = build_exe(PYTHON_64, "x64", icon_path)
    
    # 3. Build 32-bit Executable
    if os.path.exists(PYTHON_32):
        install_deps(PYTHON_32)
        exe_32 = build_exe(PYTHON_32, "x86", icon_path)
    else:
        print("\nWarning: 32-bit Python environment not found. Skipping 32-bit executable compilation.")
        exe_32 = None
        
    # 4. Generate Setup Installers
    if os.path.exists(ISCC):
        # Build 64-bit installer
        iss_64 = generate_iss("x64", exe_64, icon_path)
        compile_installer(ISCC, iss_64)
        
        # Build 32-bit installer
        if exe_32:
            iss_32 = generate_iss("x86", exe_32, icon_path)
            compile_installer(ISCC, iss_32)
    else:
        print(f"\nWarning: Inno Setup compiler not found at {ISCC}. Installer compilation skipped.")

if __name__ == "__main__":
    main()
