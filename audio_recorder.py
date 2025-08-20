"""
Audio Recording Module - Handles live audio recording functionality
"""

import numpy as np
import wave
import threading
import time
import logging
from pathlib import Path
import tempfile
from datetime import datetime

# Optional import with fallback
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None

# PyQt6 imports for GUI components
try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QComboBox, 
                               QProgressBar, QGroupBox, QMessageBox)
    from PyQt6.QtCore import QTimer, pyqtSignal, QThread
    from PyQt6.QtGui import QFont
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


class AudioRecorder:
    """Handles live audio recording from microphone"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.channels = 1
        self.chunk_size = 1024
        
        if not PYAUDIO_AVAILABLE:
            self.logger.error("PyAudio not available - recording functionality disabled")
            self.audio = None
            self.format = None
            return
            
        self.format = pyaudio.paInt16
        
        # Initialize PyAudio
        try:
            self.audio = pyaudio.PyAudio()
            self.logger.info("Audio system initialized")
        except Exception as e:
            self.logger.error(f"Audio system initialization failed: {e}")
            self.audio = None
    
    def get_audio_devices(self):
        """Get list of available audio input devices"""
        devices = []
        if not self.audio:
            return devices
        
        try:
            device_count = self.audio.get_device_count()
            for i in range(device_count):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'max_input_channels': device_info['maxInputChannels'],
                        'default_sample_rate': device_info['defaultSampleRate']
                    })
            return devices
        except Exception as e:
            self.logger.error(f"Error getting audio devices: {e}")
            return []
    
    def start_recording(self, device_index=None):
        """Start recording audio"""
        if not self.audio:
            raise Exception("Audio system not initialized")
        
        if self.is_recording:
            self.logger.warning("Recording already in progress")
            return False
        
        try:
            self.audio_data = []
            self.is_recording = True
            
            # Open stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            self.logger.info("Recording started")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            self.is_recording = False
            return False
    
    def _recording_loop(self):
        """Recording loop - runs in separate thread"""
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
        except Exception as e:
            self.logger.error(f"Recording loop error: {e}")
        finally:
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
    
    def stop_recording(self):
        """Stop recording and return audio data"""
        if not self.is_recording:
            return None
        
        try:
            self.is_recording = False
            
            # Wait for recording thread to finish
            if hasattr(self, 'recording_thread'):
                self.recording_thread.join(timeout=2.0)
            
            if not self.audio_data:
                return None
            
            # Convert recorded data to numpy array
            audio_bytes = b''.join(self.audio_data)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Convert to float and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            self.logger.info(f"Recording stopped. Duration: {len(audio_float)/self.sample_rate:.2f} seconds")
            
            return audio_float, self.sample_rate
            
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            return None
    
    def save_recording(self, audio_data, sample_rate, filename):
        """Save recorded audio to file"""
        try:
            # Convert float audio back to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            self.logger.info(f"Recording saved to: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving recording: {e}")
            return False
    
    def get_recording_level(self):
        """Get current recording level (for VU meter)"""
        if not self.is_recording or not self.audio_data:
            return 0.0
        
        try:
            # Get last chunk of audio data
            if len(self.audio_data) > 0:
                last_chunk = self.audio_data[-1]
                audio_array = np.frombuffer(last_chunk, dtype=np.int16)
                audio_float = audio_array.astype(np.float32) / 32768.0
                
                # Calculate RMS level
                rms = np.sqrt(np.mean(audio_float ** 2))
                return min(rms * 100, 100)  # Scale to 0-100
            
            return 0.0
            
        except Exception as e:
            return 0.0
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.is_recording:
            self.stop_recording()
        
        if self.audio:
            try:
                self.audio.terminate()
                self.audio = None
                self.logger.info("Audio system cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up audio: {e}")
    
    def __del__(self):
        """Destructor - cleanup resources"""
        self.cleanup()


class RecordingThread(QThread):
    """Thread for handling recording in GUI"""
    
    level_updated = pyqtSignal(float)
    recording_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, recorder, device_index=None):
        super().__init__()
        self.recorder = recorder
        self.device_index = device_index
        self.is_running = False
    
    def run(self):
        """Run recording thread"""
        try:
            self.is_running = True
            
            if not self.recorder.start_recording(self.device_index):
                self.error_occurred.emit("Failed to start recording")
                return
            
            # Monitor recording levels
            while self.is_running and self.recorder.is_recording:
                level = self.recorder.get_recording_level()
                self.level_updated.emit(level)
                self.msleep(100)  # Update every 100ms
            
        except Exception as e:
            self.error_occurred.emit(f"Recording error: {e}")
    
    def stop_recording(self):
        """Stop the recording"""
        try:
            self.is_running = False
            result = self.recorder.stop_recording()
            if result:
                self.recording_finished.emit(result)
            else:
                self.error_occurred.emit("Failed to stop recording properly")
        except Exception as e:
            self.error_occurred.emit(f"Error stopping recording: {e}")


class RecordingDialog(QDialog):
    """Recording dialog for GUI integration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.recorder = AudioRecorder()
        self.recording_file = None
        self.recording_thread = None
        
        if not PYAUDIO_AVAILABLE:
            QMessageBox.critical(self, "Audio Error", 
                               "PyAudio is not available. Recording functionality is disabled.")
            return
        
        if not self.recorder.audio:
            QMessageBox.critical(self, "Audio Error", 
                               "Failed to initialize audio system. Check your microphone connection.")
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the recording dialog UI"""
        self.setWindowTitle("Audio Recording")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Device selection
        device_group = QGroupBox("Audio Device")
        device_layout = QVBoxLayout(device_group)
        
        self.device_combo = QComboBox()
        self.populate_devices()
        device_layout.addWidget(QLabel("Select Microphone:"))
        device_layout.addWidget(self.device_combo)
        
        layout.addWidget(device_group)
        
        # Recording controls
        controls_group = QGroupBox("Recording Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Level meter
        self.level_label = QLabel("Audio Level:")
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        
        controls_layout.addWidget(self.level_label)
        controls_layout.addWidget(self.level_bar)
        
        # Recording status
        self.status_label = QLabel("Ready to record")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        controls_layout.addWidget(self.status_label)
        
        # Time display
        self.time_label = QLabel("00:00")
        self.time_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: blue;")
        controls_layout.addWidget(self.time_label)
        
        layout.addWidget(controls_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("🎤 Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        self.save_btn = QPushButton("💾 Save & Use")
        self.save_btn.clicked.connect(self.save_and_use)
        self.save_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.record_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(QLabel(""))  # Spacer
        layout.addLayout(button_layout)
        
        # Timer for updating display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.start_time = None
    
    def populate_devices(self):
        """Populate device combo box"""
        devices = self.recorder.get_audio_devices()
        
        if not devices:
            self.device_combo.addItem("No audio devices found")
            return
        
        for device in devices:
            self.device_combo.addItem(
                f"{device['name']} ({device['max_input_channels']} ch)",
                device['index']
            )
    
    def toggle_recording(self):
        """Toggle recording state"""
        if not self.recorder.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording"""
        try:
            device_index = self.device_combo.currentData()
            
            # Create and start recording thread
            self.recording_thread = RecordingThread(self.recorder, device_index)
            self.recording_thread.level_updated.connect(self.update_level)
            self.recording_thread.recording_finished.connect(self.on_recording_finished)
            self.recording_thread.error_occurred.connect(self.on_recording_error)
            
            self.recording_thread.start()
            
            # Update UI
            self.record_btn.setText("🛑 Stop Recording")
            self.record_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
            self.status_label.setText("Recording...")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.device_combo.setEnabled(False)
            self.save_btn.setEnabled(False)
            
            # Start timer
            self.start_time = time.time()
            self.timer.start(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Recording Error", f"Failed to start recording: {e}")
    
    def stop_recording(self):
        """Stop recording"""
        try:
            if self.recording_thread:
                self.recording_thread.stop_recording()
            
            # Update UI immediately
            self.record_btn.setText("🎤 Start Recording")
            self.record_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
            self.status_label.setText("Processing...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
            self.device_combo.setEnabled(True)
            
            # Stop timer
            self.timer.stop()
            
        except Exception as e:
            QMessageBox.critical(self, "Recording Error", f"Failed to stop recording: {e}")
    
    def update_level(self, level):
        """Update recording level display"""
        self.level_bar.setValue(int(level))
    
    def update_time(self):
        """Update time display"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def on_recording_finished(self, result):
        """Handle recording finished"""
        try:
            audio_data, sample_rate = result
            
            if audio_data is not None and len(audio_data) > 0:
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.recording_file = Path(temp_dir) / f"recording_{timestamp}.wav"
                
                # Save the recording
                if self.recorder.save_recording(audio_data, sample_rate, self.recording_file):
                    self.status_label.setText("Recording completed successfully!")
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.save_btn.setEnabled(True)
                else:
                    self.on_recording_error("Failed to save recording")
            else:
                self.on_recording_error("No audio data recorded")
                
        except Exception as e:
            self.on_recording_error(f"Error processing recording: {e}")
    
    def on_recording_error(self, error_message):
        """Handle recording error"""
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        QMessageBox.critical(self, "Recording Error", error_message)
        
        # Reset UI
        self.record_btn.setText("🎤 Start Recording")
        self.record_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.device_combo.setEnabled(True)
        self.timer.stop()
    
    def save_and_use(self):
        """Save and use the recorded file"""
        if self.recording_file and self.recording_file.exists():
            self.accept()
        else:
            QMessageBox.warning(self, "No Recording", "No recording available to save.")
    
    def get_recorded_file(self):
        """Get the path to the recorded file"""
        return str(self.recording_file) if self.recording_file else None
    
    def show_recording_dialog(self):
        """Show the recording dialog and return the recorded file path"""
        try:
            if self.exec() == QDialog.DialogCode.Accepted:
                return self.get_recorded_file()
            return None
        except Exception as e:
            QMessageBox.critical(self, "Dialog Error", f"Error showing recording dialog: {e}")
            return None
    
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.recorder.is_recording:
            self.stop_recording()
        
        # Cleanup
        if self.recording_thread:
            self.recording_thread.quit()
            self.recording_thread.wait()
        
        self.recorder.cleanup()
        event.accept()


def show_recording_dialog(parent=None):
    """Convenience function to show recording dialog"""
    if not PYAUDIO_AVAILABLE:
        if PYQT6_AVAILABLE:
            QMessageBox.critical(parent, "Audio Error", 
                               "PyAudio is required for audio recording.\n"
                               "Please install it with: pip install pyaudio")
        return None
    
    dialog = RecordingDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_recorded_file()
    
    return None
