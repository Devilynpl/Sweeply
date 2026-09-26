import os
import shutil
import pytest
from unittest.mock import MagicMock, patch
from src.core import Cleaner, UndoManager
from src.utils import get_category

# Test Utils
def test_get_category():
    assert get_category(".jpg") == "IMAGES"
    assert get_category(".mp3") == "MUSIC"
    assert get_category(".py") == "SCRIPTS_AND_CODE"
    assert get_category(".unknown") == "OTHER"
    assert get_category(".JPG") == "IMAGES" # Case insensitive

# Test Cleaner Logic
@pytest.fixture
def cleaner():
    return Cleaner()

def test_cleaner_init(cleaner):
    assert cleaner.desktop_path is not None
    assert "desktop.ini" in cleaner.ignore_files

def test_set_exclusions(cleaner):
    cleaner.set_exclusions([".lnk", ".ico"])
    assert ".lnk" in cleaner.ignore_files
    assert ".ico" in cleaner.ignore_files
    # Ensure system files remain
    assert "desktop.ini" in cleaner.ignore_files

@patch("os.path.expanduser")

def test_get_desktop_path(mock_expanduser):
    mock_expanduser.return_value = "/mock/desktop"
    c = Cleaner()
    assert c.desktop_path == "/mock/desktop"
    assert c.clean_folder_path == os.path.join("/mock/desktop", "Sweeply")

@patch("os.scandir")
def test_scan_desktop(mock_scandir, cleaner):
    # Setup mock desktop content
    cleaner.desktop_path = "/mock/desktop"
    
    entry1 = MagicMock()
    entry1.name = "photo.jpg"
    entry1.is_file.return_value = True
    entry1.stat.return_value.st_size = 1024
    
    entry2 = MagicMock()
    entry2.name = "doc.pdf"
    entry2.is_file.return_value = True
    entry2.stat.return_value.st_size = 2048
    
    entry3 = MagicMock()
    entry3.name = "folder"
    entry3.is_file.return_value = False
    
    entry4 = MagicMock()
    entry4.name = ".hidden"
    entry4.is_file.return_value = True
    entry4.stat.return_value.st_size = 100
    
    entry5 = MagicMock()
    entry5.name = "desktop.ini"
    entry5.is_file.return_value = True
    entry5.stat.return_value.st_size = 200
    
    entry6 = MagicMock()
    entry6.name = "shortcut.lnk"
    entry6.is_file.return_value = True
    entry6.stat.return_value.st_size = 300
    
    mock_scandir.return_value.__enter__.return_value = [entry1, entry2, entry3, entry4, entry5, entry6]

    # 1. Default scan (should ignore desktop.ini, .hidden)
    cleaner.set_exclusions([]) # default only system
    files = cleaner.scan_desktop()
    expected = [("photo.jpg", 1024), ("doc.pdf", 2048), ("shortcut.lnk", 300)]
    assert sorted(files) == sorted(expected)

    # 2. Exclude shortcuts
    cleaner.set_exclusions([".lnk"])
    files = cleaner.scan_desktop()
    expected_excl = [("photo.jpg", 1024), ("doc.pdf", 2048)]
    assert sorted(files) == sorted(expected_excl)


@patch("shutil.move")
@patch("os.makedirs")
@patch("os.path.exists")
def test_organize_files_dry_run(mock_exists, mock_makedirs, mock_move, cleaner):
    cleaner.desktop_path = "/mock/desktop"
    files = ["photo.jpg", "doc.pdf"]
    
    # Mock exists to say CLEAN folder exists
    mock_exists.return_value = True
    
    # Execute dry run
    preview = cleaner.organize_files(files, dry_run=True)
    
    assert len(preview) == 2
    assert preview[0] == ("photo.jpg", "IMAGES")
    assert preview[1] == ("doc.pdf", "DOCUMENTS")
    
    # Ensure no side effects
    mock_makedirs.assert_not_called()
    mock_move.assert_not_called()

@patch("shutil.move")
@patch("os.makedirs")
@patch("os.path.exists")
def test_organize_files_execution(mock_exists, mock_makedirs, mock_move, cleaner):
    cleaner.config = {"dated_folders": False}
    cleaner.desktop_path = "/mock/desktop"
    cleaner.clean_folder_path = os.path.join("/mock/desktop", "CLEAN")
    files = ["photo.jpg"]
    
    mock_exists.return_value = False # Folders don't exist yet
    
    results, errors = cleaner.organize_files(files, dry_run=False)
    
    # Check directory creation
    mock_makedirs.assert_any_call(os.path.join("/mock/desktop", "CLEAN", "IMAGES"), exist_ok=True)
    
    # Check move
    src = os.path.join("/mock/desktop", "photo.jpg")
    dst = os.path.join("/mock/desktop", "CLEAN", "IMAGES", "photo.jpg")
    mock_move.assert_called_with(src, dst)
    
    assert len(results) == 1
    assert len(errors) == 0

# Test Undo Manager
def test_undo_manager():
    manager = UndoManager()
    
    # Simulate a move
    moves = [("/src/file1.txt", "/dst/file1.txt"), ("/src/file2.jpg", "/dst/file2.jpg")]
    manager.push_history(moves)
    
    assert manager.has_history() is True
    
    with patch("shutil.move") as mock_move:
        # Mock exists to ensure undo logic proceeds
        with patch("os.path.exists", return_value=True):
             manager.undo_last() 

        

@patch("os.scandir")
def test_scan_desktop_folders(mock_scandir, cleaner):
    cleaner.desktop_path = "/mock/desktop"
    
    entry1 = MagicMock()
    entry1.name = "file.txt"
    entry1.is_dir.return_value = False
    
    entry2 = MagicMock()
    entry2.name = "MyFolder"
    entry2.is_dir.return_value = True
    entry2.stat.return_value.st_size = 4096
    
    entry3 = MagicMock()
    entry3.name = "desktop.ini"
    entry3.is_dir.return_value = False
    
    entry4 = MagicMock()
    entry4.name = "AnotherFolder"
    entry4.is_dir.return_value = True
    entry4.stat.return_value.st_size = 8192

    mock_scandir.return_value.__enter__.return_value = [entry1, entry2, entry3, entry4]
    
    # 1. Default scan (should find both folders)
    cleaner.set_skip_folders(False)
    folders = cleaner.scan_desktop_folders()
    expected = [("MyFolder", 0), ("AnotherFolder", 0)]
    assert sorted(folders) == sorted(expected)

    # 2. Skip folders scan
    cleaner.set_skip_folders(True)
    folders = cleaner.scan_desktop_folders()
    assert folders == []

@patch("shutil.move")
@patch("os.makedirs")
@patch("os.path.exists")
def test_organize_folders_execution(mock_exists, mock_makedirs, mock_move, cleaner):
    cleaner.config = {"dated_folders": False}
    cleaner.desktop_path = "/mock/desktop"
    cleaner.clean_folder_path = os.path.join("/mock/desktop", "CLEAN")
    folders = ["MyFolder"]
    
    mock_exists.return_value = False 
    
    results, errors = cleaner.organize_folders(folders, dry_run=False)
    
    # Check directory creation for @FOLDERS
    mock_makedirs.assert_any_call(os.path.join("/mock/desktop", "CLEAN", "@FOLDERS"), exist_ok=True)
    
    # Check move
    src = os.path.join("/mock/desktop", "MyFolder")
    dst = os.path.join("/mock/desktop", "CLEAN", "@FOLDERS", "MyFolder")
    mock_move.assert_called_with(src, dst)
    
    assert len(results) == 1
    assert len(errors) == 0

def test_custom_exclusions(cleaner):
    # Mock config to have custom ignored items
    cleaner.config["ignored_items"] = ["keep_this_file.txt", "keep_this_dir"]
    cleaner.set_exclusions([".lnk"])
    
    # Check that both custom items and lnk extension are in ignore_files
    assert "keep_this_file.txt" in cleaner.ignore_files
    assert "keep_this_dir" in cleaner.ignore_files
    assert ".lnk" in cleaner.ignore_files
    assert "desktop.ini" in cleaner.ignore_files
