import autoit
import time
import os

# Note: autoit-wrapper is simpler for this specific task than full uiautomation sometimes,
# but uiautomation is more robust. Let's try uiautomation first as planned.
# Wait, let's stick to the plan: uiautomation.

import uiautomation as auto

def test_desktop_hover():
    print("Move your mouse over desktop icons. Press Ctrl+C to stop.")
    try:
        desktop = auto.ListControl(ClassName="SysListView32", Name="FolderView")
        # Sometimes it's directly under Pane "Program Manager"
        if not desktop.Exists(0, 0):
             desktop = auto.ListControl(ClassName="SysListView32", AutomationId="1")
        
        while True:
            rect = desktop.BoundingRectangle
            # print(f"Desktop Rect: {rect}")
            
            x, y = auto.GetCursorPos()
            element = auto.ControlFromCursor()
            
            if element:
                print(f"Under Mouse: Name={element.Name}, Type={element.ControlTypeName}, Class={element.ClassName}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_desktop_hover()
