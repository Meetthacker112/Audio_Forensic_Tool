"""
Enhanced GUI Module - Modern interface for Forensic Audio Analysis Tool with multi-threading
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar,
    QTabWidget, QScrollArea, QSplitter, QGroupBox, QListWidget,
    QComboBox, QSpinBox, QCheckBox, QSlider, QFrame, QMessageBox,
    QStatusBar, QMenuBar, QToolBar, QApplication, QDialog, QDialogButtonBox,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QMutex, QWaitCondition
from PyQt6.QtGui import QFont, QPixmap, QIcon, QAction, QPalette, QColor, QTextCharFormat, QTextCursor
import pyqtgraph as pg
import numpy as np
from audio_processing import AudioProcessor
from speech_analysis import EnhancedSpeechAnalyzer
from keyword_detection import EnhancedKeywordDetector
from forensic_ai import ForensicAI
from report_generator import ReportGenerator
import logging
import json
from datetime import datetime


class LanguageSelectionDialog(QDialog):
    """Dialog for language selection and analysis options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Configuration")
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Language selection
        lang_group = QGroupBox("Language Detection")
        lang_layout = QVBoxLayout(lang_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(['Auto-detect', 'English', 'Hindi', 'Gujarati'])
        lang_layout.addWidget(QLabel("Select Language:"))
        lang_layout.addWidget(self.language_combo)
        layout.addWidget(lang_group)
        
        # Analysis options
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout(options_group)
        
        self.transcription_check = QCheckBox("Multi-language Transcription")
        self.transcription_check.setChecked(True)
        options_layout.addWidget(self.transcription_check)
        
        self.diarization_check = QCheckBox("Speaker Diarization")
        self.diarization_check.setChecked(True)
        options_layout.addWidget(self.diarization_check)
        
        self.keyword_check = QCheckBox("Crime Keyword Detection")
        self.keyword_check.setChecked(True)
        options_layout.addWidget(self.keyword_check)
        
        self.ai_check = QCheckBox("AI Forensic Analysis")
        self.ai_check.setChecked(True)
        options_layout.addWidget(self.ai_check)
        
        layout.addWidget(options_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self):
        return {
            'language': self.language_combo.currentText().lower().replace('-', '_'),
            'transcription': self.transcription_check.isChecked(),
            'diarization': self.diarization_check.isChecked(),
            'keyword_detection': self.keyword_check.isChecked(),
            'ai_analysis': self.ai_check.isChecked()
        }


class EnhancedAudioAnalysisThread(QThread):
    """Enhanced thread for comprehensive audio analysis"""
    progress_updated = pyqtSignal(int, str)
    analysis_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    keyword_detected = pyqtSignal(dict)
    
    def __init__(self, file_path, config):
        super().__init__()
        self.file_path = file_path
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.should_stop = False
    
    def run(self):
        """Run comprehensive audio analysis"""
        try:
            self.progress_updated.emit(5, "Initializing analysis systems...")
            
            # Initialize enhanced processors
            audio_processor = AudioProcessor()
            speech_analyzer = EnhancedSpeechAnalyzer()
            keyword_detector = EnhancedKeywordDetector()
            forensic_ai = ForensicAI()
            
            results = {
                'file_path': self.file_path,
                'analysis_timestamp': datetime.now().isoformat(),
                'config': self.config
            }
            
            # Step 1: Load and analyze audio
            self.progress_updated.emit(10, "Loading audio file...")
            if self.should_stop:
                return
                
            audio_analysis = audio_processor.analyze_audio(self.file_path)
            results['audio_analysis'] = audio_analysis
            
            # Step 2: Enhanced transcription with language detection
            if self.config.get('transcription', True):
                self.progress_updated.emit(25, "Performing multi-language transcription...")
                if self.should_stop:
                    return
                    
                language = self.config.get('language', 'auto')
                if language == 'auto_detect' or language == 'auto':
                    language = 'auto'
                
                self.logger.info(f"Starting transcription with language: {language}")
                transcript_data = speech_analyzer.transcribe_audio_enhanced(self.file_path, language)
                results['transcript'] = transcript_data
                
                self.logger.info(f"Transcription completed. Data keys: {list(transcript_data.keys()) if transcript_data else 'None'}")
                
                if transcript_data and not transcript_data.get('error'):
                    detected_language = transcript_data.get('language', 'english')
                    transcript_text = transcript_data.get('transcript', '')
                    confidence = transcript_data.get('confidence', 0)
                    
                    self.logger.info(f"Transcript length: {len(transcript_text)} characters")
                    self.logger.info(f"Language: {detected_language}, Confidence: {confidence}")
                    
                    if transcript_text:
                        self.progress_updated.emit(35, f"Transcription successful: {detected_language.title()}")
                    else:
                        self.progress_updated.emit(35, f"Transcription completed but no text extracted")
                else:
                    error_msg = transcript_data.get('error', 'Unknown error') if transcript_data else 'No data returned'
                    self.progress_updated.emit(35, f"Transcription failed: {error_msg}")
                    self.logger.warning(f"Transcription had issues: {error_msg}")
            else:
                self.progress_updated.emit(35, "Transcription skipped")
            
            # Step 3: Speaker diarization
            if self.config.get('diarization', True) and 'transcript' in results:
                self.progress_updated.emit(45, "Analyzing speakers...")
                if self.should_stop:
                    return
                    
                # Enhanced speaker analysis is included in transcript_data
                results['speakers'] = {
                    'count': results['transcript'].get('speaker_count', 1),
                    'segments': results['transcript'].get('speaker_segments', [])
                }
            
            # Step 4: Enhanced keyword detection
            if self.config.get('keyword_detection', True) and 'transcript' in results:
                self.progress_updated.emit(60, "Detecting crime-related keywords...")
                if self.should_stop:
                    return
                
                try:
                    transcript_text = results['transcript'].get('transcript', '')
                    detected_language = results['transcript'].get('language', 'english')
                    
                    if transcript_text.strip():
                        self.logger.info(f"Analyzing {len(transcript_text)} characters for keywords in {detected_language}")
                        keywords = keyword_detector.detect_keywords_enhanced(transcript_text, detected_language)
                        results['keywords'] = keywords
                        
                        # Emit keyword alerts for real-time display
                        high_priority_count = 0
                        for keyword in keywords:
                            if keyword.get('severity') in ['CRITICAL', 'HIGH']:
                                high_priority_count += 1
                                self.keyword_detected.emit(keyword)
                        
                        self.logger.info(f"Found {len(keywords)} total keywords, {high_priority_count} high-priority")
                    else:
                        self.logger.warning("No transcript text available for keyword detection")
                        results['keywords'] = []
                        
                except Exception as e:
                    self.logger.error(f"Keyword detection error: {e}")
                    results['keywords'] = []
            else:
                self.logger.info("Keyword detection skipped")
                results['keywords'] = []
            
            # Step 5: AI forensic analysis
            if self.config.get('ai_analysis', True):
                self.progress_updated.emit(75, "Generating AI forensic insights...")
                if self.should_stop:
                    return
                
                try:
                    self.logger.info("Starting AI forensic analysis...")
                    ai_insights = forensic_ai.generate_comprehensive_analysis(results)
                    results['ai_analysis'] = ai_insights
                    self.logger.info("AI analysis completed successfully")
                except Exception as e:
                    self.logger.error(f"AI analysis error: {e}")
                    results['ai_analysis'] = {'error': str(e), 'message': 'AI analysis failed'}
            else:
                self.logger.info("AI analysis skipped")
                results['ai_analysis'] = {'message': 'AI analysis disabled'}
            
            # Step 6: Generate final report data
            self.progress_updated.emit(90, "Preparing analysis results...")
            if self.should_stop:
                return
            
            # Calculate overall risk score
            results['risk_assessment'] = self.calculate_risk_score(results)
            
            self.progress_updated.emit(100, "Analysis completed successfully!")
            self.analysis_completed.emit(results)
            
        except Exception as e:
            self.logger.error(f"Analysis thread error: {e}")
            self.error_occurred.emit(str(e))
    
    def calculate_risk_score(self, results):
        """Calculate overall forensic risk score"""
        score = 0
        factors = []
        
        # Keyword-based scoring
        keywords = results.get('keywords', [])
        if keywords:
            critical_count = sum(1 for kw in keywords if kw.get('severity') == 'CRITICAL')
            high_count = sum(1 for kw in keywords if kw.get('severity') == 'HIGH')
            medium_count = sum(1 for kw in keywords if kw.get('severity') == 'MEDIUM')
            
            keyword_score = (critical_count * 30) + (high_count * 20) + (medium_count * 10)
            score += min(keyword_score, 70)  # Cap at 70
            
            if critical_count > 0:
                factors.append(f"Critical threats detected ({critical_count})")
            if high_count > 0:
                factors.append(f"High-risk keywords found ({high_count})")
        
        # AI analysis scoring
        ai_analysis = results.get('ai_analysis', {})
        if ai_analysis:
            intent_score = ai_analysis.get('intent_likelihood', 0)
            if intent_score > 70:
                score += 20
                factors.append("High criminal intent likelihood")
            elif intent_score > 40:
                score += 10
                factors.append("Moderate criminal intent")
        
        # Determine risk level
        if score >= 80:
            risk_level = "CRITICAL"
        elif score >= 60:
            risk_level = "HIGH" 
        elif score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'score': min(score, 100),
            'level': risk_level,
            'factors': factors,
            'recommendation': self.get_recommendation(risk_level)
        }
    
    def get_recommendation(self, risk_level):
        """Get recommendation based on risk level"""
        recommendations = {
            'CRITICAL': "IMMEDIATE ACTION REQUIRED: High probability of criminal activity. Consider emergency response and legal intervention.",
            'HIGH': "URGENT ATTENTION: Significant criminal indicators detected. Recommend immediate investigation.",
            'MEDIUM': "INVESTIGATION RECOMMENDED: Suspicious activity detected. Further analysis and monitoring advised.",
            'LOW': "ROUTINE MONITORING: Low risk indicators. Standard documentation and filing recommended."
        }
        return recommendations.get(risk_level, "No specific recommendation.")
    
    def stop(self):
        """Stop the analysis thread"""
        self.should_stop = True


class MainWindow(QMainWindow):
    """Enhanced main application window with modern forensic interface"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_file = None
        self.analysis_results = {}
        self.report_generator = ReportGenerator()
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Forensic Audio Analysis Tool")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Set application style
        self.setStyleSheet(self.get_stylesheet())
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 1)
        
        # Create main content area
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 4)
        
        # Create status bar
        self.create_status_bar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
    
    def get_stylesheet(self):
        """Return application stylesheet"""
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                border-radius: 4px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', monospace;
            }
            
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """
    
    def create_sidebar(self):
        """Create the sidebar with controls"""
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(300)
        sidebar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        
        # File Input Section
        file_group = QGroupBox("Audio Input")
        file_layout = QVBoxLayout(file_group)
        
        self.upload_btn = QPushButton("📁 Upload Audio File")
        self.upload_btn.clicked.connect(self.upload_file)
        file_layout.addWidget(self.upload_btn)
        
        self.record_btn = QPushButton("🎤 Record Audio")
        self.record_btn.clicked.connect(self.record_audio)
        file_layout.addWidget(self.record_btn)
        
        self.current_file_label = QLabel("No file selected")
        self.current_file_label.setWordWrap(True)
        file_layout.addWidget(self.current_file_label)
        
        sidebar_layout.addWidget(file_group)
        
        # Analysis Options Section
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout(options_group)
        
        self.speech_analysis_cb = QCheckBox("Speech Analysis")
        self.speech_analysis_cb.setChecked(True)
        options_layout.addWidget(self.speech_analysis_cb)
        
        self.keyword_detection_cb = QCheckBox("Keyword Detection")
        self.keyword_detection_cb.setChecked(True)
        options_layout.addWidget(self.keyword_detection_cb)
        
        self.ai_analysis_cb = QCheckBox("AI Analysis")
        self.ai_analysis_cb.setChecked(True)
        options_layout.addWidget(self.ai_analysis_cb)
        
        self.anomaly_detection_cb = QCheckBox("Anomaly Detection")
        self.anomaly_detection_cb.setChecked(True)
        options_layout.addWidget(self.anomaly_detection_cb)
        
        # Language selection
        lang_label = QLabel("Analysis Language:")
        options_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Hindi", "Gujarati", "Multi-language"])
        options_layout.addWidget(self.language_combo)
        
        sidebar_layout.addWidget(options_group)
        
        # Analysis Controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.analyze_btn = QPushButton("🔍 Start Analysis")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        controls_layout.addWidget(self.analyze_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        controls_layout.addWidget(self.progress_label)
        
        sidebar_layout.addWidget(controls_group)
        
        # Report Generation
        report_group = QGroupBox("Report Generation")
        report_layout = QVBoxLayout(report_group)
        
        self.generate_report_btn = QPushButton("📄 Generate Report")
        self.generate_report_btn.clicked.connect(self.generate_report)
        self.generate_report_btn.setEnabled(False)
        report_layout.addWidget(self.generate_report_btn)
        
        format_label = QLabel("Format:")
        report_layout.addWidget(format_label)
        
        self.report_format_combo = QComboBox()
        self.report_format_combo.addItems(["PDF", "DOCX", "Both"])
        report_layout.addWidget(self.report_format_combo)
        
        sidebar_layout.addWidget(report_group)
        
        # Add stretch to push everything to top
        sidebar_layout.addStretch()
        
        return sidebar_frame
    
    def create_content_area(self):
        """Create the main content area with tabs"""
        self.tab_widget = QTabWidget()
        
        # Overview Tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Audio Analysis Tab
        self.audio_tab = self.create_audio_analysis_tab()
        self.tab_widget.addTab(self.audio_tab, "🎵 Audio Analysis")
        
        # Speech Analysis Tab
        self.speech_tab = self.create_speech_analysis_tab()
        self.tab_widget.addTab(self.speech_tab, "🗣️ Speech Analysis")
        
        # Keywords Tab
        self.keywords_tab = self.create_keywords_tab()
        self.tab_widget.addTab(self.keywords_tab, "🔍 Keywords")
        
        # AI Insights Tab
        self.ai_tab = self.create_ai_insights_tab()
        self.tab_widget.addTab(self.ai_tab, "🤖 AI Insights")
        
        # Forensic Report Tab
        self.report_tab = self.create_report_tab()
        self.tab_widget.addTab(self.report_tab, "📋 Report")
        
        return self.tab_widget
    
    def create_overview_tab(self):
        """Create overview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File information
        info_group = QGroupBox("File Information")
        info_layout = QGridLayout(info_group)
        
        self.file_info_labels = {}
        info_fields = [
            ("Filename:", "filename"),
            ("Format:", "format"),
            ("Duration:", "duration"),
            ("Sample Rate:", "sample_rate"),
            ("Channels:", "channels"),
            ("Bit Depth:", "bit_depth"),
            ("File Size:", "file_size")
        ]
        
        for i, (label, key) in enumerate(info_fields):
            info_layout.addWidget(QLabel(label), i, 0)
            value_label = QLabel("N/A")
            self.file_info_labels[key] = value_label
            info_layout.addWidget(value_label, i, 1)
        
        layout.addWidget(info_group)
        
        # Analysis summary
        summary_group = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        layout.addStretch()
        return tab
    
    def create_audio_analysis_tab(self):
        """Create audio analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Waveform
        waveform_group = QGroupBox("Waveform")
        waveform_layout = QVBoxLayout(waveform_group)
        
        self.waveform_widget = pg.PlotWidget()
        self.waveform_widget.setLabel('left', 'Amplitude')
        self.waveform_widget.setLabel('bottom', 'Time (s)')
        self.waveform_widget.setTitle('Audio Waveform')
        waveform_layout.addWidget(self.waveform_widget)
        
        layout.addWidget(waveform_group)
        
        # Spectrogram
        spectrogram_group = QGroupBox("Spectrogram")
        spectrogram_layout = QVBoxLayout(spectrogram_group)
        
        self.spectrogram_widget = pg.PlotWidget()
        self.spectrogram_widget.setLabel('left', 'Frequency (Hz)')
        self.spectrogram_widget.setLabel('bottom', 'Time (s)')
        self.spectrogram_widget.setTitle('Spectrogram')
        spectrogram_layout.addWidget(self.spectrogram_widget)
        
        layout.addWidget(spectrogram_group)
        
        return tab
    
    def create_speech_analysis_tab(self):
        """Create speech analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Transcription
        transcript_group = QGroupBox("Transcription")
        transcript_layout = QVBoxLayout(transcript_group)
        
        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        transcript_layout.addWidget(self.transcript_text)
        
        layout.addWidget(transcript_group)
        
        # Speaker analysis
        speaker_group = QGroupBox("Speaker Analysis")
        speaker_layout = QVBoxLayout(speaker_group)
        
        self.speaker_info = QTextEdit()
        self.speaker_info.setReadOnly(True)
        self.speaker_info.setMaximumHeight(150)
        speaker_layout.addWidget(self.speaker_info)
        
        layout.addWidget(speaker_group)
        
        # Emotion analysis
        emotion_group = QGroupBox("Emotion Analysis")
        emotion_layout = QVBoxLayout(emotion_group)
        
        self.emotion_info = QTextEdit()
        self.emotion_info.setReadOnly(True)
        self.emotion_info.setMaximumHeight(150)
        emotion_layout.addWidget(self.emotion_info)
        
        layout.addWidget(emotion_group)
        
        return tab
    
    def create_keywords_tab(self):
        """Create keywords detection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detected keywords
        keywords_group = QGroupBox("Detected Keywords")
        keywords_layout = QVBoxLayout(keywords_group)
        
        self.keywords_list = QListWidget()
        keywords_layout.addWidget(self.keywords_list)
        
        layout.addWidget(keywords_group)
        
        # Context analysis
        context_group = QGroupBox("Context Analysis")
        context_layout = QVBoxLayout(context_group)
        
        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        context_layout.addWidget(self.context_text)
        
        layout.addWidget(context_group)
        
        return tab
    
    def create_ai_insights_tab(self):
        """Create AI insights tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI analysis results
        insights_group = QGroupBox("AI-Generated Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.ai_insights_text = QTextEdit()
        self.ai_insights_text.setReadOnly(True)
        insights_layout.addWidget(self.ai_insights_text)
        
        layout.addWidget(insights_group)
        
        return tab
    
    def create_report_tab(self):
        """Create report preview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Report preview
        report_group = QGroupBox("Report Preview")
        report_layout = QVBoxLayout(report_group)
        
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        report_layout.addWidget(self.report_preview)
        
        layout.addWidget(report_group)
        
        return tab
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Audio File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.upload_file)
        file_menu.addAction(open_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = self.addToolBar("Main")
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.upload_file)
        toolbar.addAction(open_action)
        
        analyze_action = QAction("Analyze", self)
        analyze_action.triggered.connect(self.start_analysis)
        toolbar.addAction(analyze_action)
        
        report_action = QAction("Report", self)
        report_action.triggered.connect(self.generate_report)
        toolbar.addAction(report_action)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def upload_file(self):
        """Handle file upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.aac *.flac *.ogg *.m4a)"
        )
        
        if file_path:
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.current_file_label.setText(f"Selected: {filename}")
            self.analyze_btn.setEnabled(True)
            self.status_bar.showMessage(f"Loaded: {filename}")
            
            # Update overview tab with basic info
            self.update_file_info(file_path)
    
    def record_audio(self):
        """Handle audio recording"""
        try:
            from audio_recorder import RecordingDialog
            
            # Create recording dialog
            recording_dialog = RecordingDialog(self)
            recorded_file = recording_dialog.show_recording_dialog()
            
            if recorded_file:
                self.current_file = recorded_file
                filename = os.path.basename(recorded_file)
                self.current_file_label.setText(f"Recorded: {filename}")
                self.analyze_btn.setEnabled(True)
                self.status_bar.showMessage(f"Recording saved: {filename}")
                
                # Update overview tab with basic info
                self.update_file_info(recorded_file)
            
        except Exception as e:
            self.logger.error(f"Recording error: {e}")
            QMessageBox.critical(self, "Recording Error", f"Failed to record audio: {e}")
    
    def start_analysis(self):
        """Start audio analysis"""
        if not self.current_file:
            QMessageBox.warning(self, "No File", "Please select an audio file first.")
            return
        
        # Prepare analysis options with correct keys
        analysis_options = {
            'transcription': self.speech_analysis_cb.isChecked(),
            'keyword_detection': self.keyword_detection_cb.isChecked(),
            'ai_analysis': self.ai_analysis_cb.isChecked(),
            'diarization': self.speech_analysis_cb.isChecked(),  # Speaker diarization with speech
            'anomaly_detection': self.anomaly_detection_cb.isChecked(),
            'language': self.language_combo.currentText().lower()
        }
        
        # Handle language auto-detection
        if analysis_options['language'] == 'multi-language':
            analysis_options['language'] = 'auto'
        
        self.logger.info(f"Starting analysis with options: {analysis_options}")
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.analyze_btn.setEnabled(False)
        
        # Start analysis thread
        self.analysis_thread = EnhancedAudioAnalysisThread(self.current_file, analysis_options)
        self.analysis_thread.progress_updated.connect(self.update_progress)
        self.analysis_thread.analysis_completed.connect(self.analysis_completed)
        self.analysis_thread.error_occurred.connect(self.analysis_error)
        self.analysis_thread.start()
    
    def update_progress(self, value, message):
        """Update progress bar and message"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.status_bar.showMessage(message)
    
    def analysis_completed(self, results):
        """Handle completed analysis"""
        self.analysis_results = results
        self.update_ui_with_results(results)
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.generate_report_btn.setEnabled(True)
        
        self.status_bar.showMessage("Analysis completed")
        QMessageBox.information(self, "Analysis Complete", "Audio analysis has been completed successfully!")
    
    def analysis_error(self, error_message):
        """Handle analysis error"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.analyze_btn.setEnabled(True)
        
        self.status_bar.showMessage("Analysis failed")
        QMessageBox.critical(self, "Analysis Error", f"Analysis failed: {error_message}")
    
    def update_file_info(self, file_path):
        """Update file information in overview tab"""
        try:
            from audio_processing import AudioProcessor
            processor = AudioProcessor()
            metadata = processor.extract_metadata(file_path)
            
            self.file_info_labels['filename'].setText(os.path.basename(file_path))
            self.file_info_labels['format'].setText(metadata.get('format', 'N/A'))
            self.file_info_labels['duration'].setText(f"{metadata.get('duration', 0):.2f} seconds")
            self.file_info_labels['sample_rate'].setText(f"{metadata.get('sample_rate', 0)} Hz")
            self.file_info_labels['channels'].setText(str(metadata.get('channels', 0)))
            self.file_info_labels['bit_depth'].setText(f"{metadata.get('bit_depth', 0)} bit")
            self.file_info_labels['file_size'].setText(f"{metadata.get('file_size', 0):.2f} MB")
            
        except Exception as e:
            self.logger.error(f"Error updating file info: {e}")
    
    def update_ui_with_results(self, results):
        """Update UI with analysis results"""
        try:
            # Update overview
            summary = self.generate_summary(results)
            self.summary_text.setPlainText(summary)
            
            # Update audio analysis tab
            self.update_audio_visualizations(results)
            
            # Update speech analysis tab
            self.update_speech_analysis(results)
            
            # Update keywords tab
            self.update_keywords_display(results)
            
            # Update AI insights tab
            self.update_ai_insights(results)
            
            # Update report preview
            self.update_report_preview(results)
            
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")
    
    def generate_summary(self, results):
        """Generate analysis summary"""
        summary_lines = ["FORENSIC AUDIO ANALYSIS SUMMARY", "=" * 40, ""]
        
        # Audio metadata from audio_analysis
        if 'audio_analysis' in results and 'metadata' in results['audio_analysis']:
            metadata = results['audio_analysis']['metadata']
            summary_lines.append(f"File: {metadata.get('filename', 'N/A')}")
            summary_lines.append(f"Duration: {metadata.get('duration', 0):.2f} seconds")
            summary_lines.append(f"Quality: {metadata.get('sample_rate', 0)} Hz, {metadata.get('channels', 0)} channels")
            summary_lines.append(f"File Size: {metadata.get('file_size', 0):.2f} MB")
            summary_lines.append("")
        
        # Transcription info
        if 'transcript' in results and results['transcript']:
            transcript_data = results['transcript']
            transcript_text = transcript_data.get('transcript', '')
            language = transcript_data.get('language', 'Unknown')
            word_count = len(transcript_text.split()) if transcript_text else 0
            confidence = transcript_data.get('confidence', 0)
            
            summary_lines.append(f"Transcription: {word_count} words")
            summary_lines.append(f"Language Detected: {language.title()}")
            summary_lines.append(f"Confidence: {confidence:.2f}")
            summary_lines.append("")
        
        # Keywords detected
        if 'keywords' in results and results['keywords']:
            keywords = results['keywords']
            high_risk = [k for k in keywords if k.get('severity') in ['CRITICAL', 'HIGH']]
            summary_lines.append(f"Keywords Detected: {len(keywords)} total")
            if high_risk:
                summary_lines.append(f"High-Risk Keywords: {len(high_risk)}")
            summary_lines.append("")
        
        # Speaker information
        if 'speakers' in results and results['speakers']:
            speaker_data = results['speakers']
            speaker_count = speaker_data.get('count', 0)
            if speaker_count > 0:
                summary_lines.append(f"Speakers Detected: {speaker_count}")
                summary_lines.append("")
        
        # Risk assessment
        if 'risk_assessment' in results:
            risk_data = results['risk_assessment']
            risk_level = risk_data.get('level', 'Unknown')
            risk_score = risk_data.get('score', 0)
            summary_lines.append(f"Risk Level: {risk_level}")
            summary_lines.append(f"Risk Score: {risk_score}/100")
            summary_lines.append("")
        
        # AI Analysis status
        if 'ai_analysis' in results:
            summary_lines.append("AI Forensic Analysis: Completed")
            summary_lines.append("")
        
        # Audio quality assessment
        if 'audio_analysis' in results and 'summary' in results['audio_analysis']:
            audio_summary = results['audio_analysis']['summary']
            quality = audio_summary.get('audio_quality', 'Unknown')
            snr = audio_summary.get('estimated_snr_db', 0)
            anomalies = audio_summary.get('total_anomalies', 0)
            
            summary_lines.append(f"Audio Quality: {quality}")
            summary_lines.append(f"Signal-to-Noise Ratio: {snr:.1f} dB")
            if anomalies > 0:
                summary_lines.append(f"Anomalies Detected: {anomalies}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
    
    def update_audio_visualizations(self, results):
        """Update audio visualization widgets"""
        try:
            # Check for audio analysis data
            if 'audio_analysis' in results:
                audio_data = results['audio_analysis']
                
                # Waveform visualization
                if 'waveform' in audio_data and audio_data['waveform']:
                    waveform_data = audio_data['waveform']
                    if 'time' in waveform_data and 'amplitude' in waveform_data:
                        self.waveform_widget.clear()
                        self.waveform_widget.plot(
                            waveform_data['time'], 
                            waveform_data['amplitude'], 
                            pen='b',
                            name='Waveform'
                        )
                        self.waveform_widget.setLabel('left', 'Amplitude')
                        self.waveform_widget.setLabel('bottom', 'Time (s)')
                
                # Display audio statistics
                if 'noise_analysis' in audio_data:
                    noise_data = audio_data['noise_analysis']
                    stats_text = []
                    stats_text.append(f"SNR: {noise_data.get('snr_estimate_db', 0):.1f} dB")
                    stats_text.append(f"Speech Ratio: {noise_data.get('speech_ratio', 0):.2f}")
                    stats_text.append(f"Dynamic Range: {noise_data.get('dynamic_range_db', 0):.1f} dB")
                    
                    # Update audio stats display if widget exists
                    if hasattr(self, 'audio_stats_text'):
                        self.audio_stats_text.setPlainText("\n".join(stats_text))
                
                # Display anomalies
                if 'anomalies' in audio_data and audio_data['anomalies']:
                    anomaly_text = []
                    for anomaly in audio_data['anomalies']:
                        anomaly_text.append(
                            f"{anomaly.get('type', 'Unknown')} at {anomaly.get('time', 0):.2f}s "
                            f"(confidence: {anomaly.get('confidence', 0):.2f})"
                        )
                    
                    if hasattr(self, 'anomaly_text'):
                        self.anomaly_text.setPlainText("\n".join(anomaly_text))
                
        except Exception as e:
            self.logger.error(f"Error updating visualizations: {e}")
    
    def update_speech_analysis(self, results):
        """Update speech analysis tab"""
        try:
            # Transcription
            if 'transcript' in results and results['transcript']:
                transcript_data = results['transcript']
                transcript_text = transcript_data.get('transcript', 'No transcription available')
                language = transcript_data.get('language', 'Unknown')
                confidence = transcript_data.get('confidence', 0)
                method = transcript_data.get('method_used', 'Unknown')
                
                # Format transcription with metadata
                formatted_transcript = f"Language: {language.title()}\n"
                formatted_transcript += f"Method: {method}\n"
                formatted_transcript += f"Confidence: {confidence:.2f}\n"
                formatted_transcript += f"Processing Time: {transcript_data.get('processing_time', 0):.2f}s\n"
                formatted_transcript += "\n" + "="*50 + "\nTRANSCRIPT:\n" + "="*50 + "\n\n"
                formatted_transcript += transcript_text
                
                self.transcript_text.setPlainText(formatted_transcript)
            else:
                self.transcript_text.setPlainText("No transcription available")
            
            # Speaker information
            if 'speakers' in results and results['speakers']:
                speaker_data = results['speakers']
                speakers_text = f"Speaker Count: {speaker_data.get('count', 0)}\n\n"
                
                segments = speaker_data.get('segments', [])
                if segments:
                    speakers_text += "SPEAKER TIMELINE:\n" + "="*30 + "\n"
                    for segment in segments:
                        speaker = segment.get('speaker', 'Unknown')
                        start = segment.get('start_time', 0)
                        end = segment.get('end_time', 0)
                        text = segment.get('text', '')
                        speakers_text += f"\n[{start:.1f}s - {end:.1f}s] {speaker}:\n{text}\n"
                
                self.speaker_info.setPlainText(speakers_text)
            else:
                self.speaker_info.setPlainText("No speaker information available")
            
            # Emotion analysis (if available)
            if hasattr(self, 'emotion_info'):
                if 'transcript' in results and 'emotion_analysis' in results['transcript']:
                    emotion_data = results['transcript']['emotion_analysis']
                    emotion_text = self.format_emotion_analysis(emotion_data)
                    self.emotion_info.setPlainText(emotion_text)
                else:
                    self.emotion_info.setPlainText("No emotion analysis available")
                
        except Exception as e:
            self.logger.error(f"Error updating speech analysis: {e}")
    
    def update_keywords_display(self, results):
        """Update keywords tab"""
        try:
            self.keywords_list.clear()
            
            if 'keywords' in results and results['keywords']:
                keywords = results['keywords']
                
                # Sort keywords by severity
                severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                sorted_keywords = sorted(keywords, key=lambda k: severity_order.get(k.get('severity', 'LOW'), 3))
                
                for keyword_data in sorted_keywords:
                    if isinstance(keyword_data, dict):
                        keyword = keyword_data.get('keyword', 'Unknown')
                        severity = keyword_data.get('severity', 'LOW')
                        language = keyword_data.get('language', 'Unknown')
                        context = keyword_data.get('context', '')
                        confidence = keyword_data.get('confidence', 0)
                        
                        # Choose icon based on severity
                        if severity == 'CRITICAL':
                            icon = "🚨"
                        elif severity == 'HIGH':
                            icon = "🔴"
                        elif severity == 'MEDIUM':
                            icon = "🟡"
                        else:
                            icon = "🔵"
                        
                        # Format display text
                        display_text = f"{icon} [{severity}] {keyword} ({language})"
                        if confidence > 0:
                            display_text += f" - Confidence: {confidence:.2f}"
                        
                        item = QListWidgetItem(display_text)
                        
                        # Set tooltip with context
                        if context:
                            item.setToolTip(f"Context: {context}")
                        
                        self.keywords_list.addItem(item)
                
                # Update context display
                if hasattr(self, 'context_text'):
                    context_summary = self.generate_keyword_context_summary(keywords)
                    self.context_text.setPlainText(context_summary)
            else:
                # No keywords found
                item = QListWidgetItem("✅ No suspicious keywords detected")
                self.keywords_list.addItem(item)
                
                if hasattr(self, 'context_text'):
                    self.context_text.setPlainText("No crime-related content detected in the audio.")
                
        except Exception as e:
            self.logger.error(f"Error updating keywords display: {e}")
    
    def generate_keyword_context_summary(self, keywords):
        """Generate context summary for keywords"""
        try:
            summary_lines = ["CRIME KEYWORD ANALYSIS", "=" * 30, ""]
            
            # Group by severity
            by_severity = {}
            for kw in keywords:
                severity = kw.get('severity', 'LOW')
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(kw)
            
            # Display by severity
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity in by_severity:
                    summary_lines.append(f"{severity} RISK KEYWORDS ({len(by_severity[severity])}):")
                    for kw in by_severity[severity][:5]:  # Show top 5 per category
                        keyword = kw.get('keyword', 'Unknown')
                        context = kw.get('context', '')
                        if context:
                            # Truncate long context
                            if len(context) > 100:
                                context = context[:100] + "..."
                            summary_lines.append(f"  • {keyword}: \"{context}\"")
                        else:
                            summary_lines.append(f"  • {keyword}")
                    summary_lines.append("")
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            self.logger.error(f"Error generating keyword context summary: {e}")
            return "Error generating keyword summary"
                
        except Exception as e:
            self.logger.error(f"Error updating keywords: {e}")
    
    def update_ai_insights(self, results):
        """Update AI insights tab"""
        try:
            if 'ai_analysis' in results and results['ai_analysis']:
                ai_data = results['ai_analysis']
                
                insights_text = []
                insights_text.append("🤖 AI FORENSIC ANALYSIS")
                insights_text.append("=" * 50)
                insights_text.append("")
                
                # Executive Summary
                if 'executive_summary' in ai_data:
                    insights_text.append("📋 EXECUTIVE SUMMARY:")
                    insights_text.append("-" * 25)
                    insights_text.append(ai_data['executive_summary'])
                    insights_text.append("")
                
                # Criminal Assessment
                if 'criminal_assessment' in ai_data:
                    insights_text.append("⚠️ CRIMINAL ASSESSMENT:")
                    insights_text.append("-" * 25)
                    assessment = ai_data['criminal_assessment']
                    if isinstance(assessment, dict):
                        risk_level = assessment.get('risk_level', 'Unknown')
                        assessment_text = assessment.get('assessment', 'No assessment available')
                        insights_text.append(f"Risk Level: {risk_level}")
                        insights_text.append(f"Assessment: {assessment_text}")
                    else:
                        insights_text.append(str(assessment))
                    insights_text.append("")
                
                # Speaker Analysis
                if 'speaker_analysis' in ai_data:
                    insights_text.append("👥 SPEAKER ANALYSIS:")
                    insights_text.append("-" * 25)
                    speaker_analysis = ai_data['speaker_analysis']
                    if isinstance(speaker_analysis, dict):
                        insights_text.append(f"Speaker Count: {speaker_analysis.get('speaker_count', 'Unknown')}")
                        insights_text.append(f"Analysis: {speaker_analysis.get('analysis', 'No analysis available')}")
                    else:
                        insights_text.append(str(speaker_analysis))
                    insights_text.append("")
                
                # Investigation Recommendations
                if 'recommendations' in ai_data:
                    insights_text.append("📝 RECOMMENDATIONS:")
                    insights_text.append("-" * 25)
                    recommendations = ai_data['recommendations']
                    if isinstance(recommendations, list):
                        for i, rec in enumerate(recommendations, 1):
                            insights_text.append(f"{i}. {rec}")
                    else:
                        insights_text.append(str(recommendations))
                    insights_text.append("")
                
                # Risk Assessment
                if 'risk_assessment' in ai_data:
                    insights_text.append("🎯 RISK ASSESSMENT:")
                    insights_text.append("-" * 25)
                    risk_data = ai_data['risk_assessment']
                    if isinstance(risk_data, dict):
                        for key, value in risk_data.items():
                            insights_text.append(f"{key.replace('_', ' ').title()}: {value}")
                    else:
                        insights_text.append(str(risk_data))
                    insights_text.append("")
                
                formatted_insights = "\n".join(insights_text)
                
                if hasattr(self, 'ai_insights_text'):
                    self.ai_insights_text.setPlainText(formatted_insights)
            else:
                if hasattr(self, 'ai_insights_text'):
                    self.ai_insights_text.setPlainText("No AI analysis available. Ensure OpenAI API key is configured.")
                
        except Exception as e:
            self.logger.error(f"Error updating AI insights: {e}")
            if hasattr(self, 'ai_insights_text'):
                self.ai_insights_text.setPlainText(f"Error displaying AI insights: {e}")
    
    def update_report_preview(self, results):
        """Update report preview tab"""
        try:
            preview_text = self.report_generator.generate_preview(results)
            self.report_preview.setPlainText(preview_text)
            
        except Exception as e:
            self.logger.error(f"Error updating report preview: {e}")
    
    def format_speaker_diarization(self, diarization_data):
        """Format speaker diarization data"""
        if not diarization_data:
            return "No speaker diarization data available"
        
        formatted_lines = ["SPEAKER DIARIZATION", "=" * 20, ""]
        
        for segment in diarization_data:
            speaker = segment.get('speaker', 'Unknown')
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            text = segment.get('text', '')
            
            formatted_lines.append(f"{speaker} ({start_time:.1f}s - {end_time:.1f}s):")
            formatted_lines.append(f"  {text}")
            formatted_lines.append("")
        
        return "\n".join(formatted_lines)
    
    def format_emotion_analysis(self, emotion_data):
        """Format emotion analysis data"""
        if not emotion_data:
            return "No emotion analysis data available"
        
        formatted_lines = ["EMOTION ANALYSIS", "=" * 20, ""]
        
        for emotion, confidence in emotion_data.items():
            formatted_lines.append(f"{emotion.capitalize()}: {confidence:.2f}")
        
        return "\n".join(formatted_lines)
    
    def generate_report(self):
        """Generate enhanced forensic report with case tracking"""
        if not self.analysis_results:
            QMessageBox.warning(self, "No Data", "No analysis results available to generate report")
            return
        
        try:
            # Get output directory
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if not output_dir:
                return
            
            format_option = self.report_format_combo.currentText()
            generated_reports = []
            
            # Generate reports
            self.status_bar.showMessage("Generating forensic reports...")
            
            if format_option in ["PDF", "Both"]:
                pdf_path = self.report_generator.generate_pdf_report(self.analysis_results, output_dir)
                generated_reports.append(pdf_path)
                self.logger.info(f"PDF report generated: {os.path.basename(pdf_path)}")
            
            if format_option in ["DOCX", "Both"]:
                docx_path = self.report_generator.generate_docx_report(self.analysis_results, output_dir)
                generated_reports.append(docx_path)
                self.logger.info(f"DOCX report generated: {os.path.basename(docx_path)}")
            
            # Show completion message with details
            reports_dir = os.path.join(output_dir, "Forensic_Reports")
            report_names = [os.path.basename(path) for path in generated_reports]
            
            message = f"Forensic analysis complete!\n\n"
            message += f"Generated {len(generated_reports)} files:\n"
            for name in report_names:
                message += f"• {name}\n"
            message += f"\nLocation: {reports_dir}"
            
            self.status_bar.showMessage("Reports generated successfully")
            QMessageBox.information(self, "Reports Generated", message)
            
            # Option to open reports folder
            reply = QMessageBox.question(self, "Open Reports Folder", 
                                       "Would you like to open the reports folder?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(f'explorer "{reports_dir}"', shell=True)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", reports_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", reports_dir])
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            QMessageBox.critical(self, "Report Error", f"Failed to generate report: {e}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "Forensic Audio Analysis Tool v1.0\n\n"
                         "A comprehensive tool for forensic audio analysis\n"
                         "including speech recognition, keyword detection,\n"
                         "and AI-powered insights.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
