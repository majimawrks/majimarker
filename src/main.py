"""MajiMarker - Image Watermarking Tool

Entry point for the application.
"""

import sys
from pathlib import Path

# Add src to path for imports when running as script
if __name__ == "__main__":
    src_dir = Path(__file__).parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from gui import run_app


def main():
    """Main entry point."""
    run_app()


if __name__ == "__main__":
    main()
