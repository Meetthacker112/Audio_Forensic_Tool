"""
Audio Processing Module - Handles audio loading, analysis, and visualization
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.stats import entropy
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import logging
from datetime import datetime
from pydub import AudioSegment
from scipy.signal import find_peaks

# Optional imports with fallbacks
try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    webrtcvad = None

try:
    import parselmouth
    PARSELMOUTH_AVAILABLE = True
except ImportError:
    PARSELMOUTH_AVAILABLE = False
    parselmouth = None


class AudioProcessor:
    """Handles all audio processing operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.wav', '.mp3', '.aac', '.flac', '.ogg', '.m4a']
    
    def load_audio(self, file_path, target_sr=22050):
        """Load audio file and return audio data and sample rate"""
        try:
            # Convert file path to string if it's a Path object
            file_path = str(file_path)
            
            # Check file format
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {file_ext}")
            
            # Load audio using librosa (handles most formats)
            try:
                audio_data, sample_rate = librosa.load(file_path, sr=target_sr, mono=False)
            except Exception as e:
                # Fallback to pydub for additional format support
                audio_segment = AudioSegment.from_file(file_path)
                audio_data = np.array(audio_segment.get_array_of_samples())
                
                # Handle stereo
                if audio_segment.channels == 2:
                    audio_data = audio_data.reshape((-1, 2)).T
                
                sample_rate = audio_segment.frame_rate
                
                # Resample if needed
                if sample_rate != target_sr:
                    audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=target_sr)
                    sample_rate = target_sr
            
            # Ensure mono for analysis (take mean if stereo)
            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=0)
            
            self.logger.info(f"Loaded audio: {file_path}, shape: {audio_data.shape}, sr: {sample_rate}")
            return audio_data, sample_rate
            
        except Exception as e:
            self.logger.error(f"Error loading audio file {file_path}: {e}")
            raise
    
    def extract_metadata(self, file_path):
        """Extract audio file metadata"""
        try:
            file_path = str(file_path)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Load audio to get properties
            audio_data, sample_rate = self.load_audio(file_path)
            duration = len(audio_data) / sample_rate
            
            # Try to get additional info using pydub
            try:
                audio_segment = AudioSegment.from_file(file_path)
                channels = audio_segment.channels
                bit_depth = audio_segment.sample_width * 8
                format_name = Path(file_path).suffix.upper()[1:]
            except:
                channels = 1  # fallback
                bit_depth = 16  # fallback
                format_name = Path(file_path).suffix.upper()[1:]
            
            metadata = {
                'filename': os.path.basename(file_path),
                'format': format_name,
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'bit_depth': bit_depth,
                'file_size': file_size_mb
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def generate_waveform(self, audio_data, sample_rate):
        """Generate waveform data for visualization"""
        try:
            time = np.linspace(0, len(audio_data) / sample_rate, len(audio_data))
            
            # Downsample for display if too many points
            max_points = 50000
            if len(audio_data) > max_points:
                step = len(audio_data) // max_points
                time = time[::step]
                audio_data = audio_data[::step]
            
            return {
                'time': time,
                'amplitude': audio_data
            }
            
        except Exception as e:
            self.logger.error(f"Error generating waveform: {e}")
            return {'time': [], 'amplitude': []}
    
    def generate_spectrogram(self, audio_data, sample_rate, n_fft=2048, hop_length=512):
        """Generate spectrogram data"""
        try:
            # Compute Short-Time Fourier Transform
            stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
            magnitude = np.abs(stft)
            
            # Convert to dB scale
            magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
            
            # Time and frequency axes
            time_frames = librosa.frames_to_time(np.arange(magnitude_db.shape[1]), 
                                               sr=sample_rate, hop_length=hop_length)
            frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
            
            return {
                'magnitude_db': magnitude_db,
                'time_frames': time_frames,
                'frequencies': frequencies
            }
            
        except Exception as e:
            self.logger.error(f"Error generating spectrogram: {e}")
            return {}
    
    def analyze_noise(self, audio_data, sample_rate):
        """Analyze noise characteristics in the audio"""
        try:
            # Calculate spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            # Zero crossing rate (indicates noise vs speech)
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            
            # Calculate background noise level
            # Use bottom 10% of RMS values as noise floor
            noise_floor = np.percentile(rms, 10)
            snr_estimate = 20 * np.log10(np.mean(rms) / (noise_floor + 1e-8))
            
            # Voice Activity Detection using energy
            energy_threshold = np.percentile(rms, 30)
            speech_segments = rms > energy_threshold
            speech_ratio = np.sum(speech_segments) / len(speech_segments)
            
            noise_analysis = {
                'noise_floor_db': 20 * np.log10(noise_floor + 1e-8),
                'snr_estimate_db': snr_estimate,
                'speech_ratio': speech_ratio,
                'avg_spectral_centroid': np.mean(spectral_centroids),
                'avg_spectral_rolloff': np.mean(spectral_rolloff),
                'avg_spectral_bandwidth': np.mean(spectral_bandwidth),
                'avg_zero_crossing_rate': np.mean(zcr),
                'dynamic_range_db': 20 * np.log10(np.max(rms) / (np.min(rms) + 1e-8))
            }
            
            return noise_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing noise: {e}")
            return {}
    
    def detect_anomalies(self, audio_data, sample_rate):
        """Detect potential anomalies or tampering in audio"""
        try:
            anomalies = []
            
            # 1. Detect sudden amplitude changes (potential cuts/edits)
            rms = librosa.feature.rms(y=audio_data, frame_length=2048, hop_length=512)[0]
            rms_diff = np.diff(rms)
            
            # Find sudden jumps
            threshold = 3 * np.std(rms_diff)
            sudden_changes = np.where(np.abs(rms_diff) > threshold)[0]
            
            for change_idx in sudden_changes:
                time_sec = librosa.frames_to_time(change_idx, sr=sample_rate, hop_length=512)
                anomalies.append({
                    'type': 'Sudden Amplitude Change',
                    'time': time_sec,
                    'confidence': min(abs(rms_diff[change_idx]) / threshold, 1.0)
                })
            
            # 2. Detect frequency domain anomalies
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            
            # Look for unusual spectral patterns
            spectral_entropy = []
            for frame in magnitude.T:
                # Normalize and calculate entropy
                frame_norm = frame / (np.sum(frame) + 1e-8)
                spec_entropy = entropy(frame_norm + 1e-8)
                spectral_entropy.append(spec_entropy)
            
            spectral_entropy = np.array(spectral_entropy)
            entropy_threshold = np.mean(spectral_entropy) + 2 * np.std(spectral_entropy)
            
            unusual_entropy_frames = np.where(spectral_entropy > entropy_threshold)[0]
            for frame_idx in unusual_entropy_frames:
                time_sec = librosa.frames_to_time(frame_idx, sr=sample_rate)
                anomalies.append({
                    'type': 'Spectral Anomaly',
                    'time': time_sec,
                    'confidence': min((spectral_entropy[frame_idx] - np.mean(spectral_entropy)) / 
                                    (2 * np.std(spectral_entropy)), 1.0)
                })
            
            # 3. Detect potential compression artifacts
            # Look for specific frequency patterns that might indicate re-encoding
            frequencies = librosa.fft_frequencies(sr=sample_rate)
            avg_magnitude = np.mean(magnitude, axis=1)
            
            # Check for MP3-like artifacts (high-frequency rolloff)
            high_freq_energy = np.sum(avg_magnitude[frequencies > sample_rate * 0.4])
            total_energy = np.sum(avg_magnitude)
            hf_ratio = high_freq_energy / (total_energy + 1e-8)
            
            if hf_ratio < 0.01:  # Very low high-frequency content
                anomalies.append({
                    'type': 'Potential Compression Artifact',
                    'time': 0,  # Applies to entire file
                    'confidence': 1.0 - hf_ratio * 100
                })
            
            # 4. Check for clipping
            clipping_threshold = 0.95 * np.max(np.abs(audio_data))
            clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
            clipping_ratio = clipped_samples / len(audio_data)
            
            if clipping_ratio > 0.001:  # More than 0.1% clipped
                anomalies.append({
                    'type': 'Audio Clipping',
                    'time': 0,
                    'confidence': min(clipping_ratio * 1000, 1.0)
                })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def extract_pitch_features(self, audio_data, sample_rate):
        """Extract pitch and formant features using Parselmouth/Praat"""
        try:
            # Create Parselmouth Sound object
            sound = parselmouth.Sound(audio_data, sampling_frequency=sample_rate)
            
            # Extract pitch
            pitch = sound.to_pitch(pitch_floor=75.0, pitch_ceiling=500.0)
            pitch_values = pitch.selected_array['frequency']
            pitch_values[pitch_values == 0] = np.nan  # Remove unvoiced frames
            
            # Extract formants
            formants = sound.to_formant_burg(maximum_number_of_formants=5, maximum_formant=5500.0)
            
            # Get F1, F2, F3 values
            time_points = formants.ts()
            f1_values = []
            f2_values = []
            f3_values = []
            
            for t in time_points:
                try:
                    f1 = formants.get_value_at_time(1, t)
                    f2 = formants.get_value_at_time(2, t)
                    f3 = formants.get_value_at_time(3, t)
                    f1_values.append(f1 if not np.isnan(f1) else None)
                    f2_values.append(f2 if not np.isnan(f2) else None)
                    f3_values.append(f3 if not np.isnan(f3) else None)
                except:
                    f1_values.append(None)
                    f2_values.append(None)
                    f3_values.append(None)
            
            # Calculate statistics
            valid_pitch = pitch_values[~np.isnan(pitch_values)]
            valid_f1 = [f for f in f1_values if f is not None]
            valid_f2 = [f for f in f2_values if f is not None]
            valid_f3 = [f for f in f3_values if f is not None]
            
            features = {
                'mean_pitch': np.mean(valid_pitch) if len(valid_pitch) > 0 else 0,
                'std_pitch': np.std(valid_pitch) if len(valid_pitch) > 0 else 0,
                'min_pitch': np.min(valid_pitch) if len(valid_pitch) > 0 else 0,
                'max_pitch': np.max(valid_pitch) if len(valid_pitch) > 0 else 0,
                'mean_f1': np.mean(valid_f1) if len(valid_f1) > 0 else 0,
                'mean_f2': np.mean(valid_f2) if len(valid_f2) > 0 else 0,
                'mean_f3': np.mean(valid_f3) if len(valid_f3) > 0 else 0,
                'pitch_range': (np.max(valid_pitch) - np.min(valid_pitch)) if len(valid_pitch) > 0 else 0
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting pitch features: {e}")
            return {}
    
    def detect_background_events(self, audio_data, sample_rate):
        """Detect background events like gunshots, glass breaking, vehicles, etc."""
        try:
            events_detected = []
            
            # 1. Gunshot detection - sudden high-energy broadband event
            # Calculate energy in overlapping windows
            window_size = int(0.1 * sample_rate)  # 100ms windows
            hop_size = int(0.05 * sample_rate)    # 50ms hop
            
            energy_windows = []
            for i in range(0, len(audio_data) - window_size, hop_size):
                window = audio_data[i:i + window_size]
                energy = np.sum(window ** 2)
                energy_windows.append(energy)
            
            energy_windows = np.array(energy_windows)
            
            # Look for sudden energy spikes
            energy_threshold = np.mean(energy_windows) + 4 * np.std(energy_windows)
            gunshot_candidates = np.where(energy_windows > energy_threshold)[0]
            
            for candidate in gunshot_candidates:
                start_time = candidate * hop_size / sample_rate
                
                # Additional verification - check for broadband energy
                window_start = candidate * hop_size
                window_end = window_start + window_size
                window_data = audio_data[window_start:window_end]
                
                # Compute spectrum
                freqs, psd = signal.welch(window_data, sample_rate, nperseg=512)
                
                # Check if energy is distributed across frequencies (broadband)
                low_freq_energy = np.sum(psd[freqs < 1000])
                mid_freq_energy = np.sum(psd[(freqs >= 1000) & (freqs < 4000)])
                high_freq_energy = np.sum(psd[freqs >= 4000])
                
                total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
                
                if (mid_freq_energy > 0.3 * total_energy and 
                    high_freq_energy > 0.2 * total_energy):
                    events_detected.append({
                        'type': 'Potential Gunshot',
                        'time': start_time,
                        'confidence': min(energy_windows[candidate] / energy_threshold - 1, 1.0),
                        'duration': 0.1
                    })
            
            # 2. Glass breaking detection - high-frequency transient
            # High-pass filter to isolate high frequencies
            sos = signal.butter(4, 2000, btype='highpass', fs=sample_rate, output='sos')
            high_freq_audio = signal.sosfilt(sos, audio_data)
            
            # Look for high-frequency transients
            hf_energy_windows = []
            for i in range(0, len(high_freq_audio) - window_size, hop_size):
                window = high_freq_audio[i:i + window_size]
                energy = np.sum(window ** 2)
                hf_energy_windows.append(energy)
            
            hf_energy_windows = np.array(hf_energy_windows)
            hf_threshold = np.mean(hf_energy_windows) + 3 * np.std(hf_energy_windows)
            
            glass_candidates = np.where(hf_energy_windows > hf_threshold)[0]
            for candidate in glass_candidates:
                start_time = candidate * hop_size / sample_rate
                events_detected.append({
                    'type': 'Potential Glass Breaking',
                    'time': start_time,
                    'confidence': min(hf_energy_windows[candidate] / hf_threshold - 1, 1.0),
                    'duration': 0.1
                })
            
            # 3. Vehicle detection - low-frequency rumble
            # Low-pass filter for vehicle sounds
            sos_lp = signal.butter(4, 500, btype='lowpass', fs=sample_rate, output='sos')
            low_freq_audio = signal.sosfilt(sos_lp, audio_data)
            
            # Look for sustained low-frequency energy
            lf_energy_windows = []
            for i in range(0, len(low_freq_audio) - window_size, hop_size):
                window = low_freq_audio[i:i + window_size]
                energy = np.sum(window ** 2)
                lf_energy_windows.append(energy)
            
            lf_energy_windows = np.array(lf_energy_windows)
            
            # Use a lower threshold for sustained detection
            lf_threshold = np.mean(lf_energy_windows) + 1.5 * np.std(lf_energy_windows)
            
            # Find sustained periods
            vehicle_segments = lf_energy_windows > lf_threshold
            
            # Group consecutive segments
            in_vehicle_segment = False
            segment_start = 0
            
            for i, is_vehicle in enumerate(vehicle_segments):
                if is_vehicle and not in_vehicle_segment:
                    in_vehicle_segment = True
                    segment_start = i
                elif not is_vehicle and in_vehicle_segment:
                    in_vehicle_segment = False
                    segment_duration = (i - segment_start) * hop_size / sample_rate
                    
                    # Only report if segment is long enough to be a vehicle
                    if segment_duration > 1.0:  # At least 1 second
                        events_detected.append({
                            'type': 'Potential Vehicle',
                            'time': segment_start * hop_size / sample_rate,
                            'confidence': 0.7,  # Lower confidence for vehicles
                            'duration': segment_duration
                        })
            
            return events_detected
            
        except Exception as e:
            self.logger.error(f"Error detecting background events: {e}")
            return []
    
    def analyze_audio(self, file_path):
        """
        Comprehensive audio analysis - main method called by GUI
        Returns complete analysis results including all audio features
        """
        try:
            self.logger.info(f"Starting comprehensive audio analysis for: {file_path}")
            
            # Initialize results dictionary
            analysis_results = {
                'status': 'success',
                'file_path': str(file_path),
                'timestamp': None,
                'metadata': {},
                'waveform': {},
                'spectrogram': {},
                'noise_analysis': {},
                'anomalies': [],
                'background_events': [],
                'pitch_features': {}
            }
            
            # 1. Extract metadata
            self.logger.info("Extracting audio metadata...")
            metadata = self.extract_metadata(file_path)
            analysis_results['metadata'] = metadata
            
            # 2. Load audio data
            self.logger.info("Loading audio data...")
            audio_data, sample_rate = self.load_audio(file_path)
            
            # 3. Generate waveform data
            self.logger.info("Generating waveform visualization data...")
            waveform_data = self.generate_waveform(audio_data, sample_rate)
            analysis_results['waveform'] = waveform_data
            
            # 4. Generate spectrogram
            self.logger.info("Computing spectrogram...")
            spectrogram_data = self.generate_spectrogram(audio_data, sample_rate)
            analysis_results['spectrogram'] = spectrogram_data
            
            # 5. Noise analysis
            self.logger.info("Analyzing noise characteristics...")
            noise_analysis = self.analyze_noise(audio_data, sample_rate)
            analysis_results['noise_analysis'] = noise_analysis
            
            # 6. Anomaly detection
            self.logger.info("Detecting potential anomalies...")
            anomalies = self.detect_anomalies(audio_data, sample_rate)
            analysis_results['anomalies'] = anomalies
            
            # 7. Background events detection
            self.logger.info("Detecting background events...")
            background_events = self.detect_background_events(audio_data, sample_rate)
            analysis_results['background_events'] = background_events
            
            # 8. Pitch and formant analysis (if Parselmouth is available)
            if PARSELMOUTH_AVAILABLE:
                self.logger.info("Extracting pitch and formant features...")
                pitch_features = self.extract_pitch_features(audio_data, sample_rate)
                analysis_results['pitch_features'] = pitch_features
            else:
                self.logger.warning("Parselmouth not available - skipping pitch analysis")
                analysis_results['pitch_features'] = {}
            
            # 9. Add summary statistics
            analysis_results['summary'] = {
                'duration_seconds': metadata.get('duration', 0),
                'sample_rate': sample_rate,
                'total_anomalies': len(anomalies),
                'background_events_count': len(background_events),
                'estimated_snr_db': noise_analysis.get('snr_estimate_db', 0),
                'speech_activity_ratio': noise_analysis.get('speech_ratio', 0),
                'audio_quality': self.assess_audio_quality(noise_analysis, anomalies)
            }
            
            # Add timestamp
            analysis_results['timestamp'] = datetime.now().isoformat()
            
            self.logger.info("Audio analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive audio analysis: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'file_path': str(file_path),
                'timestamp': datetime.now().isoformat()
            }
    
    def assess_audio_quality(self, noise_analysis, anomalies):
        """Assess overall audio quality based on analysis results"""
        try:
            quality_score = 100  # Start with perfect score
            
            # Deduct for poor SNR
            snr = noise_analysis.get('snr_estimate_db', 20)
            if snr < 10:
                quality_score -= 30
            elif snr < 15:
                quality_score -= 15
            
            # Deduct for low speech activity
            speech_ratio = noise_analysis.get('speech_ratio', 1.0)
            if speech_ratio < 0.3:
                quality_score -= 20
            elif speech_ratio < 0.5:
                quality_score -= 10
            
            # Deduct for anomalies
            high_confidence_anomalies = [a for a in anomalies if a.get('confidence', 0) > 0.7]
            quality_score -= len(high_confidence_anomalies) * 10
            
            # Ensure score doesn't go below 0
            quality_score = max(0, quality_score)
            
            # Convert to quality rating
            if quality_score >= 80:
                return 'Excellent'
            elif quality_score >= 60:
                return 'Good'
            elif quality_score >= 40:
                return 'Fair'
            else:
                return 'Poor'
                
        except Exception as e:
            self.logger.error(f"Error assessing audio quality: {e}")
            return 'Unknown'
    
    def save_processed_audio(self, audio_data, sample_rate, output_path):
        """Save processed audio to file"""
        try:
            sf.write(output_path, audio_data, sample_rate)
            self.logger.info(f"Saved processed audio to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving audio: {e}")
            raise
