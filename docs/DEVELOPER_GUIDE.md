# Developer Guide

## Getting Started

### Development Environment Setup

1. **Clone Repository**
```bash
git clone https://github.com/Meetthacker112/Audio_Forensic_Tool.git
cd Audio_Forensic_Tool
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Project Structure

```
Audio_Forensic_Tool/
├── src/                    # Core modules
│   ├── analytics_engine.py
│   ├── enhanced_text_detection.py
│   └── lightweight_models.py
├── data/                   # Configuration data
│   ├── confidence_rules.json
│   ├── cultural_context.json
│   └── enhanced_crime_keywords.json
├── logs/                   # Application logs
├── models/                 # ML model cache
├── reports/                # Generated reports
├── main.py                 # Entry point
├── gui.py                  # GUI implementation
├── audio_processing.py     # Audio analysis
├── speech_analysis.py      # Speech recognition
├── keyword_detection.py    # NLP processing
├── forensic_ai.py         # AI integration
└── report_generator.py    # Report generation
```

## Code Style

### Python Standards

- Follow PEP 8 style guide
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use docstrings for all public functions

**Example:**
```python
def analyze_audio(file_path: str, options: dict) -> dict:
    """
    Analyze audio file with specified options.
    
    Args:
        file_path: Path to audio file
        options: Analysis configuration
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If options are invalid
    """
    pass
```

### Naming Conventions

- Classes: `PascalCase`
- Functions/Methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

## Adding New Features

### 1. Audio Analysis Module

Create new analysis in `audio_processing.py`:

```python
class NewAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        
    def analyze(self, audio_data: np.ndarray, sr: int) -> dict:
        """Implement your analysis logic"""
        results = {}
        # Your code here
        return results
```

### 2. Keyword Detection

Add keywords to `data/enhanced_crime_keywords.json`:

```json
{
  "category_name": {
    "keywords": ["word1", "word2"],
    "severity": "high",
    "context_required": true
  }
}
```

### 3. GUI Components

Add UI elements in `gui.py`:

```python
def create_new_tab(self):
    tab = QWidget()
    layout = QVBoxLayout()
    # Add widgets
    tab.setLayout(layout)
    self.tabs.addTab(tab, "Tab Name")
```

## Testing

### Unit Tests

```bash
pytest tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Import Errors:**
- Verify virtual environment is activated
- Check `requirements.txt` installed

**Audio Loading Fails:**
- Verify ffmpeg installed
- Check file format compatibility

**ML Model Errors:**
- Clear model cache: `rm -rf models/`
- Re-download models

## Contributing

### Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes with tests
4. Run tests: `pytest`
5. Commit: `git commit -m "feat: add new feature"`
6. Push: `git push origin feature/new-feature`
7. Create Pull Request

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting
- `chore:` Maintenance

## API Development

### Adding Endpoints

In `api_server.py`:

```python
@app.post("/api/new-endpoint")
async def new_endpoint(data: RequestModel):
    """Endpoint description"""
    result = process_data(data)
    return {"result": result}
```

### Request Validation

Use Pydantic models:

```python
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    file_id: str
    options: dict
```

## Performance Optimization

### Profiling

```python
import cProfile
cProfile.run('analyze_audio(file_path)')
```

### Memory Management

- Use generators for large datasets
- Clear unused variables
- Monitor with `memory_profiler`

## Documentation

### Code Documentation

- Add docstrings to all functions
- Include usage examples
- Document parameters and return values

### API Documentation

- Update `docs/API_DOCUMENTATION.md`
- Include request/response examples
- Document error codes

## Release Process

1. Update version in `main.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Build distribution: `python setup.py sdist`
5. Push tag: `git push origin v1.0.0`
