import os
import shutil
from src.core import Cleaner, UndoManager

def test_real_undo():
    # Setup temp environment
    base_dir = os.path.abspath("temp_test_undo")
    desktop = os.path.join(base_dir, "Desktop")
    clean_dir = os.path.join(desktop, "CLEAN")
    
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(desktop)
    
    # Create a dummy file
    test_file = os.path.join(desktop, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("content")
        
    print(f"Created {test_file}")
    
    # Initialize Cleaner manually to point dependencies
    cleaner = Cleaner()
    cleaner.desktop_path = desktop
    cleaner.clean_folder_path = clean_dir
    
    undo_manager = UndoManager()
    
    # Perform clean
    print("Cleaning...")
    files = cleaner.scan_desktop()
    print(f"Found: {files}")
    
    moved, errors = cleaner.organize_files(files, dry_run=False)
    if errors:
        print(f"Clean Errors: {errors}")
        return

    print(f"Moved: {moved}")
    undo_manager.push_history(moved)
    
    # Validate move
    dst_file = moved[0][1]
    
    # SIMULATE LOCK: Open file at destination and keep handle
    print("Simulating file lock at destination...")
    locked_file = open(dst_file, "r")
    
    # Perform Undo
    print("Undoing...")
    success, undo_errors = undo_manager.undo_last()
    
    locked_file.close() # Cleanup


    
    if undo_errors:
        print(f"Undo Failed with errors: {undo_errors}")
        if not undo_manager.has_history():
            print("CRITICAL FAIL: History lost after failed undo!")
        else:
            print("History preserved (Good).")
    else:
        print(f"Undo Successful. Count: {success}")
        if os.path.exists(test_file):
            print("Verified: File is back on desktop.")
        else:
            print("FAIL: File not found on desktop.")


    # Cleanup
    # shutil.rmtree(base_dir)

if __name__ == "__main__":
    test_real_undo()
