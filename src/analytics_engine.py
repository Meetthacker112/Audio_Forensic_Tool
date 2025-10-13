"""
Analytics Engine for Suspicious Text Detection

This module provides comprehensive analytics, metrics, and reporting
for the suspicious text detection system.

Author: AI Assistant
Version: 2.0.0
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import statistics

try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    _PANDAS_AVAILABLE = False

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    np = None
    _NUMPY_AVAILABLE = False


@dataclass
class DetectionMetrics:
    """Metrics for a single detection"""
    detection_id: str
    timestamp: str
    language: str
    confidence: float
    severity: str
    flags: List[str]
    method: str
    text_length: int
    processing_time: float
    context_indicators: Dict[str, int]


@dataclass
class AnalyticsSummary:
    """Summary of analytics data"""
    total_detections: int
    time_period: str
    average_confidence: float
    severity_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    method_distribution: Dict[str, int]
    flag_frequency: Dict[str, int]
    processing_time_stats: Dict[str, float]
    confidence_trends: List[float]
    high_confidence_detections: int
    false_positive_estimate: float


class AnalyticsEngine:
    """Main analytics engine for detection data"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir or Path(__file__).parent.parent / "logs"
        self.data_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.detections: List[DetectionMetrics] = []
        self.metrics_cache: Dict[str, Any] = {}
        self.cache_timestamp: Optional[float] = None
        self.cache_duration = 300  # 5 minutes
        
        # Load existing data
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical detection data"""
        try:
            analytics_file = self.data_dir / "detection_analytics.json"
            if analytics_file.exists():
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line.strip())
                            self.detections.append(DetectionMetrics(**data))
                
                self.logger.info(f"Loaded {len(self.detections)} historical detections")
        except Exception as e:
            self.logger.error(f"Failed to load historical data: {e}")
    
    def log_detection(self, detection_data: Dict[str, Any]):
        """Log a new detection for analytics"""
        try:
            # Create detection metrics
            metrics = DetectionMetrics(
                detection_id=detection_data.get("detection_id", f"det_{int(time.time())}"),
                timestamp=detection_data.get("timestamp", datetime.now().isoformat()),
                language=detection_data.get("language", "unknown"),
                confidence=detection_data.get("confidence", 0.0),
                severity=detection_data.get("severity", "LOW"),
                flags=detection_data.get("flags", []),
                method=detection_data.get("method", "unknown"),
                text_length=detection_data.get("text_length", 0),
                processing_time=detection_data.get("processing_time", 0.0),
                context_indicators=detection_data.get("context_indicators", {})
            )
            
            # Add to in-memory storage
            self.detections.append(metrics)
            
            # Append to file
            analytics_file = self.data_dir / "detection_analytics.json"
            with open(analytics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(metrics)) + '\n')
            
            # Invalidate cache
            self.cache_timestamp = None
            
            self.logger.debug(f"Logged detection: {metrics.detection_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to log detection: {e}")
    
    def get_summary(self, hours: int = 24) -> AnalyticsSummary:
        """Get analytics summary for specified time period"""
        # Check cache
        if (self.cache_timestamp and 
            time.time() - self.cache_timestamp < self.cache_duration and
            "summary" in self.metrics_cache):
            return self.metrics_cache["summary"]
        
        try:
            # Filter detections by time period
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_detections = [
                d for d in self.detections
                if datetime.fromisoformat(d.timestamp) >= cutoff_time
            ]
            
            if not recent_detections:
                return AnalyticsSummary(
                    total_detections=0,
                    time_period=f"{hours}h",
                    average_confidence=0.0,
                    severity_distribution={},
                    language_distribution={},
                    method_distribution={},
                    flag_frequency={},
                    processing_time_stats={},
                    confidence_trends=[],
                    high_confidence_detections=0,
                    false_positive_estimate=0.0
                )
            
            # Calculate metrics
            confidences = [d.confidence for d in recent_detections]
            processing_times = [d.processing_time for d in recent_detections]
            
            # Severity distribution
            severity_counts = Counter(d.severity for d in recent_detections)
            
            # Language distribution
            language_counts = Counter(d.language for d in recent_detections)
            
            # Method distribution
            method_counts = Counter(d.method for d in recent_detections)
            
            # Flag frequency
            all_flags = []
            for d in recent_detections:
                all_flags.extend(d.flags)
            flag_counts = Counter(all_flags)
            
            # Processing time statistics
            processing_stats = {
                "mean": statistics.mean(processing_times) if processing_times else 0.0,
                "median": statistics.median(processing_times) if processing_times else 0.0,
                "min": min(processing_times) if processing_times else 0.0,
                "max": max(processing_times) if processing_times else 0.0,
                "std": statistics.stdev(processing_times) if len(processing_times) > 1 else 0.0
            }
            
            # Confidence trends (hourly averages)
            confidence_trends = self._calculate_confidence_trends(recent_detections, hours)
            
            # High confidence detections
            high_confidence_count = sum(1 for d in recent_detections if d.confidence > 0.8)
            
            # False positive estimate (based on very low confidence detections)
            false_positive_count = sum(1 for d in recent_detections if d.confidence < 0.3)
            false_positive_estimate = false_positive_count / len(recent_detections) if recent_detections else 0.0
            
            summary = AnalyticsSummary(
                total_detections=len(recent_detections),
                time_period=f"{hours}h",
                average_confidence=statistics.mean(confidences) if confidences else 0.0,
                severity_distribution=dict(severity_counts),
                language_distribution=dict(language_counts),
                method_distribution=dict(method_counts),
                flag_frequency=dict(flag_counts),
                processing_time_stats=processing_stats,
                confidence_trends=confidence_trends,
                high_confidence_detections=high_confidence_count,
                false_positive_estimate=false_positive_estimate
            )
            
            # Cache the result
            self.metrics_cache["summary"] = summary
            self.cache_timestamp = time.time()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return AnalyticsSummary(
                total_detections=0,
                time_period=f"{hours}h",
                average_confidence=0.0,
                severity_distribution={},
                language_distribution={},
                method_distribution={},
                flag_frequency={},
                processing_time_stats={},
                confidence_trends=[],
                high_confidence_detections=0,
                false_positive_estimate=0.0
            )
    
    def _calculate_confidence_trends(self, detections: List[DetectionMetrics], hours: int) -> List[float]:
        """Calculate confidence trends over time"""
        try:
            # Group detections by hour
            hourly_confidences = defaultdict(list)
            
            for detection in detections:
                dt = datetime.fromisoformat(detection.timestamp)
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                hourly_confidences[hour_key].append(detection.confidence)
            
            # Calculate hourly averages
            trends = []
            for hour in sorted(hourly_confidences.keys()):
                avg_confidence = statistics.mean(hourly_confidences[hour])
                trends.append(avg_confidence)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to calculate confidence trends: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the system"""
        try:
            if not self.detections:
                return {"error": "No detection data available"}
            
            # Calculate performance metrics
            total_detections = len(self.detections)
            processing_times = [d.processing_time for d in self.detections]
            confidences = [d.confidence for d in self.detections]
            
            # Throughput metrics
            if self.detections:
                first_detection = min(datetime.fromisoformat(d.timestamp) for d in self.detections)
                last_detection = max(datetime.fromisoformat(d.timestamp) for d in self.detections)
                time_span = (last_detection - first_detection).total_seconds() / 3600  # hours
                throughput = total_detections / time_span if time_span > 0 else 0
            else:
                throughput = 0
            
            # Accuracy estimates
            high_confidence_ratio = sum(1 for c in confidences if c > 0.8) / total_detections
            medium_confidence_ratio = sum(1 for c in confidences if 0.5 <= c <= 0.8) / total_detections
            low_confidence_ratio = sum(1 for c in confidences if c < 0.5) / total_detections
            
            # Method performance
            method_performance = {}
            for method in set(d.method for d in self.detections):
                method_detections = [d for d in self.detections if d.method == method]
                if method_detections:
                    method_confidences = [d.confidence for d in method_detections]
                    method_performance[method] = {
                        "count": len(method_detections),
                        "avg_confidence": statistics.mean(method_confidences),
                        "avg_processing_time": statistics.mean([d.processing_time for d in method_detections])
                    }
            
            return {
                "total_detections": total_detections,
                "throughput_per_hour": throughput,
                "avg_processing_time": statistics.mean(processing_times) if processing_times else 0,
                "median_processing_time": statistics.median(processing_times) if processing_times else 0,
                "avg_confidence": statistics.mean(confidences) if confidences else 0,
                "confidence_distribution": {
                    "high": high_confidence_ratio,
                    "medium": medium_confidence_ratio,
                    "low": low_confidence_ratio
                },
                "method_performance": method_performance,
                "data_quality": {
                    "complete_detections": sum(1 for d in self.detections if d.confidence > 0),
                    "incomplete_detections": sum(1 for d in self.detections if d.confidence == 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance metrics: {e}")
            return {"error": str(e)}
    
    def get_language_analytics(self) -> Dict[str, Any]:
        """Get analytics specific to language detection"""
        try:
            language_stats = defaultdict(lambda: {
                "count": 0,
                "confidences": [],
                "severities": [],
                "flags": [],
                "processing_times": []
            })
            
            for detection in self.detections:
                lang = detection.language
                language_stats[lang]["count"] += 1
                language_stats[lang]["confidences"].append(detection.confidence)
                language_stats[lang]["severities"].append(detection.severity)
                language_stats[lang]["flags"].extend(detection.flags)
                language_stats[lang]["processing_times"].append(detection.processing_time)
            
            # Calculate statistics for each language
            result = {}
            for lang, stats in language_stats.items():
                result[lang] = {
                    "detection_count": stats["count"],
                    "avg_confidence": statistics.mean(stats["confidences"]) if stats["confidences"] else 0,
                    "confidence_std": statistics.stdev(stats["confidences"]) if len(stats["confidences"]) > 1 else 0,
                    "severity_distribution": dict(Counter(stats["severities"])),
                    "top_flags": dict(Counter(stats["flags"]).most_common(10)),
                    "avg_processing_time": statistics.mean(stats["processing_times"]) if stats["processing_times"] else 0
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to calculate language analytics: {e}")
            return {"error": str(e)}
    
    def get_flag_analytics(self) -> Dict[str, Any]:
        """Get analytics for detected flags"""
        try:
            all_flags = []
            flag_confidences = defaultdict(list)
            flag_severities = defaultdict(list)
            flag_languages = defaultdict(list)
            
            for detection in self.detections:
                for flag in detection.flags:
                    all_flags.append(flag)
                    flag_confidences[flag].append(detection.confidence)
                    flag_severities[flag].append(detection.severity)
                    flag_languages[flag].append(detection.language)
            
            flag_counts = Counter(all_flags)
            
            # Calculate statistics for each flag
            result = {}
            for flag, count in flag_counts.most_common(20):  # Top 20 flags
                result[flag] = {
                    "frequency": count,
                    "percentage": (count / len(all_flags)) * 100 if all_flags else 0,
                    "avg_confidence": statistics.mean(flag_confidences[flag]) if flag_confidences[flag] else 0,
                    "confidence_std": statistics.stdev(flag_confidences[flag]) if len(flag_confidences[flag]) > 1 else 0,
                    "severity_distribution": dict(Counter(flag_severities[flag])),
                    "language_distribution": dict(Counter(flag_languages[flag])),
                    "co_occurrence": self._calculate_flag_co_occurrence(flag, all_flags)
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to calculate flag analytics: {e}")
            return {"error": str(e)}
    
    def _calculate_flag_co_occurrence(self, target_flag: str, all_flags: List[str]) -> Dict[str, int]:
        """Calculate co-occurrence of flags"""
        try:
            co_occurrence = defaultdict(int)
            
            # Group flags by detection (assuming they're in order)
            # This is a simplified approach - in practice, you'd need to track which flags came from which detection
            for i, flag in enumerate(all_flags):
                if flag == target_flag:
                    # Look at surrounding flags
                    for j in range(max(0, i-2), min(len(all_flags), i+3)):
                        if j != i and all_flags[j] != target_flag:
                            co_occurrence[all_flags[j]] += 1
            
            return dict(co_occurrence)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate flag co-occurrence: {e}")
            return {}
    
    def export_analytics(self, output_path: Path, format: str = "json") -> bool:
        """Export analytics data to file"""
        try:
            if format.lower() == "json":
                data = {
                    "summary": asdict(self.get_summary()),
                    "performance_metrics": self.get_performance_metrics(),
                    "language_analytics": self.get_language_analytics(),
                    "flag_analytics": self.get_flag_analytics(),
                    "export_timestamp": datetime.now().isoformat()
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv" and _PANDAS_AVAILABLE:
                # Convert detections to DataFrame and export
                df_data = []
                for detection in self.detections:
                    row = asdict(detection)
                    row['flags'] = '|'.join(detection.flags)  # Convert list to string
                    df_data.append(row)
                
                df = pd.DataFrame(df_data)
                df.to_csv(output_path, index=False)
            
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False
            
            self.logger.info(f"Analytics exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export analytics: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generate a human-readable analytics report"""
        try:
            summary = self.get_summary()
            performance = self.get_performance_metrics()
            language_analytics = self.get_language_analytics()
            flag_analytics = self.get_flag_analytics()
            
            report_lines = [
                "SUSPICIOUS TEXT DETECTION - ANALYTICS REPORT",
                "=" * 60,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Time Period: {summary.time_period}",
                "",
                "OVERVIEW",
                "-" * 20,
                f"Total Detections: {summary.total_detections}",
                f"Average Confidence: {summary.average_confidence:.2f}",
                f"High Confidence Detections: {summary.high_confidence_detections}",
                f"False Positive Estimate: {summary.false_positive_estimate:.1%}",
                "",
                "SEVERITY DISTRIBUTION",
                "-" * 25,
            ]
            
            for severity, count in summary.severity_distribution.items():
                percentage = (count / summary.total_detections) * 100 if summary.total_detections > 0 else 0
                report_lines.append(f"{severity}: {count} ({percentage:.1f}%)")
            
            report_lines.extend([
                "",
                "LANGUAGE DISTRIBUTION",
                "-" * 25,
            ])
            
            for language, count in summary.language_distribution.items():
                percentage = (count / summary.total_detections) * 100 if summary.total_detections > 0 else 0
                report_lines.append(f"{language}: {count} ({percentage:.1f}%)")
            
            report_lines.extend([
                "",
                "DETECTION METHOD DISTRIBUTION",
                "-" * 35,
            ])
            
            for method, count in summary.method_distribution.items():
                percentage = (count / summary.total_detections) * 100 if summary.total_detections > 0 else 0
                report_lines.append(f"{method}: {count} ({percentage:.1f}%)")
            
            report_lines.extend([
                "",
                "TOP FLAGS",
                "-" * 10,
            ])
            
            for flag, count in list(summary.flag_frequency.items())[:10]:
                percentage = (count / sum(summary.flag_frequency.values())) * 100 if summary.flag_frequency else 0
                report_lines.append(f"{flag}: {count} ({percentage:.1f}%)")
            
            if "throughput_per_hour" in performance:
                report_lines.extend([
                    "",
                    "PERFORMANCE METRICS",
                    "-" * 20,
                    f"Throughput: {performance['throughput_per_hour']:.1f} detections/hour",
                    f"Average Processing Time: {performance['avg_processing_time']:.3f}s",
                    f"Median Processing Time: {performance['median_processing_time']:.3f}s",
                ])
            
            return "\n".join(report_lines)
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return f"Error generating report: {e}"


# Convenience functions
def create_analytics_engine(data_dir: Optional[Path] = None) -> AnalyticsEngine:
    """Create an analytics engine instance"""
    return AnalyticsEngine(data_dir)


def log_detection_for_analytics(detection_data: Dict[str, Any], data_dir: Optional[Path] = None):
    """Quick function to log detection data for analytics"""
    engine = create_analytics_engine(data_dir)
    engine.log_detection(detection_data)


if __name__ == "__main__":
    # Example usage
    engine = create_analytics_engine()
    
    # Generate and print report
    report = engine.generate_report()
    print(report)
    
    # Export analytics
    output_path = Path("analytics_export.json")
    if engine.export_analytics(output_path):
        print(f"\nAnalytics exported to {output_path}")