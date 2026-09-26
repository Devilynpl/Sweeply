import os
import shutil
from src.core import Cleaner

def restore_files():
    cleaner = Cleaner()
    clean_dir = cleaner.clean_folder_path
    desktop = cleaner.desktop_path
    
    if not os.path.exists(clean_dir):
        print(f"No CLEAN folder found at {clean_dir}")
        return

    print(f"Restoring files from {clean_dir} to {desktop}...")
    
    count = 0
    # Walk through all subdirectories in CLEAN
    for root, dirs, files in os.walk(clean_dir):
        for file in files:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(desktop, file)
            
            # Crash protection: Don't overwrite if file exists on desktop (e.g. user created new one)
            if os.path.exists(dst_path):
                print(f"Skipping {file}: Exists on Desktop.")
                continue
                
            try:
                shutil.move(src_path, dst_path)
                print(f"Restored: {file}")
                count += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")
                
    print(f"Recovery complete. Restored {count} files.")
    
    # Optional: Remove empty folders in CLEAN? 
    # Let's leave them for safety or manually delete.

if __name__ == "__main__":
    restore_files()
