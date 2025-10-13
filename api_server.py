"""
FastAPI Server for Suspicious Text Detection

This module provides a REST API for programmatic access to the
suspicious text detection system.

Author: AI Assistant
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field, validator
    from contextlib import asynccontextmanager
except ImportError as e:
    print(f"FastAPI not available: {e}")
    print("Please install FastAPI: pip install fastapi uvicorn")
    sys.exit(1)

try:
    from enhanced_text_detection import EnhancedSuspiciousDetector, analyze_text_enhanced_sync
    from analytics_engine import AnalyticsEngine, create_analytics_engine
    from lightweight_models import create_lightweight_detector
except ImportError as e:
    print(f"Enhanced detection modules not available: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for shared resources
detector: Optional[EnhancedSuspiciousDetector] = None
analytics_engine: Optional[AnalyticsEngine] = None
lightweight_detector: Optional[Any] = None

# Pydantic models for API
class DetectionRequest(BaseModel):
    """Request model for text detection"""
    text: str = Field(..., description="Text to analyze", min_length=1, max_length=10000)
    language: Optional[str] = Field(None, description="Language hint (auto-detect if not provided)")
    include_explanation: bool = Field(True, description="Include detailed explanation")
    include_context: bool = Field(True, description="Include context analysis")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class BatchDetectionRequest(BaseModel):
    """Request model for batch text detection"""
    texts: List[str] = Field(..., description="List of texts to analyze", min_items=1, max_items=100)
    language: Optional[str] = Field(None, description="Language hint for all texts")
    include_explanation: bool = Field(True, description="Include detailed explanations")
    include_context: bool = Field(True, description="Include context analysis")

class DetectionResponse(BaseModel):
    """Response model for detection results"""
    detection_id: str
    timestamp: str
    text: str
    language: str
    confidence: float
    severity: str
    flags: List[str]
    detection_method: str
    explanation: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None

class BatchDetectionResponse(BaseModel):
    """Response model for batch detection results"""
    results: List[DetectionResponse]
    total_processed: int
    processing_time: float
    errors: List[Dict[str, Any]] = []

class AnalyticsRequest(BaseModel):
    """Request model for analytics queries"""
    hours: int = Field(24, description="Time period in hours", ge=1, le=168)
    include_charts: bool = Field(False, description="Include chart data")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    models_loaded: Dict[str, bool]
    analytics_available: bool

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: str

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global detector, analytics_engine, lightweight_detector
    
    # Startup
    logger.info("Initializing suspicious text detection API...")
    
    try:
        # Initialize enhanced detector
        detector = EnhancedSuspiciousDetector()
        logger.info("Enhanced detector initialized")
        
        # Initialize analytics engine
        analytics_engine = create_analytics_engine()
        logger.info("Analytics engine initialized")
        
        # Initialize lightweight detector
        lightweight_detector = create_lightweight_detector()
        logger.info("Lightweight detector initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down suspicious text detection API...")

# Create FastAPI app
app = FastAPI(
    title="Suspicious Text Detection API",
    description="Advanced API for detecting suspicious and crime-related text content",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get detector
def get_detector() -> EnhancedSuspiciousDetector:
    if detector is None:
        raise HTTPException(status_code=503, detail="Detector not initialized")
    return detector

def get_analytics() -> AnalyticsEngine:
    if analytics_engine is None:
        raise HTTPException(status_code=503, detail="Analytics engine not initialized")
    return analytics_engine

def get_lightweight_detector():
    if lightweight_detector is None:
        raise HTTPException(status_code=503, detail="Lightweight detector not initialized")
    return lightweight_detector

# API Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Suspicious Text Detection API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    models_loaded = {
        "enhanced_detector": detector is not None,
        "analytics_engine": analytics_engine is not None,
        "lightweight_detector": lightweight_detector is not None
    }
    
    return HealthResponse(
        status="healthy" if all(models_loaded.values()) else "degraded",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        models_loaded=models_loaded,
        analytics_available=analytics_engine is not None
    )

@app.post("/api/v1/detect", response_model=DetectionResponse)
async def detect_suspicious_text(
    request: DetectionRequest,
    detector: EnhancedSuspiciousDetector = Depends(get_detector),
    analytics: AnalyticsEngine = Depends(get_analytics)
):
    """Detect suspicious content in a single text"""
    try:
        start_time = time.time()
        
        # Perform detection
        results = await detector.analyze_text(
            text=request.text,
            language=request.language
        )
        
        processing_time = time.time() - start_time
        
        if not results:
            # No suspicious content detected
            return DetectionResponse(
                detection_id=f"det_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                text=request.text,
                language=request.language or "auto",
                confidence=0.0,
                severity="INFO",
                flags=[],
                detection_method="none",
                explanation={"reasoning": "No suspicious content detected"} if request.include_explanation else None,
                context={"threat_level": "LOW"} if request.include_context else None,
                processing_time=processing_time,
                metadata={"text_length": len(request.text)}
            )
        
        # Get the first (and typically only) result
        result = results[0]
        
        # Log for analytics
        analytics.log_detection({
            "detection_id": result.detection_id,
            "timestamp": result.timestamp,
            "language": result.language,
            "confidence": result.confidence,
            "severity": result.severity.value,
            "flags": result.flags,
            "method": result.detection_method.value,
            "text_length": len(request.text),
            "processing_time": processing_time,
            "context_indicators": {
                "planning": len(result.context.planning_indicators),
                "temporal": len(result.context.temporal_indicators),
                "location": len(result.context.location_indicators)
            }
        })
        
        # Prepare response
        response_data = {
            "detection_id": result.detection_id,
            "timestamp": result.timestamp,
            "text": result.text,
            "language": result.language,
            "confidence": result.confidence,
            "severity": result.severity.value,
            "flags": result.flags,
            "detection_method": result.detection_method.value,
            "processing_time": processing_time,
            "metadata": result.metadata
        }
        
        if request.include_explanation:
            response_data["explanation"] = {
                "reasoning": result.explanation.reasoning,
                "confidence_factors": result.explanation.confidence_factors,
                "cultural_context": result.explanation.cultural_context,
                "keyword_matches": result.explanation.keyword_matches
            }
        
        if request.include_context:
            response_data["context"] = {
                "language": result.context.language,
                "cultural_context": result.context.cultural_context,
                "temporal_indicators": result.context.temporal_indicators,
                "location_indicators": result.context.location_indicators,
                "planning_indicators": result.context.planning_indicators,
                "threat_level": result.context.threat_level
            }
        
        return DetectionResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.post("/api/v1/detect/batch", response_model=BatchDetectionResponse)
async def detect_suspicious_text_batch(
    request: BatchDetectionRequest,
    detector: EnhancedSuspiciousDetector = Depends(get_detector),
    analytics: AnalyticsEngine = Depends(get_analytics)
):
    """Detect suspicious content in multiple texts"""
    try:
        start_time = time.time()
        results = []
        errors = []
        
        # Process texts in parallel
        tasks = []
        for i, text in enumerate(request.texts):
            task = asyncio.create_task(
                detector.analyze_text(text, request.language)
            )
            tasks.append((i, task))
        
        # Wait for all tasks to complete
        for i, task in tasks:
            try:
                text_results = await task
                if text_results:
                    result = text_results[0]
                    results.append(DetectionResponse(
                        detection_id=result.detection_id,
                        timestamp=result.timestamp,
                        text=result.text,
                        language=result.language,
                        confidence=result.confidence,
                        severity=result.severity.value,
                        flags=result.flags,
                        detection_method=result.detection_method.value,
                        explanation={
                            "reasoning": result.explanation.reasoning,
                            "confidence_factors": result.explanation.confidence_factors
                        } if request.include_explanation else None,
                        context={
                            "threat_level": result.context.threat_level,
                            "planning_indicators": result.context.planning_indicators
                        } if request.include_context else None,
                        processing_time=0.0,  # Will be calculated per result
                        metadata=result.metadata
                    ))
                else:
                    # No suspicious content detected
                    results.append(DetectionResponse(
                        detection_id=f"det_{int(time.time())}_{i}",
                        timestamp=datetime.now().isoformat(),
                        text=text,
                        language=request.language or "auto",
                        confidence=0.0,
                        severity="INFO",
                        flags=[],
                        detection_method="none",
                        explanation={"reasoning": "No suspicious content detected"} if request.include_explanation else None,
                        context={"threat_level": "LOW"} if request.include_context else None,
                        processing_time=0.0,
                        metadata={"text_length": len(text)}
                    ))
            except Exception as e:
                errors.append({
                    "index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        
        return BatchDetectionResponse(
            results=results,
            total_processed=len(results),
            processing_time=processing_time,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Batch detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary(
    hours: int = Query(24, description="Time period in hours", ge=1, le=168),
    analytics: AnalyticsEngine = Depends(get_analytics)
):
    """Get analytics summary for specified time period"""
    try:
        summary = analytics.get_summary(hours=hours)
        return {
            "time_period_hours": hours,
            "total_detections": summary.total_detections,
            "average_confidence": summary.average_confidence,
            "severity_distribution": summary.severity_distribution,
            "language_distribution": summary.language_distribution,
            "method_distribution": summary.method_distribution,
            "flag_frequency": summary.flag_frequency,
            "processing_time_stats": summary.processing_time_stats,
            "high_confidence_detections": summary.high_confidence_detections,
            "false_positive_estimate": summary.false_positive_estimate
        }
    except Exception as e:
        logger.error(f"Analytics summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics summary failed: {str(e)}")

@app.get("/api/v1/analytics/performance")
async def get_performance_metrics(
    analytics: AnalyticsEngine = Depends(get_analytics)
):
    """Get system performance metrics"""
    try:
        return analytics.get_performance_metrics()
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

@app.get("/api/v1/analytics/languages")
async def get_language_analytics(
    analytics: AnalyticsEngine = Depends(get_analytics)
):
    """Get language-specific analytics"""
    try:
        return analytics.get_language_analytics()
    except Exception as e:
        logger.error(f"Language analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Language analytics failed: {str(e)}")

@app.get("/api/v1/analytics/flags")
async def get_flag_analytics(
    analytics: AnalyticsEngine = Depends(get_analytics)
):
    """Get flag frequency analytics"""
    try:
        return analytics.get_flag_analytics()
    except Exception as e:
        logger.error(f"Flag analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Flag analytics failed: {str(e)}")

@app.post("/api/v1/lightweight/detect")
async def detect_lightweight(
    request: DetectionRequest,
    lightweight_detector = Depends(get_lightweight_detector)
):
    """Detect suspicious content using lightweight models"""
    try:
        result = lightweight_detector.comprehensive_analysis(request.text)
        
        return {
            "text": request.text,
            "suspicious_score": result["suspicious_score"],
            "confidence": result["confidence"],
            "flags": result["flags"],
            "predictions": [
                {
                    "label": pred.label,
                    "confidence": pred.confidence,
                    "model": pred.model_name
                } for pred in result.get("predictions", [])
            ],
            "analysis_time": result["analysis_time"]
        }
    except Exception as e:
        logger.error(f"Lightweight detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Lightweight detection failed: {str(e)}")

@app.get("/api/v1/models/info")
async def get_model_info(
    lightweight_detector = Depends(get_lightweight_detector)
):
    """Get information about loaded models"""
    try:
        return lightweight_detector.model_manager.get_model_info()
    except Exception as e:
        logger.error(f"Model info failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model info failed: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )