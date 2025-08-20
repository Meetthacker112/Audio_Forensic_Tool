"""
Setup and Installation Script
Run this script to set up the Forensic Audio Analysis Tool
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for installation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    logger = logging.getLogger(__name__)
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    logger = logging.getLogger(__name__)
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        logger.error("requirements.txt not found")
        return False
    
    try:
        logger.info("Installing Python packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("Package installation completed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Package installation failed: {e}")
        return False

def download_nltk_data():
    """Download required NLTK data"""
    logger = logging.getLogger(__name__)
    
    try:
        import nltk
        logger.info("Downloading NLTK data...")
        
        nltk.download('punkt', quiet=False)
        nltk.download('stopwords', quiet=False)
        nltk.download('vader_lexicon', quiet=False)
        nltk.download('averaged_perceptron_tagger', quiet=False)
        
        logger.info("NLTK data download completed")
        return True
    except Exception as e:
        logger.error(f"NLTK data download failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    logger = logging.getLogger(__name__)
    
    directories = ["logs", "reports", "temp", "models"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {dir_name}")
    
    return True

def setup_audio_system():
    """Setup audio system dependencies"""
    logger = logging.getLogger(__name__)
    
    try:
        # Test audio imports
        import pyaudio
        import soundfile
        import librosa
        
        logger.info("Audio system setup successful")
        return True
    except ImportError as e:
        logger.warning(f"Audio system setup issue: {e}")
        logger.info("Some audio features may not work properly")
        return True  # Non-fatal

def check_optional_dependencies():
    """Check optional dependencies and provide guidance"""
    logger = logging.getLogger(__name__)
    
    optional_deps = {
        'whisper': 'Advanced speech recognition',
        'pyannote.audio': 'Professional speaker diarization',
        'transformers': 'Emotion analysis and advanced NLP',
        'torch': 'Machine learning models'
    }
    
    missing_deps = []
    
    for dep, description in optional_deps.items():
        try:
            __import__(dep.replace('.', '/'))
            logger.info(f"✓ {dep} - {description}")
        except ImportError:
            missing_deps.append((dep, description))
            logger.warning(f"✗ {dep} - {description} (optional)")
    
    if missing_deps:
        logger.info("\\nOptional dependencies missing:")
        for dep, desc in missing_deps:
            logger.info(f"  pip install {dep}")
    
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    logger = logging.getLogger(__name__)
    
    if sys.platform != "win32":
        return True
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Forensic Audio Analysis.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        logger.info("Desktop shortcut created")
        return True
    except Exception as e:
        logger.warning(f"Could not create desktop shortcut: {e}")
        return True  # Non-fatal

def verify_installation():
    """Verify that the installation is working"""
    logger = logging.getLogger(__name__)
    
    try:
        # Test core imports
        from audio_processing import AudioProcessor
        from speech_analysis import SpeechAnalyzer  
        from keyword_detection import KeywordDetector
        from forensic_ai import ForensicAI
        from report_generator import ReportGenerator
        
        logger.info("✓ All core modules imported successfully")
        
        # Test basic functionality
        processor = AudioProcessor()
        analyzer = SpeechAnalyzer()
        detector = KeywordDetector()
        ai = ForensicAI()
        generator = ReportGenerator()
        
        logger.info("✓ All components initialized successfully")
        
        return True
    except Exception as e:
        logger.error(f"Installation verification failed: {e}")
        return False

def main():
    """Main setup function"""
    logger = setup_logging()
    
    logger.info("=" * 50)
    logger.info("FORENSIC AUDIO ANALYSIS TOOL - SETUP")
    logger.info("=" * 50)
    
    # Setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Installing Python packages", install_requirements),
        ("Downloading NLTK data", download_nltk_data),
        ("Setting up audio system", setup_audio_system),
        ("Checking optional dependencies", check_optional_dependencies),
        ("Creating desktop shortcut", create_desktop_shortcut),
        ("Verifying installation", verify_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"\\n{step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            logger.error(f"Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Summary
    logger.info("\\n" + "=" * 50)
    logger.info("SETUP SUMMARY")
    logger.info("=" * 50)
    
    if not failed_steps:
        logger.info("✓ Setup completed successfully!")
        logger.info("\\nTo start the application, run:")
        logger.info("  python main.py")
        logger.info("\\nFor OpenAI features, add your API key to config.json")
    else:
        logger.warning("⚠ Setup completed with warnings:")
        for step in failed_steps:
            logger.warning(f"  - {step}")
        
        logger.info("\\nYou can still run the application, but some features may be limited.")
        logger.info("Run: python main.py")
    
    logger.info("\\nFor support, check the README.md file or documentation.")

if __name__ == "__main__":
    main()
