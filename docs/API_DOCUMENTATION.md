# API Documentation

## Overview

The Forensic Audio Analysis Tool provides a RESTful API for programmatic access to audio analysis features. The API is built with FastAPI and supports both synchronous and asynchronous operations.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, implement API key authentication.

## Endpoints

### Health Check

**GET** `/health`

Check API server status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Upload Audio

**POST** `/api/upload`

Upload an audio file for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (audio file)

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "audio.wav",
  "size": 1024000,
  "duration": 120.5
}
```

### Analyze Audio

**POST** `/api/analyze/{file_id}`

Perform forensic analysis on uploaded audio.

**Parameters:**
- `file_id` (path): UUID of uploaded file
- `options` (body): Analysis configuration

**Request Body:**
```json
{
  "transcription": true,
  "speaker_diarization": true,
  "keyword_detection": true,
  "emotion_analysis": true,
  "anomaly_detection": true,
  "ai_insights": true,
  "language": "en"
}
```

**Response:**
```json
{
  "analysis_id": "uuid-string",
  "status": "completed",
  "results": {
    "transcription": "...",
    "speakers": [...],
    "keywords": [...],
    "emotions": {...},
    "anomalies": [...],
    "ai_insights": {...}
  }
}
```

### Get Analysis Status

**GET** `/api/analysis/{analysis_id}/status`

Check analysis progress.

**Response:**
```json
{
  "analysis_id": "uuid-string",
  "status": "processing",
  "progress": 65,
  "estimated_time": 30
}
```

### Generate Report

**POST** `/api/report/{analysis_id}`

Generate forensic report.

**Request Body:**
```json
{
  "format": "pdf",
  "include_visualizations": true,
  "include_ai_insights": true
}
```

**Response:**
```json
{
  "report_id": "uuid-string",
  "download_url": "/api/download/report/uuid-string",
  "format": "pdf"
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

**Error Format:**
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## WebSocket Support

Real-time analysis updates via WebSocket:

```javascript
ws://localhost:8000/ws/analysis/{analysis_id}
```

**Message Format:**
```json
{
  "type": "progress",
  "data": {
    "progress": 75,
    "stage": "keyword_detection"
  }
}
```
