# Forensic Audio Analysis Tool

A comprehensive Python-based GUI application for forensic audio analysis with advanced features including speech recognition, speaker diarization, keyword detection, and AI-powered insights.

## Features

### Core Functionality
- **Audio Input Options**
  - Record live audio from microphone
  - Upload audio files (.wav, .mp3, .aac, .flac, .ogg, .m4a)

### Forensic Analysis Capabilities
- **Basic Audio Properties**: Duration, sample rate, channels, bit depth, file size, format
- **Visualizations**: Waveform and spectrogram generation
- **Noise Analysis**: Background noise profiling and SNR estimation
- **Speech-to-Text**: Multi-language transcription (English, Hindi, Gujarati)
- **Speaker Diarization**: Identify and separate multiple speakers
- **Voice Analysis**: Pitch, frequency, and formant analysis for voice profiling
- **Emotion Detection**: Tone and emotion analysis in speech
- **Anomaly Detection**: Detect tampering, compression artifacts, and audio edits
- **Background Events**: Detect gunshots, glass breaking, vehicles, and other events

### Keyword & Crime Detection
- **Multi-language Keyword Detection**: Crime-related terms in English, Hindi, Gujarati
- **Context Analysis**: NLP-powered sentence-level criminal intent detection
- **Crime Categories**: Violence, drugs, theft, terrorism, organized crime
- **Keyword Highlighting**: Visual highlighting of detected terms

### AI-Powered Insights
- **ChatGPT Integration**: Generate forensic insights and summaries
- **Speaker Role Analysis**: Identify caller/receiver relationships
- **Investigation Recommendations**: AI-generated action items
- **Criminal Assessment**: Threat level and priority analysis

### Professional Reporting
- **Comprehensive Reports**: Auto-generate detailed forensic reports
- **Multiple Formats**: Export as PDF and DOCX
- **Visual Elements**: Include waveforms, spectrograms, and charts
- **Legal Standards**: Professional formatting for law enforcement use

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Quick Setup

1. **Clone or download the project**
   ```bash
   cd Audio
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Start the application**
   ```bash
   python main.py
   ```

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download NLTK data**
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

3. **Configure OpenAI API (optional)**
   - Add your OpenAI API key to `config.json`
   - This enables advanced AI analysis features

## Configuration

### OpenAI API Setup
To enable AI-powered insights, add your OpenAI API key to `config.json`:
```json
{
  "openai_api_key": "your-api-key-here"
}
```

### Audio Settings
Adjust audio processing settings in `config.json`:
```json
{
  "audio_settings": {
    "target_sample_rate": 22050,
    "chunk_size": 1024,
    "recording_format": "wav"
  }
}
```

## Usage

### Basic Workflow

1. **Launch the Application**
   ```bash
   python main.py
   ```

2. **Load Audio File**
   - Click "Upload Audio File" to select a file
   - Or use "Record Audio" for live recording

3. **Configure Analysis Options**
   - Select desired analysis features
   - Choose language for transcription
   - Enable/disable AI analysis

4. **Start Analysis**
   - Click "Start Analysis"
   - Monitor progress in real-time
   - View results in different tabs

5. **Generate Report**
   - Select report format (PDF/DOCX)
   - Click "Generate Report"
   - Choose output directory

### User Interface

The application features a modern GUI with:
- **Sidebar**: File input, analysis options, controls
- **Main Tabs**: 
  - Overview: File info and summary
  - Audio Analysis: Waveforms and spectrograms
  - Speech Analysis: Transcription and speakers
  - Keywords: Detected crime-related terms
  - AI Insights: ChatGPT-generated analysis
  - Report: Preview and export

## Architecture

### Code Organization

```
Audio/
├── main.py                 # Application entry point
├── gui.py                  # GUI interface (PyQt6)
├── audio_processing.py     # Audio analysis and processing
├── speech_analysis.py      # Transcription and speaker diarization
├── keyword_detection.py    # NLP and keyword detection
├── forensic_ai.py         # ChatGPT API integration
├── report_generator.py    # PDF/DOCX report generation
├── config.json            # Configuration settings
├── requirements.txt       # Python dependencies
├── setup.py              # Installation script
└── README.md             # Documentation
```

### Key Technologies

- **GUI**: PyQt6 for modern cross-platform interface
- **Audio Processing**: Librosa, PyAudio, SoundFile
- **Speech Recognition**: SpeechRecognition, Whisper, pyannote.audio
- **NLP**: NLTK, TextBlob, spaCy, transformers
- **AI Integration**: OpenAI GPT API
- **Visualization**: PyQtGraph, Matplotlib
- **Reports**: ReportLab (PDF), python-docx (DOCX)

## Features in Detail

### Speech Analysis
- **Multi-Engine Transcription**: Uses Whisper, Google Speech API, and fallback engines
- **Speaker Diarization**: Identifies multiple speakers with timestamps
- **Emotion Analysis**: Detects stress, anger, fear, and other emotions
- **Voice Profiling**: Pitch analysis, formant extraction using Praat/Parselmouth

### Keyword Detection
- **Multi-language Support**: English, Hindi, Gujarati keyword databases
- **Crime Categories**: Violence, drugs, theft, terrorism, organized crime
- **Context Analysis**: Sentence-level intent detection
- **Confidence Scoring**: Reliability metrics for each detection

### Anomaly Detection
- **Tampering Detection**: Identifies cuts, edits, and splicing
- **Compression Artifacts**: Detects re-encoding and quality loss
- **Clipping Detection**: Identifies audio distortion
- **Spectral Anomalies**: Unusual frequency patterns

### AI Analysis
- **Forensic Summary**: Overall case assessment
- **Speaker Analysis**: Relationship and role identification
- **Crime Assessment**: Threat level and evidence strength
- **Recommendations**: Investigation priorities and next steps

## Supported Audio Formats

- WAV (recommended for best quality)
- MP3
- AAC
- FLAC
- OGG
- M4A

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Python**: 3.8+

### Recommended for Optimal Performance
- **RAM**: 8GB+
- **CPU**: Multi-core processor
- **GPU**: NVIDIA GPU for ML models (optional)
- **Internet**: For AI features and speech recognition

## Troubleshooting

### Common Issues

1. **Audio Loading Failed**
   - Check file format compatibility
   - Ensure file is not corrupted
   - Try converting to WAV format

2. **Transcription Not Working**
   - Check internet connection for Google Speech API
   - Install Whisper for offline transcription
   - Verify audio quality and clarity

3. **AI Features Unavailable**
   - Add OpenAI API key to config.json
   - Check API key validity and credits
   - Verify internet connection

4. **Dependencies Missing**
   - Run setup.py again
   - Install packages manually: `pip install -r requirements.txt`
   - Check Python version compatibility

### Performance Tips

- Use WAV files for best quality and speed
- Enable only necessary analysis features
- Close other applications during analysis
- Use SSD storage for better I/O performance

## Legal and Ethical Considerations

### Intended Use
This tool is designed for:
- Law enforcement investigations
- Forensic audio analysis
- Security and surveillance analysis
- Academic research

### Important Notes
- Ensure proper legal authorization before analyzing audio
- Maintain chain of custody for evidence
- Follow local laws regarding audio recording and analysis
- Results should be verified by qualified forensic experts

### Limitations
- AI analysis is advisory and not definitive proof
- Keyword detection may have false positives/negatives
- Speaker diarization accuracy depends on audio quality
- Emotion detection is based on vocal patterns, not absolute truth

## License

This project is intended for law enforcement and academic use. Please ensure compliance with local laws and regulations.

## Support

For technical support:
1. Check this README for common issues
2. Review log files in the `logs/` directory
3. Verify all dependencies are installed correctly
4. Test with sample audio files first

## Future Enhancements

Planned features for future versions:
- Real-time audio monitoring
- Voice cloning detection
- Enhanced multi-language support
- Cloud-based processing options
- Integration with case management systems
- Advanced visualization tools
- Mobile companion app

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, Cross-platform
