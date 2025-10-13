"""
Streamlit Dashboard for Suspicious Text Detection Analytics

This module provides an interactive web dashboard for visualizing
detection analytics, trends, and system performance.

Author: AI Assistant
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from analytics_engine import AnalyticsEngine, create_analytics_engine
    from enhanced_text_detection import EnhancedSuspiciousDetector, analyze_text_enhanced_sync
    from lightweight_models import create_lightweight_detector
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Suspicious Text Detection Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .alert-low {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def load_analytics_data():
    """Load analytics data"""
    try:
        engine = create_analytics_engine()
        return engine
    except Exception as e:
        st.error(f"Failed to load analytics data: {e}")
        return None

def create_confidence_trend_chart(confidence_trends):
    """Create confidence trend chart"""
    if not confidence_trends:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=confidence_trends,
        mode='lines+markers',
        name='Average Confidence',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Confidence Trends Over Time",
        xaxis_title="Time (Hours)",
        yaxis_title="Average Confidence",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_severity_distribution_chart(severity_distribution):
    """Create severity distribution pie chart"""
    if not severity_distribution:
        return None
    
    colors = {
        'CRITICAL': '#d32f2f',
        'HIGH': '#f57c00',
        'MEDIUM': '#fbc02d',
        'LOW': '#388e3c',
        'INFO': '#1976d2'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(severity_distribution.keys()),
        values=list(severity_distribution.values()),
        marker_colors=[colors.get(severity, '#757575') for severity in severity_distribution.keys()],
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Severity Distribution",
        height=400
    )
    
    return fig

def create_language_distribution_chart(language_distribution):
    """Create language distribution bar chart"""
    if not language_distribution:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=list(language_distribution.keys()),
        y=list(language_distribution.values()),
        marker_color='#1f77b4'
    )])
    
    fig.update_layout(
        title="Language Distribution",
        xaxis_title="Language",
        yaxis_title="Number of Detections",
        height=400
    )
    
    return fig

def create_flag_frequency_chart(flag_frequency, top_n=15):
    """Create flag frequency horizontal bar chart"""
    if not flag_frequency:
        return None
    
    # Get top N flags
    top_flags = dict(list(flag_frequency.items())[:top_n])
    
    fig = go.Figure(data=[go.Bar(
        y=list(top_flags.keys()),
        x=list(top_flags.values()),
        orientation='h',
        marker_color='#ff7f0e'
    )])
    
    fig.update_layout(
        title=f"Top {top_n} Most Frequent Flags",
        xaxis_title="Frequency",
        yaxis_title="Flag",
        height=500
    )
    
    return fig

def create_processing_time_chart(processing_time_stats):
    """Create processing time statistics chart"""
    if not processing_time_stats:
        return None
    
    stats = processing_time_stats
    metrics = ['Mean', 'Median', 'Min', 'Max']
    values = [stats.get('mean', 0), stats.get('median', 0), 
              stats.get('min', 0), stats.get('max', 0)]
    
    fig = go.Figure(data=[go.Bar(
        x=metrics,
        y=values,
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    )])
    
    fig.update_layout(
        title="Processing Time Statistics (seconds)",
        xaxis_title="Metric",
        yaxis_title="Time (seconds)",
        height=400
    )
    
    return fig

def main():
    """Main dashboard application"""
    st.markdown('<h1 class="main-header">🔍 Suspicious Text Detection Dashboard</h1>', unsafe_allow_html=True)
    
    # Load analytics data
    analytics_engine = load_analytics_data()
    if not analytics_engine:
        st.error("Failed to load analytics data. Please check the logs directory.")
        return
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Time period selection
    time_period = st.sidebar.selectbox(
        "Time Period",
        options=[1, 6, 12, 24, 48, 72, 168],  # hours
        index=3,  # Default to 24 hours
        format_func=lambda x: f"{x} hours" if x < 24 else f"{x//24} days" if x >= 24 else f"{x} hours"
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Get analytics summary
    summary = analytics_engine.get_summary(hours=time_period)
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Detections",
            value=summary.total_detections,
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Confidence",
            value=f"{summary.average_confidence:.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="High Confidence",
            value=summary.high_confidence_detections,
            delta=None
        )
    
    with col4:
        st.metric(
            label="False Positive Est.",
            value=f"{summary.false_positive_estimate:.1%}",
            delta=None
        )
    
    # Alert cards for high-confidence detections
    if summary.high_confidence_detections > 0:
        alert_class = "alert-high" if summary.high_confidence_detections > 10 else "alert-medium"
        st.markdown(f"""
        <div class="metric-card {alert_class}">
            <h4>⚠️ High Confidence Detections Alert</h4>
            <p>{summary.high_confidence_detections} detections with confidence > 0.8 in the last {time_period} hours</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts section
    st.header("📊 Analytics Charts")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Severity distribution
        severity_chart = create_severity_distribution_chart(summary.severity_distribution)
        if severity_chart:
            st.plotly_chart(severity_chart, use_container_width=True)
        
        # Language distribution
        language_chart = create_language_distribution_chart(summary.language_distribution)
        if language_chart:
            st.plotly_chart(language_chart, use_container_width=True)
    
    with col2:
        # Confidence trends
        confidence_chart = create_confidence_trend_chart(summary.confidence_trends)
        if confidence_chart:
            st.plotly_chart(confidence_chart, use_container_width=True)
        
        # Processing time statistics
        processing_chart = create_processing_time_chart(summary.processing_time_stats)
        if processing_chart:
            st.plotly_chart(processing_chart, use_container_width=True)
    
    # Flag frequency chart (full width)
    st.subheader("🏷️ Flag Frequency Analysis")
    flag_chart = create_flag_frequency_chart(summary.flag_frequency)
    if flag_chart:
        st.plotly_chart(flag_chart, use_container_width=True)
    
    # Detailed analytics section
    st.header("📈 Detailed Analytics")
    
    # Tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs(["Performance", "Language Analysis", "Flag Analysis", "Raw Data"])
    
    with tab1:
        st.subheader("System Performance Metrics")
        performance = analytics_engine.get_performance_metrics()
        
        if "error" not in performance:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Throughput", f"{performance.get('throughput_per_hour', 0):.1f} detections/hour")
                st.metric("Avg Processing Time", f"{performance.get('avg_processing_time', 0):.3f}s")
            
            with col2:
                st.metric("Median Processing Time", f"{performance.get('median_processing_time', 0):.3f}s")
                st.metric("Data Quality", f"{performance.get('data_quality', {}).get('complete_detections', 0)} complete")
            
            # Method performance table
            if performance.get('method_performance'):
                st.subheader("Detection Method Performance")
                method_df = pd.DataFrame(performance['method_performance']).T
                st.dataframe(method_df, use_container_width=True)
        else:
            st.error(f"Performance data error: {performance['error']}")
    
    with tab2:
        st.subheader("Language-Specific Analytics")
        language_analytics = analytics_engine.get_language_analytics()
        
        if "error" not in language_analytics:
            for language, stats in language_analytics.items():
                with st.expander(f"Language: {language}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Detections", stats['detection_count'])
                        st.metric("Avg Confidence", f"{stats['avg_confidence']:.2f}")
                    
                    with col2:
                        st.metric("Confidence Std", f"{stats['confidence_std']:.2f}")
                        st.metric("Avg Processing Time", f"{stats['avg_processing_time']:.3f}s")
                    
                    with col3:
                        if stats['severity_distribution']:
                            st.write("**Severity Distribution:**")
                            for severity, count in stats['severity_distribution'].items():
                                st.write(f"- {severity}: {count}")
        else:
            st.error(f"Language analytics error: {language_analytics['error']}")
    
    with tab3:
        st.subheader("Flag Analysis")
        flag_analytics = analytics_engine.get_flag_analytics()
        
        if "error" not in flag_analytics:
            # Top flags table
            flag_data = []
            for flag, stats in flag_analytics.items():
                flag_data.append({
                    'Flag': flag,
                    'Frequency': stats['frequency'],
                    'Percentage': f"{stats['percentage']:.1f}%",
                    'Avg Confidence': f"{stats['avg_confidence']:.2f}",
                    'Confidence Std': f"{stats['confidence_std']:.2f}"
                })
            
            if flag_data:
                flag_df = pd.DataFrame(flag_data)
                st.dataframe(flag_df, use_container_width=True)
                
                # Flag co-occurrence analysis
                st.subheader("Flag Co-occurrence Analysis")
                co_occurrence_data = []
                for flag, stats in flag_analytics.items():
                    if stats.get('co_occurrence'):
                        for co_flag, count in stats['co_occurrence'].items():
                            co_occurrence_data.append({
                                'Primary Flag': flag,
                                'Co-occurring Flag': co_flag,
                                'Count': count
                            })
                
                if co_occurrence_data:
                    co_df = pd.DataFrame(co_occurrence_data)
                    co_df = co_df.sort_values('Count', ascending=False)
                    st.dataframe(co_df.head(20), use_container_width=True)
        else:
            st.error(f"Flag analytics error: {flag_analytics['error']}")
    
    with tab4:
        st.subheader("Raw Detection Data")
        
        # Show recent detections
        if analytics_engine.detections:
            # Convert to DataFrame for display
            detection_data = []
            for detection in analytics_engine.detections[-50:]:  # Show last 50
                detection_data.append({
                    'ID': detection.detection_id,
                    'Timestamp': detection.timestamp,
                    'Language': detection.language,
                    'Confidence': f"{detection.confidence:.2f}",
                    'Severity': detection.severity,
                    'Method': detection.method,
                    'Flags': ', '.join(detection.flags),
                    'Processing Time': f"{detection.processing_time:.3f}s"
                })
            
            detection_df = pd.DataFrame(detection_data)
            st.dataframe(detection_df, use_container_width=True)
            
            # Download button
            csv = detection_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Detection Data (CSV)",
                data=csv,
                file_name=f"detection_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No detection data available")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

if __name__ == "__main__":
    main()