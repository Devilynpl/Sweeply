import pytest
import tkinter as tk
from unittest.mock import patch
from src.gui import DesktopCleanerApp

def test_gui_startup():
    try:
        app = DesktopCleanerApp()
        app.update()
        app.destroy()
    except tk.TclError:
        pytest.skip("No display available for GUI test")

def test_gui_variables_and_handlers():
    try:
        app = DesktopCleanerApp()
    except tk.TclError:
        pytest.skip("No display available for GUI test")
        
    try:
        # Check initialization defaults
        assert app.var_skip_folders.get() == app.cleaner.config.get("skip_folders", False)
        assert app.var_exclude_lnk.get() is True
        
        # Test change handler updates cleaner state
        app.var_skip_folders.set(True)
        app.apply_skip_folders_settings()
        assert app.cleaner.config.get("skip_folders") is True
        
        app.var_skip_folders.set(False)
        app.apply_skip_folders_settings()
        assert app.cleaner.config.get("skip_folders") is False

        # Test exclusions handler
        app.var_exclude_lnk.set(False)
        app.apply_exclusions()
        assert ".lnk" not in app.cleaner.ignore_files

        app.var_exclude_lnk.set(True)
        app.apply_exclusions()
        assert ".lnk" in app.cleaner.ignore_files

    finally:
        app.destroy()

def test_gui_minimize_handler():
    try:
        app = DesktopCleanerApp()
    except tk.TclError:
        pytest.skip("No display available for GUI test")

    try:
        # Create a mock event representing unmap on minimize
        event = tk.Event()
        event.widget = app
        
        # Set state to iconic to simulate minimize, patch create_tray_icon to avoid real thread
        with patch.object(app, 'create_tray_icon') as mock_create:
            app.state("iconic")
            app.on_minimize(event)
            # Once minimized, it should withdraw (hide from taskbar)
            assert app.state() == "withdrawn"
            mock_create.assert_called_once()
    finally:
        app.destroy()

def test_gui_search_filter():
    try:
        app = DesktopCleanerApp()
        app.start_main_app()
    except tk.TclError:
        pytest.skip("No display available for GUI test")
        
    try:
        # Populate dummy scan results
        app.scan_results = [
            ("test_file_alpha.txt", 1024, "FILE", "TEXT"),
            ("test_file_beta.png", 2048, "FILE", "IMAGES")
        ]
        
        # Filter with 'alpha'
        app.var_search.set("alpha")
        app._trigger_filter()
        content = app.console.get(1.0, tk.END)
        assert "test_file_alpha.txt" in content
        assert "test_file_beta.png" not in content
        
        # Filter with 'beta'
        app.var_search.set("beta")
        app._trigger_filter()
        content = app.console.get(1.0, tk.END)
        assert "test_file_alpha.txt" not in content
        assert "test_file_beta.png" in content
    finally:
        app.destroy()

def test_glow_button_state_change():
    try:
        app = tk.Tk()
    except tk.TclError:
        pytest.skip("No display available for GUI test")
        
    try:
        from src.ui.widgets import GlowButton
        btn = GlowButton(app, text="TEST BUTTON")
        assert btn.state == tk.NORMAL
        
        # Disable button
        btn.configure(state=tk.DISABLED)
        assert btn.state == tk.DISABLED
        
        # Enable button again
        btn.configure(state=tk.NORMAL)
        assert btn.state == tk.NORMAL
    finally:
        app.destroy()

def test_category_editor_operations():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("No display available for GUI test")
        
    try:
        from src.ui.category_editor import CategoryEditor
        dummy_categories = {
            "DOCUMENTS": [".txt", ".pdf"],
            "IMAGES": [".jpg", ".png"]
        }
        with patch("src.ui.category_editor.load_categories", return_value=dummy_categories), \
             patch("src.ui.category_editor.save_categories", return_value=True) as mock_save, \
             patch("src.ui.category_editor.messagebox") as mock_msg:
             
            editor = CategoryEditor(root)
            
            # Check initialized categories
            assert "DOCUMENTS" in editor.categories
            assert "IMAGES" in editor.categories
            
            # Simulate adding a category (patching simpledialog)
            with patch("tkinter.simpledialog.askstring", return_value="MUSIC"):
                editor._add_category()
            assert "MUSIC" in editor.categories
            
            # Select first item (DOCUMENTS)
            editor.cat_list.selection_clear(0, tk.END)
            editor.cat_list.selection_set(0)
            editor._on_category_select(None)
            
            # Simulate adding an extension
            with patch("tkinter.simpledialog.askstring", return_value=".doc"):
                editor._add_extension()
            assert ".doc" in editor.categories["DOCUMENTS"]
            
            # Save changes
            editor._save_changes()
            mock_save.assert_called_once_with(editor.categories)
    finally:
        root.destroy()

def test_gui_individual_deselect():
    try:
        app = DesktopCleanerApp()
        app.start_main_app()
    except tk.TclError:
        pytest.skip("No display available for GUI test")
        
    try:
        app.scan_results = [
            ("test_file_alpha.txt", 1024, "FILE", "TEXT"),
            ("test_folder_beta", 0, "DIR", "FOLDER")
        ]
        
        # Trigger filter to render the checkbuttons in the console
        app.filter_console()
        
        # Verify both are selected by default
        assert app.item_selection_vars["test_file_alpha.txt"].get() is True
        assert app.item_selection_vars["test_folder_beta"].get() is True
        
        # Deselect the file
        app.item_selection_vars["test_file_alpha.txt"].set(False)
        
        with patch.object(app.cleaner, 'organize_files', return_value=([], [])) as mock_org_files, \
             patch.object(app.cleaner, 'organize_folders', return_value=([], [])) as mock_org_folders, \
             patch("src.gui.messagebox") as mock_msg:
             
             app.on_clean()
             
             # Assert only the checked folder is cleaned, not the unchecked file
             mock_org_files.assert_not_called()
             mock_org_folders.assert_called_once_with(["test_folder_beta"], dry_run=False)
    finally:
        app.destroy()
