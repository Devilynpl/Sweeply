import os
import shutil
import platform
import logging
import ctypes
import json
from datetime import datetime
from .utils import get_category

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("sweeply.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class UndoManager:
    def __init__(self):
        self.history = []  # Stack of list of moves [(src, dst), ...]

    def push_history(self, moves):
        """
        moves: list of tuples (original_path, new_path)
        """
        if moves:
            self.history.append(moves)

    def has_history(self):
        return len(self.history) > 0

    def undo_last(self):
        """
        Reverses the last batch of moves.
        Returns: (success_count, errors_list)
        """
        if not self.history:
            return 0, ["No history to undo."]

        last_moves = self.history.pop() # LIFO
        success_count = 0
        errors = []
        failed_moves = []

        # Reverse order isn't strictly necessary for safe moves but good practice if renaming chain happened
        for original_src, current_dst in reversed(last_moves):
            try:
                if os.path.exists(current_dst):
                    # Move back from current_dst to original_src
                    # Ensure parent of original_src exists (unlikely to be deleted but good safety)
                    os.makedirs(os.path.dirname(original_src), exist_ok=True)
                    shutil.move(current_dst, original_src)
                    success_count += 1
                else:
                    errors.append(f"File not found: {current_dst}")
                    # If file not found, we can't really retry moving it unless it reappears.
                    # But assuming ephemeral error, maybe push back? 
                    # If it's truly gone, pushing back is annoying.
                    # Decision: Do NOT push back "File not found". Only push back "Failed to undo" (locked etc).
            except Exception as e:
                errors.append(f"Failed to undo {current_dst}: {str(e)}")
                failed_moves.append((original_src, current_dst))
        
        if failed_moves:
            # We must restore failed moves to the top of the stack.
            # Since we processed in reversed order (C, B, A), failed_moves is in undo order.
            # When we push it back, next undo will again call reversed(), restoring original Undo Order.
            # Example: original [A, B, C]. Undo loop: C, B, A. 
            # If B, A fail, failed_moves = [B, A].
            # Next undo: reversed([B, A]) -> A, B. 
            # This is NOT the original undo order (C, B, A).
            # To get [B, A] as undo order next time, we need to push [A, B].
            self.history.append(list(reversed(failed_moves)))
            
        return success_count, errors


class Cleaner:
    def __init__(self):
        self.desktop_path = self._get_desktop_path()

        # Default destination: Desktop\Sweeply\
        # Overridden by last-used path stored in config.
        default_clean_folder = os.path.join(self.desktop_path, "Sweeply")

        # System files to ignore
        self.base_ignore_files = {
            "desktop.ini", "thumbs.db", ".ds_store",
            "icon\r", ".localized"
        }
        self.ignore_files = self.base_ignore_files.copy()

        # Hardware-Aware Configuration Layer
        self.config_path = os.path.join(os.path.expanduser("~"), ".sweeply_cfg.json")
        self.config = self._load_config()

        # Restore last-used clean folder or fall back to default
        saved_folder = self.config.get("clean_folder_path", "")
        if saved_folder and os.path.isabs(saved_folder):
            self.clean_folder_path = saved_folder
        else:
            self.clean_folder_path = default_clean_folder
            self.config["clean_folder_path"] = self.clean_folder_path

        if "ignored_items" not in self.config:
            self.config["ignored_items"] = []
        for item in self.config["ignored_items"]:
            self.ignore_files.add(item.lower())

        if self.config.get("first_run", True):
            self.config["max_capacity"] = self.calculate_capacity()
            self.config["first_run"] = False
            self._save_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"first_run": True, "max_capacity": 60, "dated_folders": False, "skip_folders": False}

    def _save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except:
            pass

    def set_dated_folders(self, enabled):
        """
        Enables or disables dated subfolders (YYYY-MM-DD).
        """
        self.config["dated_folders"] = enabled
        self._save_config()

    def set_skip_folders(self, enabled):
        """
        Enables or disables skipping folders.
        """
        self.config["skip_folders"] = enabled
        self._save_config()

    def calculate_capacity(self):
        """Measures hardware and calculates icon grid density."""
        try:
            if platform.system() == "Windows":
                # Use getattr to satisfy linters on non-Windows platforms
                user32_lib = getattr(ctypes, 'windll', None)
                if user32_lib:
                    user32 = user32_lib.user32
                    w = user32.GetSystemMetrics(78) # SM_CXVIRTUALSCREEN
                    h = user32.GetSystemMetrics(79) # SM_CYVIRTUALSCREEN
                    # Heuristic: Tactical grid 110x120px per icon cluster
                    return (w // 110) * (h // 120)
            return 60
        except:
            return 60

    def get_current_load(self):
        """Returns (current_count, max_capacity, percentage)"""
        files = self.scan_desktop()
        folders = self.scan_desktop_folders()
        current = len(files) + len(folders)
        max_cap = self.config.get("max_capacity", 60)
        percent = (current / max_cap) * 100 if max_cap > 0 else 0
        return current, max_cap, percent

    def set_exclusions(self, extensions):
        """
        Updates the ignore list with additional extensions.
        extensions: list of strings (e.g., [".lnk", ".ico"])
        """
        self.ignore_files = self.base_ignore_files.copy()
        for ext in extensions:
            self.ignore_files.add(ext.lower())
        for item in self.config.get("ignored_items", []):
            self.ignore_files.add(item.lower())

    def _get_desktop_path(self):
        """Cross-platform desktop path detection."""
        # Standard expansion
        path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Check if it actually exists, otherwise fallback to home (unlikely but safe)
        if not os.path.exists(path):
             return os.path.expanduser("~")
        return path

    def _is_ignored(self, name):
        """Checks if a file or folder matches any ignore patterns/extensions."""
        import fnmatch
        name_lower = name.lower()
        _, ext = os.path.splitext(name)
        ext_lower = ext.lower()
        
        for pattern in self.ignore_files:
            pattern_lower = pattern.lower()
            # Direct match or extension match
            if pattern_lower.startswith(".") and ext_lower == pattern_lower:
                return True
            # Glob match
            if fnmatch.fnmatch(name_lower, pattern_lower):
                return True
        return False

    def scan_desktop(self):
        """
        Scans desktop for files to be moved.
        Returns list of filenames.
        """
        # Derive the folder name to skip dynamically so it works for any destination
        clean_folder_name = os.path.basename(self.clean_folder_path)
        files_to_move = []
        try:
            with os.scandir(self.desktop_path) as entries:
                for entry in entries:
                    if entry.name.startswith("."):  # Ignore hidden files
                        continue
                    if entry.name == clean_folder_name:  # Ignore our own folder
                        continue
                    if self._is_ignored(entry.name):
                        continue

                    if entry.is_file():
                        try:
                            size = entry.stat().st_size
                        except:
                            size = 0
                        files_to_move.append((entry.name, size))
        except OSError as e:
            logging.error(f"Error scanning desktop: {e}")
            return []

        return files_to_move

    def scan_desktop_folders(self):
        """
        Scans desktop for folders to be moved.
        Returns list of (foldername, size).
        """
        if self.config.get("skip_folders", False):
            return []
        clean_folder_name = os.path.basename(self.clean_folder_path)
        folders_to_move = []
        try:
            with os.scandir(self.desktop_path) as entries:
                for entry in entries:
                    if entry.name == clean_folder_name:
                        continue
                    if entry.name.startswith("."):
                        continue
                    if self._is_ignored(entry.name):
                        continue

                    if entry.is_dir():
                        size = 0
                        try:
                            for dirpath, dirnames, filenames in os.walk(entry.path):
                                for f in filenames:
                                    fp = os.path.join(dirpath, f)
                                    if not os.path.islink(fp):
                                        size += os.path.getsize(fp)
                        except:
                            pass
                        folders_to_move.append((entry.name, size))
        except OSError as e:
            logging.error(f"Error scanning desktop folders: {e}")
            return []

        return folders_to_move

    def organize_files(self, files, dry_run=False):
        """
        Organizes the given list of filenames.
        If dry_run=True, returns list of (filename, category_name).
        If dry_run=False, returns (moved_list_tuples, error_list) and performs moves.
        """
        preview_results = []
        moved_files = [] # Stores (src, dst) for undo history
        errors = []
        
        dated_subfolder = ""
        if self.config.get("dated_folders", False):
            dated_subfolder = datetime.now().strftime("%Y-%m-%d")

        for filename in files:
            src_path = os.path.join(self.desktop_path, filename)
            _, ext = os.path.splitext(filename)
            category = get_category(ext)
            
            if dry_run:
                preview_results.append((filename, category))
                continue

            # Execution Logic
            try:
                target_dir = os.path.join(self.clean_folder_path, category)
                if dated_subfolder:
                    target_dir = os.path.join(target_dir, dated_subfolder)
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                dst_path = os.path.join(target_dir, filename)
                
                # Check for name collision
                if os.path.exists(dst_path):
                     base, extension = os.path.splitext(filename)
                     counter = 1
                     while os.path.exists(dst_path):
                         new_name = f"{base}_{counter}{extension}"
                         dst_path = os.path.join(target_dir, new_name)
                         counter += 1
                
                logging.info(f"Moving file: {src_path} -> {dst_path}")
                shutil.move(src_path, dst_path)
                moved_files.append((src_path, dst_path))
                preview_results.append((filename, category)) # reuse list for success report
                
            except Exception as e:
                err_msg = f"Error moving {filename}: {str(e)}"
                logging.error(err_msg)
                errors.append(err_msg)
        
        if dry_run:
            return preview_results
        
        return moved_files, errors

    def organize_folders(self, folders, dry_run=False):
        """
        Organizes the given list of folder names into CLEAN/@FOLDERS.
        """
        folders_category = "@FOLDERS"
        preview_results = []
        moved_files = []
        errors = []
        
        target_dir = os.path.join(self.clean_folder_path, folders_category)
        
        dated_subfolder = ""
        if self.config.get("dated_folders", False):
            dated_subfolder = datetime.now().strftime("%Y-%m-%d")
            target_dir = os.path.join(target_dir, dated_subfolder)

        for folder_name in folders:
            src_path = os.path.join(self.desktop_path, folder_name)
            
            if dry_run:
                preview_results.append((folder_name, folders_category))
                continue
            
            try:
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                dst_path = os.path.join(target_dir, folder_name)
                
                # Collision handling for folders
                if os.path.exists(dst_path):
                     counter = 1
                     while os.path.exists(dst_path):
                         new_name = f"{folder_name}_{counter}"
                         dst_path = os.path.join(target_dir, new_name)
                         counter += 1

                logging.info(f"Moving folder: {src_path} -> {dst_path}")
                shutil.move(src_path, dst_path)
                moved_files.append((src_path, dst_path))
            
            except Exception as e:
                err_msg = f"Error moving folder {folder_name}: {str(e)}"
                logging.error(err_msg)
                errors.append(err_msg)
        
        if dry_run:
            return preview_results
            
        return moved_files, errors
