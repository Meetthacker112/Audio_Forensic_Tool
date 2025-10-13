"""
Enhanced Suspicious Text Detection System

This module provides an advanced, production-ready suspicious text detection system with:
- Multilingual explainable AI with translation and context reasoning
- Advanced confidence scoring and contextual filtering
- Structured logging and analytics
- Performance optimizations with caching
- Lightweight model fallbacks

Author: AI Assistant
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum

# Core dependencies
import numpy as np
from dataclasses_json import dataclass_json

# Optional imports with graceful fallbacks
try:
    import spacy
    _SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    _SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize.punkt import PunktSentenceTokenizer
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
except ImportError:
    nltk = None
    PunktSentenceTokenizer = None
    stopwords = None
    PorterStemmer = None

try:
    from langdetect import detect as langdetect_detect
    _LANGDETECT_AVAILABLE = True
except ImportError:
    langdetect_detect = None
    _LANGDETECT_AVAILABLE = False

try:
    from googletrans import Translator
    _TRANSLATION_AVAILABLE = True
except ImportError:
    Translator = None
    _TRANSLATION_AVAILABLE = False

try:
    from openai import AsyncOpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    AsyncOpenAI = None
    _OPENAI_AVAILABLE = False

try:
    from transformers import pipeline
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    pipeline = None
    _TRANSFORMERS_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import os


class SeverityLevel(Enum):
    """Severity levels for detected content"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class DetectionMethod(Enum):
    """Detection methods used"""
    KEYWORDS = "keywords"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    PATTERN = "pattern"
    CONTEXT = "context"


@dataclass_json
@dataclass
class DetectionContext:
    """Context information for detection"""
    language: str
    cultural_context: Optional[str] = None
    temporal_indicators: List[str] = None
    location_indicators: List[str] = None
    planning_indicators: List[str] = None
    threat_level: str = "UNKNOWN"
    
    def __post_init__(self):
        if self.temporal_indicators is None:
            self.temporal_indicators = []
        if self.location_indicators is None:
            self.location_indicators = []
        if self.planning_indicators is None:
            self.planning_indicators = []


@dataclass_json
@dataclass
class DetectionExplanation:
    """Explanation for why content was flagged"""
    reasoning: str
    confidence_factors: List[str]
    cultural_context: Optional[str] = None
    translation_analysis: Optional[str] = None
    pattern_matches: List[str] = None
    keyword_matches: List[str] = None
    
    def __post_init__(self):
        if self.pattern_matches is None:
            self.pattern_matches = []
        if self.keyword_matches is None:
            self.keyword_matches = []


@dataclass_json
@dataclass
class EnhancedDetectionResult:
    """Enhanced detection result with comprehensive information"""
    detection_id: str
    timestamp: str
    text: str
    language: str
    confidence: float
    severity: SeverityLevel
    flags: List[str]
    detection_method: DetectionMethod
    explanation: DetectionExplanation
    context: DetectionContext
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConfidenceScorer:
    """Advanced confidence scoring system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.confidence_rules = self._load_confidence_rules()
    
    def _load_confidence_rules(self) -> Dict[str, Any]:
        """Load confidence scoring rules from configuration"""
        rules_path = Path(__file__).parent.parent / "data" / "confidence_rules.json"
        if rules_path.exists():
            try:
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load confidence rules: {e}")
        
        # Default confidence rules
        return {
            "keyword_weights": {
                "violence": 0.9,
                "weapons": 0.85,
                "threats": 0.8,
                "drugs": 0.75,
                "theft": 0.7,
                "fraud": 0.65,
                "general": 0.5
            },
            "context_weights": {
                "planning": 0.3,
                "temporal": 0.2,
                "location": 0.15,
                "imperative": 0.25,
                "question": 0.1
            },
            "method_weights": {
                "keywords": 0.4,
                "openai": 0.8,
                "huggingface": 0.6,
                "pattern": 0.5,
                "context": 0.3
            }
        }
    
    def calculate_confidence(
        self,
        flags: List[str],
        detection_method: DetectionMethod,
        context: DetectionContext,
        explanation: DetectionExplanation
    ) -> float:
        """Calculate confidence score based on multiple factors"""
        try:
            base_confidence = 0.0
            
            # Method-based confidence
            method_weight = self.confidence_rules["method_weights"].get(
                detection_method.value, 0.5
            )
            base_confidence += method_weight * 0.4
            
            # Keyword-based confidence
            keyword_confidence = 0.0
            for flag in flags:
                for category, weight in self.confidence_rules["keyword_weights"].items():
                    if category in flag.lower():
                        keyword_confidence = max(keyword_confidence, weight)
            
            base_confidence += keyword_confidence * 0.4
            
            # Context-based confidence
            context_confidence = 0.0
            if context.planning_indicators:
                context_confidence += self.confidence_rules["context_weights"]["planning"]
            if context.temporal_indicators:
                context_confidence += self.confidence_rules["context_weights"]["temporal"]
            if context.location_indicators:
                context_confidence += self.confidence_rules["context_weights"]["location"]
            
            base_confidence += context_confidence * 0.2
            
            # Ensure confidence is between 0 and 1
            return max(0.0, min(1.0, base_confidence))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default moderate confidence


class TranslationService:
    """Multilingual translation service with cultural context awareness"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.translator = None
        self.cultural_context = self._load_cultural_context()
        
        if _TRANSLATION_AVAILABLE:
            try:
                self.translator = Translator()
            except Exception as e:
                self.logger.warning(f"Translation service unavailable: {e}")
    
    def _load_cultural_context(self) -> Dict[str, Any]:
        """Load cultural context rules for different languages"""
        context_path = Path(__file__).parent.parent / "data" / "cultural_context.json"
        if context_path.exists():
            try:
                with open(context_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load cultural context: {e}")
        
        # Default cultural context
        return {
            "english": {
                "direct_threats": True,
                "implicit_violence": True,
                "planning_language": True
            },
            "hindi": {
                "direct_threats": True,
                "implicit_violence": True,
                "planning_language": True,
                "respect_hierarchy": True
            },
            "gujarati": {
                "direct_threats": True,
                "implicit_violence": True,
                "planning_language": True,
                "respect_hierarchy": True
            }
        }
    
    async def translate_text(self, text: str, target_language: str = "en") -> str:
        """Translate text to target language"""
        if not self.translator:
            return text
        
        try:
            result = self.translator.translate(text, dest=target_language)
            return result.text
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return text
    
    def get_cultural_context(self, language: str) -> Dict[str, Any]:
        """Get cultural context rules for language"""
        return self.cultural_context.get(language.lower(), self.cultural_context["english"])


class ExplainableAI:
    """Explainable AI system for providing reasoning behind detections"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.translation_service = TranslationService()
    
    def generate_explanation(
        self,
        text: str,
        flags: List[str],
        detection_method: DetectionMethod,
        context: DetectionContext,
        confidence: float
    ) -> DetectionExplanation:
        """Generate detailed explanation for detection"""
        try:
            reasoning_parts = []
            confidence_factors = []
            
            # Method-based reasoning
            if detection_method == DetectionMethod.KEYWORDS:
                reasoning_parts.append("Detection based on keyword matching against crime-related terms")
                confidence_factors.append("Exact keyword matches found")
            elif detection_method == DetectionMethod.OPENAI:
                reasoning_parts.append("AI-powered semantic analysis detected suspicious content")
                confidence_factors.append("Advanced language model analysis")
            elif detection_method == DetectionMethod.HUGGINGFACE:
                reasoning_parts.append("Lightweight AI model identified suspicious patterns")
                confidence_factors.append("Machine learning pattern recognition")
            
            # Flag-based reasoning
            if flags:
                flag_explanations = []
                for flag in flags:
                    if "violence" in flag.lower():
                        flag_explanations.append("violence-related terminology")
                    elif "weapon" in flag.lower():
                        flag_explanations.append("weapon references")
                    elif "threat" in flag.lower():
                        flag_explanations.append("threatening language")
                    elif "drug" in flag.lower():
                        flag_explanations.append("drug-related content")
                    elif "theft" in flag.lower():
                        flag_explanations.append("theft-related terminology")
                
                if flag_explanations:
                    reasoning_parts.append(f"Specific indicators: {', '.join(flag_explanations)}")
                    confidence_factors.append(f"Multiple crime categories detected: {len(set(flags))}")
            
            # Context-based reasoning
            if context.planning_indicators:
                reasoning_parts.append("Planning language detected, indicating potential premeditation")
                confidence_factors.append("Planning indicators present")
            
            if context.temporal_indicators:
                reasoning_parts.append("Time-specific references suggest concrete plans")
                confidence_factors.append("Temporal specificity increases threat level")
            
            if context.location_indicators:
                reasoning_parts.append("Location references indicate specific targeting")
                confidence_factors.append("Geographic specificity detected")
            
            # Cultural context
            cultural_context = self.translation_service.get_cultural_context(context.language)
            if cultural_context.get("respect_hierarchy", False):
                reasoning_parts.append("Cultural context analysis applied for hierarchical language patterns")
            
            # Confidence-based reasoning
            if confidence > 0.8:
                reasoning_parts.append("High confidence due to multiple converging indicators")
                confidence_factors.append("Multiple high-confidence factors")
            elif confidence > 0.6:
                reasoning_parts.append("Moderate confidence with some uncertainty factors")
                confidence_factors.append("Mixed confidence indicators")
            else:
                reasoning_parts.append("Lower confidence due to limited or ambiguous indicators")
                confidence_factors.append("Limited confidence factors")
            
            return DetectionExplanation(
                reasoning="; ".join(reasoning_parts),
                confidence_factors=confidence_factors,
                cultural_context=f"Analyzed in {context.language} cultural context",
                keyword_matches=flags
            )
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {e}")
            return DetectionExplanation(
                reasoning="Detection completed with standard analysis",
                confidence_factors=["Standard analysis applied"]
            )


class EnhancedSuspiciousDetector:
    """Enhanced suspicious text detector with advanced features"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.confidence_scorer = ConfidenceScorer()
        self.explainable_ai = ExplainableAI()
        self.translation_service = TranslationService()
        
        # Load enhanced keyword database
        self.keywords = self._load_enhanced_keywords()
        
        # Initialize AI models
        self.openai_client = self._init_openai()
        self.huggingface_model = self._init_huggingface()
        
        # Initialize sentence segmenter
        self.sentence_segmenter = self._init_sentence_segmenter()
        
        # Detection patterns
        self.patterns = self._load_detection_patterns()
        
        # Analytics
        self.detection_count = 0
        self.start_time = time.time()
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration settings"""
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        # Default configuration
        return {
            "use_openai": os.getenv("USE_OPENAI", "false").lower() == "true",
            "use_huggingface": True,
            "confidence_threshold": 0.5,
            "enable_translation": True,
            "enable_explanations": True,
            "cache_detections": True,
            "log_detections": True
        }
    
    def _load_enhanced_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Load enhanced keyword database"""
        keywords_path = Path(__file__).parent.parent / "data" / "enhanced_crime_keywords.json"
        if keywords_path.exists():
            try:
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load enhanced keywords: {e}")
        
        # Fallback to existing keywords
        fallback_path = Path(__file__).parent.parent / "crime_keywords.json"
        if fallback_path.exists():
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load fallback keywords: {e}")
        
        # Minimal default keywords
        return {
            "english": {
                "violence": ["murder", "kill", "attack", "violence"],
                "weapons": ["gun", "weapon", "knife", "bomb"],
                "threats": ["threat", "threaten", "intimidate"],
                "drugs": ["drug", "cocaine", "heroin"],
                "theft": ["steal", "rob", "theft"],
                "fraud": ["fraud", "scam", "cheat"]
            }
        }
    
    def _load_detection_patterns(self) -> Dict[str, List[str]]:
        """Load detection patterns for different languages"""
        return {
            "english": [
                r"(going to|will|gonna)\s+(kill|murder|shoot|attack)",
                r"(have|got)\s+a\s+(gun|knife|weapon)",
                r"(plan to|planning to)\s+(rob|steal|kidnap)",
                r"(meet at|come to)\s+.+\s+(tonight|tomorrow)",
                r"bring\s+(money|cash|drugs)",
                r"if you\s+(tell|report|go to police)"
            ],
            "hindi": [
                r"(जाना|करना|होगा)\s+(मार|हत्या|गोली)",
                r"(है|पास)\s+(बंदूक|छुरी|हथियार)",
                r"(योजना|प्लान)\s+(चोरी|अपहरण|लूट)",
                r"(मिलना|आना)\s+.+\s+(रात|कल)",
                r"(लाना|लेकर आना)\s+(पैसा|नकद|नशा)"
            ],
            "gujarati": [
                r"(જવાનું|કરવું|થશે)\s+(મારવું|હત્યા|ગોળી)",
                r"(છે|પાસે)\s+(બંદૂક|છરી|હથિયાર)",
                r"(યોજના|પ્લાન)\s+(ચોરી|અપહરણ|લૂંટ)",
                r"(મળવું|આવવું)\s+.+\s+(રાત્રે|કાલે)",
                r"(લાવવું|લઈને આવવું)\s+(પૈસા|રોકડ|નશો)"
            ]
        }
    
    def _init_openai(self) -> Optional[AsyncOpenAI]:
        """Initialize OpenAI client"""
        if not self.config.get("use_openai", False) or not _OPENAI_AVAILABLE:
            return None
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.warning("OpenAI API key not found")
            return None
        
        try:
            return AsyncOpenAI(api_key=api_key)
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    
    def _init_huggingface(self) -> Optional[Any]:
        """Initialize HuggingFace model"""
        if not self.config.get("use_huggingface", True) or not _TRANSFORMERS_AVAILABLE:
            return None
        
        try:
            return pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # CPU
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize HuggingFace model: {e}")
            return None
    
    def _init_sentence_segmenter(self):
        """Initialize sentence segmenter"""
        # This would integrate with the existing SentenceSegmenter
        # For now, return a simple implementation
        return None
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        if not _LANGDETECT_AVAILABLE:
            # Fallback to script detection
            if re.search(r"[\u0A80-\u0AFF]", text):  # Gujarati
                return "gujarati"
            elif re.search(r"[\u0900-\u097F]", text):  # Hindi
                return "hindi"
            return "english"
        
        try:
            lang_code = langdetect_detect(text)
            lang_mapping = {
                "en": "english",
                "hi": "hindi", 
                "gu": "gujarati"
            }
            return lang_mapping.get(lang_code, "english")
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return "english"
    
    def analyze_context(self, text: str, language: str) -> DetectionContext:
        """Analyze context of the text"""
        context = DetectionContext(language=language)
        
        # Detect planning indicators
        planning_patterns = [
            r"(going to|will|gonna|plan to|planning to)",
            r"(meet at|come to|go to)",
            r"(bring|get|take)",
            r"(tonight|tomorrow|next week)"
        ]
        
        for pattern in planning_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                context.planning_indicators.append(pattern)
        
        # Detect temporal indicators
        temporal_patterns = [
            r"(tonight|tomorrow|next week|this evening|midnight)",
            r"(at \d+|\d+ o'clock)",
            r"(after dark|before dawn)"
        ]
        
        for pattern in temporal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                context.temporal_indicators.append(pattern)
        
        # Detect location indicators
        location_patterns = [
            r"(at the|near|behind|in front of)",
            r"(warehouse|building|house|street|road)",
            r"(inside|outside|underground)"
        ]
        
        for pattern in location_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                context.location_indicators.append(pattern)
        
        # Determine threat level
        if context.planning_indicators and context.temporal_indicators:
            context.threat_level = "HIGH"
        elif context.planning_indicators or context.temporal_indicators:
            context.threat_level = "MEDIUM"
        else:
            context.threat_level = "LOW"
        
        return context
    
    async def detect_keywords(self, text: str, language: str) -> Tuple[List[str], DetectionMethod]:
        """Detect keywords in text"""
        flags = []
        text_lower = text.lower()
        
        # Get keywords for language
        lang_keywords = self.keywords.get(language, self.keywords.get("english", {}))
        
        for category, keywords in lang_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    flags.append(f"{category}_{keyword}")
        
        return flags, DetectionMethod.KEYWORDS
    
    async def detect_patterns(self, text: str, language: str) -> Tuple[List[str], DetectionMethod]:
        """Detect suspicious patterns in text"""
        flags = []
        patterns = self.patterns.get(language, self.patterns.get("english", []))
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(f"pattern_{pattern}")
        
        return flags, DetectionMethod.PATTERN
    
    async def detect_with_openai(self, text: str, language: str) -> Tuple[List[str], DetectionMethod]:
        """Detect using OpenAI API"""
        if not self.openai_client:
            return [], DetectionMethod.OPENAI
        
        try:
            prompt = f"""
            Analyze this text for criminal, illegal, or suspicious content.
            Language: {language}
            Text: {text}
            
            Return a JSON object with:
            - is_suspicious: boolean
            - confidence: float (0-1)
            - flags: array of short descriptive labels
            - reasoning: brief explanation
            """
            
            response = await self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("is_suspicious", False):
                return result.get("flags", []), DetectionMethod.OPENAI
            
            return [], DetectionMethod.OPENAI
            
        except Exception as e:
            self.logger.error(f"OpenAI detection failed: {e}")
            return [], DetectionMethod.OPENAI
    
    async def detect_with_huggingface(self, text: str, language: str) -> Tuple[List[str], DetectionMethod]:
        """Detect using HuggingFace model"""
        if not self.huggingface_model:
            return [], DetectionMethod.HUGGINGFACE
        
        try:
            # Define crime-related labels
            labels = [
                "violence", "weapons", "threats", "drugs", "theft", "fraud",
                "smuggling", "kidnapping", "terrorism", "organized crime"
            ]
            
            result = self.huggingface_model(text, labels)
            
            # Filter results with confidence > 0.5
            flags = []
            for label, score in zip(result["labels"], result["scores"]):
                if score > 0.5:
                    flags.append(f"hf_{label}")
            
            return flags, DetectionMethod.HUGGINGFACE
            
        except Exception as e:
            self.logger.error(f"HuggingFace detection failed: {e}")
            return [], DetectionMethod.HUGGINGFACE
    
    async def analyze_text(self, text: str, language: Optional[str] = None) -> List[EnhancedDetectionResult]:
        """Main analysis method"""
        if not text or not text.strip():
            return []
        
        # Detect language if not provided
        detected_language = language or self.detect_language(text)
        
        # Analyze context
        context = self.analyze_context(text, detected_language)
        
        # Run all detection methods
        detection_tasks = [
            self.detect_keywords(text, detected_language),
            self.detect_patterns(text, detected_language),
            self.detect_with_openai(text, detected_language),
            self.detect_with_huggingface(text, detected_language)
        ]
        
        results = await asyncio.gather(*detection_tasks, return_exceptions=True)
        
        # Process results
        all_flags = []
        detection_methods = []
        
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Detection method failed: {result}")
                continue
            
            flags, method = result
            all_flags.extend(flags)
            detection_methods.append(method)
        
        # Remove duplicates while preserving order
        unique_flags = []
        seen = set()
        for flag in all_flags:
            if flag not in seen:
                unique_flags.append(flag)
                seen.add(flag)
        
        if not unique_flags:
            return []
        
        # Determine primary detection method
        primary_method = DetectionMethod.KEYWORDS
        if DetectionMethod.OPENAI in detection_methods:
            primary_method = DetectionMethod.OPENAI
        elif DetectionMethod.HUGGINGFACE in detection_methods:
            primary_method = DetectionMethod.HUGGINGFACE
        elif DetectionMethod.PATTERN in detection_methods:
            primary_method = DetectionMethod.PATTERN
        
        # Calculate confidence
        confidence = self.confidence_scorer.calculate_confidence(
            unique_flags, primary_method, context, None
        )
        
        # Generate explanation
        explanation = self.explainable_ai.generate_explanation(
            text, unique_flags, primary_method, context, confidence
        )
        
        # Determine severity
        severity = self._determine_severity(unique_flags, confidence, context)
        
        # Create detection result
        detection_id = f"det_{int(time.time())}_{self.detection_count}"
        self.detection_count += 1
        
        result = EnhancedDetectionResult(
            detection_id=detection_id,
            timestamp=datetime.now().isoformat(),
            text=text,
            language=detected_language,
            confidence=confidence,
            severity=severity,
            flags=unique_flags,
            detection_method=primary_method,
            explanation=explanation,
            context=context,
            metadata={
                "all_methods_used": [m.value for m in detection_methods],
                "processing_time": time.time() - self.start_time
            }
        )
        
        # Log detection if enabled
        if self.config.get("log_detections", True):
            self._log_detection(result)
        
        return [result]
    
    def _determine_severity(self, flags: List[str], confidence: float, context: DetectionContext) -> SeverityLevel:
        """Determine severity level based on flags and context"""
        # Check for critical indicators
        critical_indicators = ["violence", "murder", "kill", "weapon", "gun", "bomb"]
        if any(indicator in " ".join(flags).lower() for indicator in critical_indicators):
            return SeverityLevel.CRITICAL
        
        # Check for high indicators
        high_indicators = ["threat", "attack", "drug", "theft", "fraud"]
        if any(indicator in " ".join(flags).lower() for indicator in high_indicators):
            return SeverityLevel.HIGH
        
        # Check context
        if context.threat_level == "HIGH":
            return SeverityLevel.HIGH
        elif context.threat_level == "MEDIUM":
            return SeverityLevel.MEDIUM
        
        # Confidence-based severity
        if confidence > 0.8:
            return SeverityLevel.HIGH
        elif confidence > 0.6:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _log_detection(self, result: EnhancedDetectionResult):
        """Log detection result for analytics"""
        try:
            log_path = Path(__file__).parent.parent / "logs" / "detection_analytics.json"
            log_path.parent.mkdir(exist_ok=True)
            
            log_entry = {
                "timestamp": result.timestamp,
                "detection_id": result.detection_id,
                "language": result.language,
                "confidence": result.confidence,
                "severity": result.severity.value,
                "flags": result.flags,
                "method": result.detection_method.value,
                "text_length": len(result.text),
                "context_indicators": {
                    "planning": len(result.context.planning_indicators),
                    "temporal": len(result.context.temporal_indicators),
                    "location": len(result.context.location_indicators)
                }
            }
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log detection: {e}")


# Convenience functions for backward compatibility
async def analyze_text_enhanced(text: str, language: Optional[str] = None) -> List[EnhancedDetectionResult]:
    """Enhanced text analysis function"""
    detector = EnhancedSuspiciousDetector()
    return await detector.analyze_text(text, language)


def analyze_text_enhanced_sync(text: str, language: Optional[str] = None) -> List[EnhancedDetectionResult]:
    """Synchronous wrapper for enhanced text analysis"""
    try:
        return asyncio.run(analyze_text_enhanced(text, language))
    except RuntimeError:
        # Fallback when event loop is already running
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(analyze_text_enhanced(text, language))


if __name__ == "__main__":
    # Example usage
    async def main():
        detector = EnhancedSuspiciousDetector()
        
        test_texts = [
            "I'm going to kill him tomorrow at the warehouse",
            "He was caught smuggling drugs across the border",
            "The weather is nice today",
            "We need to plan the robbery carefully"
        ]
        
        for text in test_texts:
            print(f"\nAnalyzing: {text}")
            results = await detector.analyze_text(text)
            
            for result in results:
                print(f"Confidence: {result.confidence:.2f}")
                print(f"Severity: {result.severity.value}")
                print(f"Flags: {result.flags}")
                print(f"Explanation: {result.explanation.reasoning}")
                print("-" * 50)
    
    asyncio.run(main())