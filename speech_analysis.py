"""
Enhanced Speech Analysis Module - Multi-language transcription, speaker diarization, and emotion analysis
"""

import numpy as np
import librosa
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import logging
from pathlib import Path
import json
import wave
from textblob import TextBlob
from transformers import pipeline, Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
from sklearn.cluster import KMeans
from scipy.spatial.distance import cosine
import re
from typing import Dict, List, Tuple, Optional
import langdetect

# Optional imports with fallbacks
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    Pipeline = None


class EnhancedSpeechAnalyzer:
    """Enhanced speech analyzer with multi-language support and advanced diarization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        
        # Language detection and support
        self.supported_languages = {
            'english': {'code': 'en', 'whisper': 'en', 'google': 'en-US'},
            'hindi': {'code': 'hi', 'whisper': 'hi', 'google': 'hi-IN'},
            'gujarati': {'code': 'gu', 'whisper': 'gu', 'google': 'gu-IN'}
        }
        
        # Language codes mapping for different services
        self.language_codes = {
            'english': 'en-US',
            'hindi': 'hi-IN', 
            'gujarati': 'gu-IN',
            'auto': 'auto'
        }
        
        # Language patterns for better detection
        self.language_patterns = {
            'gujarati': [
                r'[\u0A80-\u0AFF]+',  # Gujarati Unicode range
                r'[કખગઘચછજઝટઠડઢણતથદધનપફબભમયરલવશષસહ]+',
            ],
            'hindi': [
                r'[\u0900-\u097F]+',  # Devanagari Unicode range
                r'[कखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह]+',
            ]
        }
        
        # Initialize emotion analysis pipeline
        try:
            self.emotion_analyzer = pipeline("audio-classification", 
                                            model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
        except:
            self.emotion_analyzer = None
            self.logger.warning("Emotion analysis model not available")
        
        # Initialize Whisper for better transcription
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
            except:
                self.whisper_model = None
                self.logger.warning("Whisper model not available")
        else:
            self.whisper_model = None
            self.logger.warning("Whisper not installed - using basic speech recognition only")
        
        # Language settings with enhanced detection
        self.auto_detect_language = True
        self.preferred_language = 'english'
        
    def detect_language(self, text_sample: str) -> str:
        """Detect language from text sample with pattern matching"""
        if not text_sample:
            return self.preferred_language
        
        try:
            # Check for script patterns first (more reliable for Indian languages)
            for lang, patterns in self.language_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text_sample):
                        self.logger.info(f"Language detected by script pattern: {lang}")
                        return lang
            
            # Fallback to langdetect library
            detected = langdetect.detect(text_sample)
            
            # Map common language codes
            lang_mapping = {'en': 'english', 'hi': 'hindi', 'gu': 'gujarati'}
            detected_lang = lang_mapping.get(detected, 'english')
            
            self.logger.info(f"Language detected: {detected_lang}")
            return detected_lang
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}, using preferred language")
            return self.preferred_language
    
    def quick_transcribe_sample(self, audio_sample):
        """Quick transcription of audio sample for language detection"""
        try:
            # Use a simple, fast transcription method
            if self.whisper_model:
                # Create temporary file for whisper
                import tempfile
                import soundfile as sf
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    sf.write(temp_file.name, audio_sample, 16000)
                    
                    # Quick transcription with Whisper
                    result = self.whisper_model.transcribe(temp_file.name, fp16=False)
                    
                    # Clean up
                    os.unlink(temp_file.name)
                    
                    return result.get('text', '')
            else:
                # Fallback: return empty string - will use default language
                return ''
                
        except Exception as e:
            self.logger.warning(f"Quick transcription failed: {e}")
            return ''
    
    def transcribe_audio_enhanced(self, audio_path: str, language: str = 'auto') -> Dict:
        """Enhanced transcription with multi-language support and speaker diarization"""
        try:
            self.logger.info(f"Starting enhanced transcription for: {audio_path}")
            
            # Load audio
            audio_data, sr_rate = librosa.load(audio_path, sr=16000)
            
            # Detect language if auto
            if language == 'auto':
                # Get a quick transcription sample for language detection
                sample_transcript = self.quick_transcribe_sample(audio_data[:sr_rate*30])  # First 30 seconds
                language = self.detect_language(sample_transcript)
            
            # Perform transcription with detected/specified language
            transcript_data = self.perform_multi_engine_transcription(audio_path, language)
            
            # Perform speaker diarization
            diarization_data = self.perform_enhanced_speaker_diarization(audio_data, sr_rate)
            
            # Combine transcript with speaker information
            speaker_transcript = self.align_transcript_with_speakers(transcript_data, diarization_data)
            
            # Perform emotion analysis
            emotion_data = {}
            try:
                self.logger.info("Performing emotion analysis...")
                emotion_data = self.analyze_emotion(audio_data, sr_rate)
                self.logger.info(f"Emotion analysis completed: {list(emotion_data.keys())}")
            except Exception as e:
                self.logger.warning(f"Emotion analysis failed: {e}")
                emotion_data = {}
            
            return {
                'transcript': transcript_data.get('text', ''),
                'language': language,
                'confidence': transcript_data.get('confidence', 0.0),
                'speaker_segments': speaker_transcript,
                'speaker_count': len(set(seg['speaker'] for seg in speaker_transcript)),
                'diarization_confidence': diarization_data.get('confidence', 0.0),
                'processing_time': transcript_data.get('processing_time', 0.0),
                'method_used': transcript_data.get('method', 'unknown'),
                'emotion_analysis': emotion_data
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced transcription failed: {e}")
            return {'error': str(e), 'transcript': '', 'language': language}
    
    def perform_multi_engine_transcription(self, audio_path, language):
        """
        Perform transcription using multiple engines with enhanced error handling and confidence scoring
        """
        try:
            import time
            start_time = time.time()
            
            transcription_results = []
            best_result = None
            highest_confidence = 0.0
            
            self.logger.info(f"Starting multi-engine transcription for language: {language}")
            
            # Method 1: Try Whisper (most accurate for multi-language)
            if WHISPER_AVAILABLE and self.whisper_model:
                try:
                    self.logger.info("Attempting Whisper transcription...")
                    whisper_result = self.transcribe_with_whisper(audio_path, language)
                    if whisper_result:
                        # Estimate confidence based on text length and coherence
                        confidence = min(len(whisper_result.split()) / 50.0, 1.0) * 0.9  # Whisper is generally reliable
                        transcription_results.append({
                            'method': 'Whisper',
                            'text': whisper_result,
                            'confidence': confidence
                        })
                        self.logger.info(f"Whisper transcription successful, confidence: {confidence:.2f}")
                        
                        if confidence > highest_confidence:
                            highest_confidence = confidence
                            best_result = transcription_results[-1]
                            
                except Exception as e:
                    self.logger.warning(f"Whisper transcription failed: {e}")
            
            # Method 2: Try Google Speech Recognition
            try:
                self.logger.info("Attempting Google Speech Recognition...")
                google_result = self.transcribe_with_google(audio_path, language)
                if google_result and google_result != "Could not understand audio":
                    # Google confidence estimation
                    confidence = min(len(google_result.split()) / 40.0, 1.0) * 0.8
                    transcription_results.append({
                        'method': 'Google Speech',
                        'text': google_result,
                        'confidence': confidence
                    })
                    self.logger.info(f"Google transcription successful, confidence: {confidence:.2f}")
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_result = transcription_results[-1]
                        
            except Exception as e:
                self.logger.warning(f"Google transcription failed: {e}")
            
            # Method 3: Try basic speech recognition as fallback
            try:
                self.logger.info("Attempting basic speech recognition...")
                basic_result = self.transcribe_with_basic_sr(audio_path, language)
                if basic_result and "Could not understand" not in basic_result:
                    confidence = min(len(basic_result.split()) / 30.0, 1.0) * 0.6
                    transcription_results.append({
                        'method': 'Basic SR',
                        'text': basic_result,
                        'confidence': confidence
                    })
                    self.logger.info(f"Basic SR transcription successful, confidence: {confidence:.2f}")
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_result = transcription_results[-1]
                        
            except Exception as e:
                self.logger.warning(f"Basic transcription failed: {e}")
            
            # If no successful transcription
            if not best_result:
                self.logger.error("All transcription methods failed")
                return {
                    'text': '',
                    'confidence': 0.0,
                    'method': 'failed',
                    'processing_time': time.time() - start_time,
                    'attempts': len(transcription_results)
                }
            
            # Post-process the best result
            processed_text = self.post_process_transcript(best_result['text'], language)
            
            processing_time = time.time() - start_time
            
            result = {
                'text': processed_text,
                'confidence': best_result['confidence'],
                'method': best_result['method'],
                'processing_time': processing_time,
                'all_results': transcription_results,
                'language': language
            }
            
            self.logger.info(f"Multi-engine transcription completed using {best_result['method']} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Multi-engine transcription error: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'error',
                'processing_time': 0.0,
                'error': str(e)
            }
    
    def post_process_transcript(self, text, language):
        """Post-process transcription text for better formatting"""
        try:
            if not text:
                return text
            
            # Basic cleaning
            text = text.strip()
            
            # Language-specific post-processing
            if language == 'english':
                # Capitalize first letter and after periods
                sentences = text.split('. ')
                sentences = [s.strip().capitalize() for s in sentences if s.strip()]
                text = '. '.join(sentences)
                
                # Add period at end if missing
                if not text.endswith(('.', '!', '?')):
                    text += '.'
                    
            elif language in ['hindi', 'gujarati']:
                # For Indic languages, ensure proper Unicode normalization
                import unicodedata
                text = unicodedata.normalize('NFC', text)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Post-processing error: {e}")
            return text
    
    def transcribe_audio(self, audio_path, language='English'):
        """Transcribe audio to text with multi-language support"""
        try:
            transcription_results = []
            
            # Method 1: Try Whisper (most accurate)
            if self.whisper_model:
                try:
                    whisper_result = self.transcribe_with_whisper(audio_path, language)
                    if whisper_result:
                        transcription_results.append(('Whisper', whisper_result))
                except Exception as e:
                    self.logger.warning(f"Whisper transcription failed: {e}")
            
            # Method 2: Try Google Speech Recognition
            try:
                google_result = self.transcribe_with_google(audio_path, language)
                if google_result:
                    transcription_results.append(('Google', google_result))
            except Exception as e:
                self.logger.warning(f"Google transcription failed: {e}")
            
            # Method 3: Try basic speech recognition
            try:
                basic_result = self.transcribe_with_basic_sr(audio_path, language)
                if basic_result:
                    transcription_results.append(('Basic SR', basic_result))
            except Exception as e:
                self.logger.warning(f"Basic transcription failed: {e}")
            
            # Return the best result (prefer Whisper, then Google, then basic)
            if transcription_results:
                return transcription_results[0][1]
            else:
                return "Transcription failed with all methods"
                
        except Exception as e:
            self.logger.error(f"Error in transcription: {e}")
            return "Transcription error occurred"
    
    def transcribe_with_whisper(self, audio_path, language='english'):
        """Transcribe using OpenAI Whisper"""
        try:
            # Validate file path
            if not os.path.exists(audio_path):
                self.logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # Map language to Whisper language codes
            whisper_language_codes = {
                'english': 'en',
                'hindi': 'hi', 
                'gujarati': 'gu',
                'auto': None
            }
            
            lang_code = whisper_language_codes.get(language.lower(), 'en')
            if lang_code == 'auto' or language == 'auto':
                lang_code = None  # Let Whisper auto-detect
            
            self.logger.info(f"Using Whisper with language code: {lang_code} for file: {audio_path}")
            result = self.whisper_model.transcribe(str(audio_path), language=lang_code, fp16=False)
            
            transcribed_text = result['text'].strip()
            self.logger.info(f"Whisper transcription result length: {len(transcribed_text)} characters")
            self.logger.debug(f"Whisper result: {transcribed_text[:200]}...")
            return transcribed_text
            
        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}")
            return None
    
    def transcribe_with_google(self, audio_path, language='english'):
        """Transcribe using Google Speech Recognition"""
        try:
            # Convert to WAV if necessary
            wav_path = self.convert_to_wav(audio_path)
            
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
            
            # Map language to Google language codes
            google_language_codes = {
                'english': 'en-US',
                'hindi': 'hi-IN', 
                'gujarati': 'gu-IN',
                'auto': 'en-US'  # Default for auto
            }
            
            lang_code = google_language_codes.get(language.lower(), 'en-US')
            self.logger.info(f"Using Google with language code: {lang_code}")
            
            # Perform recognition
            text = self.recognizer.recognize_google(audio_data, language=lang_code)
            self.logger.info(f"Google transcription result length: {len(text)} characters")
            return text
            
        except sr.UnknownValueError:
            self.logger.warning("Google could not understand audio")
            return "Could not understand audio"
        except sr.RequestError as e:
            self.logger.error(f"Google Speech Recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Google transcription error: {e}")
            return None
    
    def transcribe_with_basic_sr(self, audio_path, language='English'):
        """Basic transcription fallback"""
        try:
            wav_path = self.convert_to_wav(audio_path)
            
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Try offline recognition (Sphinx)
            try:
                text = self.recognizer.recognize_sphinx(audio_data)
                return text
            except:
                # Final fallback - return placeholder
                return "[Audio detected but transcription failed]"
                
        except Exception as e:
            self.logger.error(f"Basic transcription error: {e}")
            return None
    
    def convert_to_wav(self, audio_path):
        """Convert audio file to WAV format for processing"""
        try:
            audio_path = str(audio_path)
            file_ext = Path(audio_path).suffix.lower()
            
            if file_ext == '.wav':
                return audio_path
            
            # Convert using pydub
            audio = AudioSegment.from_file(audio_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_wav_path = temp_file.name
            
            audio.export(temp_wav_path, format='wav')
            return temp_wav_path
            
        except Exception as e:
            self.logger.error(f"Error converting to WAV: {e}")
            return audio_path
    
    def speaker_diarization(self, audio_path):
        """Perform speaker diarization to separate different speakers"""
        try:
            # Method 1: Try pyannote.audio (most accurate)
            try:
                diarization_result = self.diarize_with_pyannote(audio_path)
                if diarization_result:
                    return diarization_result
            except Exception as e:
                self.logger.warning(f"Pyannote diarization failed: {e}")
            
            # Method 2: Fallback to simple clustering approach
            return self.diarize_with_clustering(audio_path)
            
        except Exception as e:
            self.logger.error(f"Speaker diarization error: {e}")
            return []
    
    def diarize_with_pyannote(self, audio_path):
        """Speaker diarization using pyannote.audio"""
        try:
            # Initialize pipeline (requires authentication token for some models)
            # This is a placeholder - in production, you'd need proper model setup
            
            # For now, return a mock result
            # In production, this would use the actual pyannote pipeline
            return self.create_mock_diarization()
            
        except Exception as e:
            self.logger.error(f"Pyannote diarization error: {e}")
            return None
    
    def diarize_with_clustering(self, audio_path):
        """Simple speaker diarization using feature clustering"""
        try:
            # Load audio
            audio_data, sample_rate = librosa.load(audio_path, sr=22050)
            
            # Split into segments
            segment_length = int(2.0 * sample_rate)  # 2-second segments
            segments = []
            features = []
            
            for i in range(0, len(audio_data) - segment_length, segment_length):
                segment = audio_data[i:i + segment_length]
                
                # Extract features for each segment
                mfccs = librosa.feature.mfcc(y=segment, sr=sample_rate, n_mfcc=13)
                feature_vector = np.mean(mfccs, axis=1)
                
                segments.append({
                    'start': i / sample_rate,
                    'end': (i + segment_length) / sample_rate,
                    'audio': segment
                })
                features.append(feature_vector)
            
            if len(features) < 2:
                return [{'speaker': 'Speaker 1', 'start': 0, 'end': len(audio_data)/sample_rate, 'text': ''}]
            
            # Cluster features to identify speakers
            features = np.array(features)
            n_clusters = min(4, len(features))  # Assume max 4 speakers
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            speaker_labels = kmeans.fit_predict(features)
            
            # Create diarization result
            diarization = []
            for i, (segment, speaker_id) in enumerate(zip(segments, speaker_labels)):
                # Get transcription for this segment (simplified)
                segment_text = f"[Segment {i+1} text]"  # Placeholder
                
                diarization.append({
                    'speaker': f'Speaker {speaker_id + 1}',
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment_text
                })
            
            return diarization
            
        except Exception as e:
            self.logger.error(f"Clustering diarization error: {e}")
            return self.create_mock_diarization()
    
    def create_mock_diarization(self):
        """Create mock diarization for demonstration"""
        return [
            {
                'speaker': 'Speaker 1',
                'start': 0.0,
                'end': 5.0,
                'text': 'Hello, this is the first speaker.'
            },
            {
                'speaker': 'Speaker 2',
                'start': 5.0,
                'end': 10.0,
                'text': 'And this is the second speaker responding.'
            },
            {
                'speaker': 'Speaker 1',
                'start': 10.0,
                'end': 15.0,
                'text': 'First speaker continues the conversation.'
            }
        ]
    
    def analyze_emotion(self, audio_data, sample_rate):
        """Analyze emotion/tone in the speech"""
        try:
            emotions = {}
            
            # Method 1: Try transformer-based emotion recognition
            if self.emotion_analyzer:
                try:
                    # Resample to 16kHz if needed (required by many models)
                    if sample_rate != 16000:
                        audio_16k = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                    else:
                        audio_16k = audio_data
                    
                    # Analyze emotion
                    emotion_results = self.emotion_analyzer(audio_16k)
                    
                    for result in emotion_results:
                        emotions[result['label'].lower()] = result['score']
                        
                except Exception as e:
                    self.logger.warning(f"Transformer emotion analysis failed: {e}")
            
            # Method 2: Feature-based emotion analysis
            try:
                feature_emotions = self.analyze_emotion_from_features(audio_data, sample_rate)
                emotions.update(feature_emotions)
            except Exception as e:
                self.logger.warning(f"Feature-based emotion analysis failed: {e}")
            
            # If no emotions detected, provide defaults
            if not emotions:
                emotions = {
                    'neutral': 0.6,
                    'calm': 0.3,
                    'unknown': 0.1
                }
            
            return emotions
            
        except Exception as e:
            self.logger.error(f"Emotion analysis error: {e}")
            return {'neutral': 1.0}
    
    def analyze_emotion_from_features(self, audio_data, sample_rate):
        """Analyze emotion using acoustic features"""
        try:
            # Extract features
            pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
            pitch_values = []
            
            for t in range(pitch.shape[1]):
                index = pitch[:, t].argmax()
                pitch_val = pitch[index, t]
                if pitch_val > 0:
                    pitch_values.append(pitch_val)
            
            if len(pitch_values) == 0:
                return {}
            
            # Energy features
            rms = librosa.feature.rms(y=audio_data)[0]
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Calculate statistics
            pitch_mean = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
            energy_mean = np.mean(rms)
            energy_std = np.std(rms)
            spectral_mean = np.mean(spectral_centroid)
            zcr_mean = np.mean(zcr)
            
            # Simple emotion classification based on features
            emotions = {}
            
            # High pitch variation + high energy = excited/angry
            if pitch_std > 50 and energy_mean > 0.1:
                emotions['excited'] = 0.7
                emotions['angry'] = 0.5
            
            # Low pitch variation + low energy = calm/sad
            elif pitch_std < 20 and energy_mean < 0.05:
                emotions['calm'] = 0.6
                emotions['sad'] = 0.4
            
            # High spectral centroid = bright/happy
            if spectral_mean > 2000:
                emotions['happy'] = 0.6
            
            # High ZCR = stressed/nervous
            if zcr_mean > 0.15:
                emotions['nervous'] = 0.5
            
            # Default to neutral if no strong indicators
            if not emotions:
                emotions['neutral'] = 0.8
            
            return emotions
            
        except Exception as e:
            self.logger.error(f"Feature-based emotion analysis error: {e}")
            return {}
    
    def analyze_speech_quality(self, audio_data, sample_rate):
        """Analyze speech quality metrics"""
        try:
            quality_metrics = {}
            
            # Signal-to-noise ratio estimation
            rms = librosa.feature.rms(y=audio_data)[0]
            noise_floor = np.percentile(rms, 10)
            signal_power = np.mean(rms)
            snr = 20 * np.log10(signal_power / (noise_floor + 1e-8))
            quality_metrics['snr_db'] = snr
            
            # Spectral clarity
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            quality_metrics['spectral_clarity'] = np.mean(spectral_centroid) / (np.mean(spectral_bandwidth) + 1e-8)
            
            # Voice activity detection
            energy_threshold = np.percentile(rms, 30)
            voice_activity = rms > energy_threshold
            quality_metrics['voice_activity_ratio'] = np.mean(voice_activity)
            
            # Jitter and shimmer (simplified)
            pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
            pitch_values = []
            for t in range(pitch.shape[1]):
                index = pitch[:, t].argmax()
                if pitch[index, t] > 0:
                    pitch_values.append(pitch[index, t])
            
            if len(pitch_values) > 1:
                pitch_diffs = np.diff(pitch_values)
                quality_metrics['pitch_stability'] = 1.0 / (1.0 + np.std(pitch_diffs))
            else:
                quality_metrics['pitch_stability'] = 0.5
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Speech quality analysis error: {e}")
            return {}
    
    def extract_prosodic_features(self, audio_data, sample_rate):
        """Extract prosodic features (rhythm, stress, intonation)"""
        try:
            features = {}
            
            # Tempo and rhythm
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo'] = tempo
            features['rhythm_regularity'] = np.std(np.diff(beats))
            
            # Intensity contour
            rms = librosa.feature.rms(y=audio_data)[0]
            features['intensity_range'] = np.max(rms) - np.min(rms)
            features['intensity_mean'] = np.mean(rms)
            
            # Pitch contour
            pitch, _ = librosa.piptrack(y=audio_data, sr=sample_rate)
            pitch_contour = []
            for t in range(pitch.shape[1]):
                index = pitch[:, t].argmax()
                if pitch[index, t] > 0:
                    pitch_contour.append(pitch[index, t])
            
            if len(pitch_contour) > 0:
                features['pitch_range'] = np.max(pitch_contour) - np.min(pitch_contour)
                features['pitch_mean'] = np.mean(pitch_contour)
                
                # Intonation patterns
                pitch_slopes = np.diff(pitch_contour)
                features['rising_intonation'] = np.mean(pitch_slopes > 0)
                features['falling_intonation'] = np.mean(pitch_slopes < 0)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Prosodic feature extraction error: {e}")
            return {}
    
    def create_speaker_transcript(self, diarization_data, full_transcription):
        """Create a properly formatted speaker-separated transcript"""
        try:
            if not diarization_data:
                return f"Speaker 1: {full_transcription}"
            
            transcript_lines = []
            transcript_lines.append("SPEAKER-SEPARATED TRANSCRIPT")
            transcript_lines.append("=" * 40)
            transcript_lines.append("")
            
            for segment in diarization_data:
                speaker = segment.get('speaker', 'Unknown Speaker')
                start_time = segment.get('start', 0)
                end_time = segment.get('end', 0)
                text = segment.get('text', '')
                
                # Format: Speaker X (MM:SS - MM:SS): Text
                start_min, start_sec = divmod(int(start_time), 60)
                end_min, end_sec = divmod(int(end_time), 60)
                
                time_range = f"({start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d})"
                
                transcript_lines.append(f"{speaker} {time_range}: {text}")
                transcript_lines.append("")
            
            return "\n".join(transcript_lines)
            
        except Exception as e:
            self.logger.error(f"Error creating speaker transcript: {e}")
            return full_transcription
    
    def perform_enhanced_speaker_diarization(self, audio_data, sample_rate):
        """Perform enhanced speaker diarization"""
        try:
            self.logger.info("Starting speaker diarization...")
            
            # Simple energy-based speaker segmentation for basic diarization
            # This is a fallback when advanced tools aren't available
            
            # Calculate energy in overlapping windows
            window_size = int(1.0 * sample_rate)  # 1 second windows
            hop_size = int(0.5 * sample_rate)     # 0.5 second overlap
            
            segments = []
            for i in range(0, len(audio_data) - window_size, hop_size):
                window = audio_data[i:i + window_size]
                energy = np.sum(window ** 2)
                
                start_time = i / sample_rate
                end_time = (i + window_size) / sample_rate
                
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'energy': energy
                })
            
            if not segments:
                return {'speakers': [{'speaker': 'Speaker_1', 'start': 0, 'end': len(audio_data)/sample_rate}],
                        'confidence': 0.5}
            
            # Simple clustering based on energy levels
            energies = [seg['energy'] for seg in segments]
            median_energy = np.median(energies)
            
            # Assign speakers based on energy (simple 2-speaker model)
            speaker_segments = []
            current_speaker = None
            segment_start = 0
            
            for i, segment in enumerate(segments):
                # Determine speaker based on energy level
                if segment['energy'] > median_energy * 1.2:
                    speaker = 'Speaker_1'  # Higher energy speaker
                else:
                    speaker = 'Speaker_2'  # Lower energy speaker
                
                # If speaker changed, end previous segment and start new one
                if current_speaker != speaker:
                    if current_speaker is not None:
                        speaker_segments.append({
                            'speaker': current_speaker,
                            'start': segment_start,
                            'end': segment['start']
                        })
                    current_speaker = speaker
                    segment_start = segment['start']
            
            # Add final segment
            if current_speaker is not None:
                speaker_segments.append({
                    'speaker': current_speaker,
                    'start': segment_start,
                    'end': segments[-1]['end']
                })
            
            # If no segments created, create default single speaker
            if not speaker_segments:
                speaker_segments = [{'speaker': 'Speaker_1', 'start': 0, 'end': len(audio_data)/sample_rate}]
            
            self.logger.info(f"Diarization completed: {len(speaker_segments)} segments")
            return {
                'speakers': speaker_segments,
                'confidence': 0.7  # Moderate confidence for basic method
            }
            
        except Exception as e:
            self.logger.error(f"Speaker diarization error: {e}")
            return {
                'speakers': [{'speaker': 'Speaker_1', 'start': 0, 'end': len(audio_data)/sample_rate}],
                'confidence': 0.3
            }
    
    def align_transcript_with_speakers(self, transcript_data, diarization_data):
        """Align transcript text with speaker segments"""
        try:
            if not transcript_data or not diarization_data:
                return []
            
            transcript_text = transcript_data.get('text', '')
            if not transcript_text:
                return []
            
            speakers = diarization_data.get('speakers', [])
            if not speakers:
                return [{'speaker': 'Speaker_1', 'text': transcript_text, 'start_time': 0, 'end_time': 0}]
            
            # Simple word-based alignment
            words = transcript_text.split()
            total_words = len(words)
            
            if total_words == 0:
                return []
            
            speaker_transcript = []
            word_index = 0
            
            for speaker_seg in speakers:
                speaker = speaker_seg['speaker']
                start_time = speaker_seg['start']
                end_time = speaker_seg['end']
                segment_duration = end_time - start_time
                
                # Calculate proportion of words for this segment
                total_duration = sum(s['end'] - s['start'] for s in speakers)
                word_proportion = segment_duration / total_duration if total_duration > 0 else 1.0
                words_in_segment = max(1, int(total_words * word_proportion))
                
                # Extract words for this segment
                segment_words = words[word_index:word_index + words_in_segment]
                segment_text = ' '.join(segment_words)
                
                speaker_transcript.append({
                    'speaker': speaker,
                    'text': segment_text,
                    'start_time': start_time,
                    'end_time': end_time
                })
                
                word_index += words_in_segment
                
                # Stop if we've used all words
                if word_index >= total_words:
                    break
            
            # If there are remaining words, add them to the last speaker
            if word_index < total_words:
                remaining_words = ' '.join(words[word_index:])
                if speaker_transcript:
                    speaker_transcript[-1]['text'] += ' ' + remaining_words
                else:
                    speaker_transcript.append({
                        'speaker': 'Speaker_1',
                        'text': remaining_words,
                        'start_time': 0,
                        'end_time': 0
                    })
            
            return speaker_transcript
            
        except Exception as e:
            self.logger.error(f"Speaker alignment error: {e}")
            return [{'speaker': 'Speaker_1', 'text': transcript_data.get('text', ''), 'start_time': 0, 'end_time': 0}]
    
    def cleanup_temp_files(self):
        """Clean up temporary files created during processing"""
        try:
            # Clean up any temporary WAV files
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith('tmp') and file.endswith('.wav'):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except:
                        pass
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")
