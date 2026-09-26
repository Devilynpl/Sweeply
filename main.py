import sys
import argparse
from src.gui import DesktopCleanerApp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-skin', action='store_true', help='Run with standard Windows UI')
    args = parser.parse_args()
    
    app = DesktopCleanerApp(no_skin=args.no_skin)
    app.mainloop()

if __name__ == "__main__":
    main()

