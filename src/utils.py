import os
import json

def load_categories():
    """
    Loads categories from categories.json.
    """
    try:
        # Get the path to categories.json relative to this file
        current_dir = os.path.dirname(__file__)
        json_path = os.path.join(current_dir, "categories.json")
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading categories: {e}")
    return {}

def save_categories(categories):
    """
    Saves categories to categories.json.
    """
    try:
        current_dir = os.path.dirname(__file__)
        json_path = os.path.join(current_dir, "categories.json")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving categories: {e}")
        return False

# Define file categories and their extensions
CATEGORIES = load_categories()

def get_category(file_extension):
    """
    Returns the category for a given file extension.
    Returns "OTHER" if no match is found.
    Extensions should be lowercase and include the dot (e.g., ".jpg").
    """
    ext = file_extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "OTHER"
