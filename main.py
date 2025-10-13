#!/usr/bin/env python3
"""
Forensic Audio Analysis Tool - Main Entry Point

This is the main entry point for the Forensic Audio Analysis Tool application.
It initializes logging, checks system requirements, and launches the GUI.
"""

import sys
import os
import logging
from pathlib import Path
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "forensic_tool.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if critical dependencies are available"""
    missing_deps = []
    
    # Critical GUI dependencies
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        missing_deps.append("PyQt6")
    
    # Audio processing dependencies
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    try:
        import soundfile
    except ImportError:
        missing_deps.append("soundfile")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    return missing_deps

def main():
    """Main application entry point"""
    logger = setup_logging()
    
    try:
        logger.info("Starting Forensic Audio Analysis Tool...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required")
            print("Error: Python 3.8 or higher is required")
            sys.exit(1)
        
        logger.info(f"Python version: {sys.version}")
        
        # Check dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            logger.error(f"Missing dependencies: {missing_deps}")
            print(f"Error: Missing required packages: {', '.join(missing_deps)}")
            print("Please run: python setup.py")
            print("Or install manually: pip install -r requirements.txt")
            sys.exit(1)
        
        # Import and create the application
        from PyQt6.QtWidgets import QApplication
        from gui import MainWindow
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Forensic Audio Analysis Tool")
        app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        logger.info("Initializing GUI...")
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run the application
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Import error: {e}")
        print("Please install dependencies by running: python setup.py")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        print(f"Error starting application: {e}")
        print("Check logs/forensic_tool.log for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    main()
