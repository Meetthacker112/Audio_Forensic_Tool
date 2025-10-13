"""
Lightweight AI Models for Suspicious Text Detection

This module provides fallback AI models using HuggingFace transformers
when OpenAI API is unavailable or for cost optimization.

Author: AI Assistant
Version: 2.0.0
"""

from __future__ import annotations

import logging
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

# Optional imports with graceful fallbacks
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from transformers import AutoModel, AutoConfig
    import torch
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    pipeline = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None
    AutoModel = None
    AutoConfig = None
    torch = None
    _TRANSFORMERS_AVAILABLE = False

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    np = None
    _NUMPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    _SENTENCE_TRANSFORMERS_AVAILABLE = False


@dataclass
class ModelPrediction:
    """Prediction result from lightweight model"""
    label: str
    confidence: float
    model_name: str
    processing_time: float
    metadata: Dict[str, Any] = None


class LightweightModelManager:
    """Manager for lightweight AI models"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.models = {}
        self.model_configs = self._load_model_configs()
        
        # Initialize available models
        self._initialize_models()
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration for lightweight models"""
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        # Default configuration
        return {
            "use_gpu": False,
            "max_length": 512,
            "batch_size": 16,
            "confidence_threshold": 0.5,
            "enable_caching": True,
            "cache_size": 1000,
            "models": {
                "zero_shot": "facebook/bart-large-mnli",
                "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "emotion": "j-hartmann/emotion-english-distilroberta-base",
                "sentence_transformer": "all-MiniLM-L6-v2"
            }
        }
    
    def _load_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load model configurations"""
        return {
            "zero_shot": {
                "model_name": "facebook/bart-large-mnli",
                "task": "zero-shot-classification",
                "labels": [
                    "violence", "weapons", "threats", "drugs", "theft", "fraud",
                    "smuggling", "kidnapping", "terrorism", "organized crime",
                    "illegal activity", "criminal behavior", "suspicious activity"
                ],
                "confidence_threshold": 0.3
            },
            "sentiment": {
                "model_name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "task": "sentiment-analysis",
                "confidence_threshold": 0.6
            },
            "emotion": {
                "model_name": "j-hartmann/emotion-english-distilroberta-base",
                "task": "text-classification",
                "confidence_threshold": 0.4
            },
            "sentence_transformer": {
                "model_name": "all-MiniLM-L6-v2",
                "task": "feature-extraction",
                "confidence_threshold": 0.7
            }
        }
    
    def _initialize_models(self):
        """Initialize available models"""
        if not _TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers not available, skipping model initialization")
            return
        
        try:
            # Initialize zero-shot classification model
            if self.config.get("models", {}).get("zero_shot"):
                self._load_zero_shot_model()
            
            # Initialize sentiment analysis model
            if self.config.get("models", {}).get("sentiment"):
                self._load_sentiment_model()
            
            # Initialize emotion analysis model
            if self.config.get("models", {}).get("emotion"):
                self._load_emotion_model()
            
            # Initialize sentence transformer
            if self.config.get("models", {}).get("sentence_transformer"):
                self._load_sentence_transformer()
                
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
    
    def _load_zero_shot_model(self):
        """Load zero-shot classification model"""
        try:
            model_name = self.model_configs["zero_shot"]["model_name"]
            self.models["zero_shot"] = pipeline(
                "zero-shot-classification",
                model=model_name,
                device=0 if self.config.get("use_gpu", False) and torch and torch.cuda.is_available() else -1
            )
            self.logger.info(f"Loaded zero-shot model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load zero-shot model: {e}")
    
    def _load_sentiment_model(self):
        """Load sentiment analysis model"""
        try:
            model_name = self.model_configs["sentiment"]["model_name"]
            self.models["sentiment"] = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=0 if self.config.get("use_gpu", False) and torch and torch.cuda.is_available() else -1
            )
            self.logger.info(f"Loaded sentiment model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load sentiment model: {e}")
    
    def _load_emotion_model(self):
        """Load emotion analysis model"""
        try:
            model_name = self.model_configs["emotion"]["model_name"]
            self.models["emotion"] = pipeline(
                "text-classification",
                model=model_name,
                device=0 if self.config.get("use_gpu", False) and torch and torch.cuda.is_available() else -1
            )
            self.logger.info(f"Loaded emotion model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load emotion model: {e}")
    
    def _load_sentence_transformer(self):
        """Load sentence transformer model"""
        if not _SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.warning("Sentence transformers not available")
            return
        
        try:
            model_name = self.model_configs["sentence_transformer"]["model_name"]
            self.models["sentence_transformer"] = SentenceTransformer(model_name)
            self.logger.info(f"Loaded sentence transformer: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load sentence transformer: {e}")
    
    def classify_zero_shot(self, text: str, custom_labels: Optional[List[str]] = None) -> ModelPrediction:
        """Classify text using zero-shot classification"""
        if "zero_shot" not in self.models:
            return ModelPrediction(
                label="unknown",
                confidence=0.0,
                model_name="zero_shot",
                processing_time=0.0,
                metadata={"error": "Model not loaded"}
            )
        
        try:
            start_time = time.time()
            
            labels = custom_labels or self.model_configs["zero_shot"]["labels"]
            result = self.models["zero_shot"](text, labels)
            
            processing_time = time.time() - start_time
            
            # Get the best prediction
            best_label = result["labels"][0]
            best_confidence = result["scores"][0]
            
            return ModelPrediction(
                label=best_label,
                confidence=best_confidence,
                model_name="zero_shot",
                processing_time=processing_time,
                metadata={
                    "all_labels": result["labels"],
                    "all_scores": result["scores"],
                    "sequence": result.get("sequence", text)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Zero-shot classification failed: {e}")
            return ModelPrediction(
                label="error",
                confidence=0.0,
                model_name="zero_shot",
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    def analyze_sentiment(self, text: str) -> ModelPrediction:
        """Analyze sentiment of text"""
        if "sentiment" not in self.models:
            return ModelPrediction(
                label="unknown",
                confidence=0.0,
                model_name="sentiment",
                processing_time=0.0,
                metadata={"error": "Model not loaded"}
            )
        
        try:
            start_time = time.time()
            result = self.models["sentiment"](text)
            processing_time = time.time() - start_time
            
            # Handle both single and batch results
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            return ModelPrediction(
                label=result["label"],
                confidence=result["score"],
                model_name="sentiment",
                processing_time=processing_time,
                metadata={"raw_result": result}
            )
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return ModelPrediction(
                label="error",
                confidence=0.0,
                model_name="sentiment",
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    def analyze_emotion(self, text: str) -> ModelPrediction:
        """Analyze emotion in text"""
        if "emotion" not in self.models:
            return ModelPrediction(
                label="unknown",
                confidence=0.0,
                model_name="emotion",
                processing_time=0.0,
                metadata={"error": "Model not loaded"}
            )
        
        try:
            start_time = time.time()
            result = self.models["emotion"](text)
            processing_time = time.time() - start_time
            
            # Handle both single and batch results
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            return ModelPrediction(
                label=result["label"],
                confidence=result["score"],
                model_name="emotion",
                processing_time=processing_time,
                metadata={"raw_result": result}
            )
            
        except Exception as e:
            self.logger.error(f"Emotion analysis failed: {e}")
            return ModelPrediction(
                label="error",
                confidence=0.0,
                model_name="emotion",
                processing_time=0.0,
                metadata={"error": str(e)}
            )
    
    def get_sentence_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get sentence embedding using sentence transformer"""
        if "sentence_transformer" not in self.models:
            return None
        
        try:
            embedding = self.models["sentence_transformer"].encode(text)
            return embedding
        except Exception as e:
            self.logger.error(f"Sentence embedding failed: {e}")
            return None
    
    def detect_suspicious_content(self, text: str) -> List[ModelPrediction]:
        """Detect suspicious content using multiple models"""
        predictions = []
        
        # Zero-shot classification for crime-related content
        zero_shot_result = self.classify_zero_shot(text)
        if zero_shot_result.confidence > self.model_configs["zero_shot"]["confidence_threshold"]:
            predictions.append(zero_shot_result)
        
        # Sentiment analysis for negative sentiment
        sentiment_result = self.analyze_sentiment(text)
        if sentiment_result.label in ["NEGATIVE", "LABEL_0"] and sentiment_result.confidence > 0.6:
            predictions.append(sentiment_result)
        
        # Emotion analysis for anger, fear, etc.
        emotion_result = self.analyze_emotion(text)
        if emotion_result.label in ["anger", "fear", "disgust"] and emotion_result.confidence > 0.4:
            predictions.append(emotion_result)
        
        return predictions
    
    def batch_classify(self, texts: List[str], model_type: str = "zero_shot") -> List[ModelPrediction]:
        """Classify multiple texts in batch"""
        if model_type not in self.models:
            return []
        
        try:
            start_time = time.time()
            
            if model_type == "zero_shot":
                labels = self.model_configs["zero_shot"]["labels"]
                results = self.models[model_type](texts, labels)
            else:
                results = self.models[model_type](texts)
            
            processing_time = time.time() - start_time
            
            predictions = []
            for i, result in enumerate(results):
                if model_type == "zero_shot":
                    best_label = result["labels"][0]
                    best_confidence = result["scores"][0]
                else:
                    best_label = result["label"]
                    best_confidence = result["score"]
                
                predictions.append(ModelPrediction(
                    label=best_label,
                    confidence=best_confidence,
                    model_name=model_type,
                    processing_time=processing_time / len(texts),
                    metadata={"batch_index": i, "raw_result": result}
                ))
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Batch classification failed: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        info = {
            "available_models": list(self.models.keys()),
            "config": self.config,
            "model_configs": self.model_configs,
            "transformers_available": _TRANSFORMERS_AVAILABLE,
            "sentence_transformers_available": _SENTENCE_TRANSFORMERS_AVAILABLE,
            "numpy_available": _NUMPY_AVAILABLE
        }
        
        # Add model-specific info
        for model_name, model in self.models.items():
            if hasattr(model, 'model'):
                info[f"{model_name}_model_name"] = getattr(model.model, 'name_or_path', 'unknown')
            elif hasattr(model, 'model_name'):
                info[f"{model_name}_model_name"] = model.model_name
        
        return info


class SuspiciousContentDetector:
    """Specialized detector for suspicious content using lightweight models"""
    
    def __init__(self, model_manager: Optional[LightweightModelManager] = None):
        self.logger = logging.getLogger(__name__)
        self.model_manager = model_manager or LightweightModelManager()
        
        # Crime-related labels for zero-shot classification
        self.crime_labels = [
            "violence", "murder", "assault", "attack", "weapons", "guns", "knives",
            "threats", "intimidation", "blackmail", "extortion", "drugs", "drug trafficking",
            "theft", "robbery", "burglary", "fraud", "scam", "money laundering",
            "kidnapping", "hostage", "terrorism", "bomb", "explosive", "organized crime",
            "illegal activity", "criminal behavior", "suspicious activity", "planning crime"
        ]
        
        # Suspicious emotion labels
        self.suspicious_emotions = ["anger", "fear", "disgust", "contempt"]
        
        # Negative sentiment indicators
        self.negative_sentiment = ["NEGATIVE", "LABEL_0", "negative"]
    
    def detect_crime_related_content(self, text: str) -> List[ModelPrediction]:
        """Detect crime-related content using zero-shot classification"""
        return [self.model_manager.classify_zero_shot(text, self.crime_labels)]
    
    def detect_suspicious_emotions(self, text: str) -> List[ModelPrediction]:
        """Detect suspicious emotions in text"""
        emotion_result = self.model_manager.analyze_emotion(text)
        if emotion_result.label in self.suspicious_emotions:
            return [emotion_result]
        return []
    
    def detect_negative_sentiment(self, text: str) -> List[ModelPrediction]:
        """Detect negative sentiment that might indicate suspicious content"""
        sentiment_result = self.model_manager.analyze_sentiment(text)
        if sentiment_result.label in self.negative_sentiment and sentiment_result.confidence > 0.6:
            return [sentiment_result]
        return []
    
    def comprehensive_analysis(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive analysis using all available models"""
        results = {
            "text": text,
            "analysis_time": 0.0,
            "predictions": [],
            "suspicious_score": 0.0,
            "flags": [],
            "confidence": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Crime-related content detection
            crime_predictions = self.detect_crime_related_content(text)
            results["predictions"].extend(crime_predictions)
            
            # Emotion analysis
            emotion_predictions = self.detect_suspicious_emotions(text)
            results["predictions"].extend(emotion_predictions)
            
            # Sentiment analysis
            sentiment_predictions = self.detect_negative_sentiment(text)
            results["predictions"].extend(sentiment_predictions)
            
            # Calculate suspicious score
            suspicious_score = 0.0
            confidence_scores = []
            flags = []
            
            for prediction in results["predictions"]:
                if prediction.confidence > 0.3:  # Threshold for consideration
                    suspicious_score += prediction.confidence
                    confidence_scores.append(prediction.confidence)
                    
                    # Extract flags from labels
                    if "violence" in prediction.label.lower():
                        flags.append("violence")
                    elif "weapon" in prediction.label.lower():
                        flags.append("weapons")
                    elif "threat" in prediction.label.lower():
                        flags.append("threats")
                    elif "drug" in prediction.label.lower():
                        flags.append("drugs")
                    elif "theft" in prediction.label.lower():
                        flags.append("theft")
                    elif "fraud" in prediction.label.lower():
                        flags.append("fraud")
                    elif prediction.label in self.suspicious_emotions:
                        flags.append("suspicious_emotion")
                    elif prediction.label in self.negative_sentiment:
                        flags.append("negative_sentiment")
            
            # Normalize suspicious score
            if confidence_scores:
                results["suspicious_score"] = suspicious_score / len(confidence_scores)
                results["confidence"] = max(confidence_scores)
            else:
                results["suspicious_score"] = 0.0
                results["confidence"] = 0.0
            
            results["flags"] = list(set(flags))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            results["error"] = str(e)
        
        results["analysis_time"] = time.time() - start_time
        return results


# Convenience functions
def create_lightweight_detector(config_path: Optional[Path] = None) -> SuspiciousContentDetector:
    """Create a lightweight suspicious content detector"""
    model_manager = LightweightModelManager(config_path)
    return SuspiciousContentDetector(model_manager)


def detect_suspicious_lightweight(text: str, config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Quick function to detect suspicious content using lightweight models"""
    detector = create_lightweight_detector(config_path)
    return detector.comprehensive_analysis(text)


if __name__ == "__main__":
    # Example usage
    detector = create_lightweight_detector()
    
    test_texts = [
        "I'm going to kill him tomorrow",
        "The weather is nice today",
        "We need to plan the robbery carefully",
        "I'm feeling angry and frustrated"
    ]
    
    for text in test_texts:
        print(f"\nAnalyzing: {text}")
        result = detector.comprehensive_analysis(text)
        print(f"Suspicious Score: {result['suspicious_score']:.2f}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Flags: {result['flags']}")
        print(f"Analysis Time: {result['analysis_time']:.3f}s")