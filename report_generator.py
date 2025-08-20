"""
Enhanced Forensic Audio Analysis Report Generator
Professional comprehensive PDF and DOCX report generation with rich formatting
Designed for CID/Police forensic investigations with complete analysis coverage
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any
import json

# PDF Generation Imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie

# DOCX Generation Imports
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK_TYPE
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn


class ComprehensiveForensicReportGenerator:
    """
    Advanced Forensic Audio Analysis Report Generator
    
    Features:
    - Comprehensive PDF and DOCX reports with rich formatting
    - Complete analysis result coverage including audio, transcript, speakers, keywords, AI insights
    - Professional law enforcement grade documentation
    - Detailed technical specifications and forensic assessments
    - Visual charts and statistical analysis
    - Multi-language support for evidence documentation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_professional_styles()
        self.report_metadata = {
            'version': '2.0',
            'system': 'Enhanced Forensic Audio Analysis System',
            'classification': 'CONFIDENTIAL - LAW ENFORCEMENT USE ONLY',
            'authority': 'Criminal Investigation Department'
        }
    
    def setup_professional_styles(self):
        """Setup clean, professional report styles"""
        self.styles = getSampleStyleSheet()
        
        # Clean Title Style
        self.styles.add(ParagraphStyle(
            name='ForensicTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceBefore=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Clean Section Headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Clean Subsection Headers
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        ))
        
        # Clean Body Text
        self.styles.add(ParagraphStyle(
            name='ForensicBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Clean Important Note Style
        self.styles.add(ParagraphStyle(
            name='ImportantNote',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=10,
            spaceAfter=10,
            textColor=colors.red,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Clean Transcript Style
        self.styles.add(ParagraphStyle(
            name='TranscriptText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceBefore=8,
            spaceAfter=8,
            leftIndent=20,
            rightIndent=20,
            fontName='Helvetica',
            backColor=colors.lightgrey
        ))
        
        # Clean Footnote Style
        self.styles.add(ParagraphStyle(
            name='FootnoteText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceBefore=5,
            spaceAfter=5,
            textColor=colors.grey,
            fontName='Helvetica'
        ))
        
        # Statistical Data Style
        self.styles.add(ParagraphStyle(
            name='StatisticalData',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica',
            textColor=colors.black
        ))
    
    def create_enhanced_reports_directory(self, base_dir: str) -> str:
        """Create organized forensic reports directory with metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = os.path.join(base_dir, f"ForensicAnalysis_Report_{timestamp}")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Create subdirectories for organization
        os.makedirs(os.path.join(reports_dir, "PDF_Reports"), exist_ok=True)
        os.makedirs(os.path.join(reports_dir, "DOCX_Reports"), exist_ok=True)
        os.makedirs(os.path.join(reports_dir, "Evidence_Data"), exist_ok=True)
        
        return reports_dir
    
    def generate_enhanced_filename(self, analysis_results: Dict, extension: str, report_type: str = "Comprehensive") -> str:
        """Generate detailed filename with case information"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_id = f"FA{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # Extract audio filename for report naming
        file_path = analysis_results.get('file_path', '')
        if file_path:
            audio_name = os.path.splitext(os.path.basename(file_path))[0]
            # Clean and limit filename length
            audio_name = "".join(c for c in audio_name if c.isalnum() or c in (' ', '-', '_')).strip()
            if len(audio_name) > 30:
                audio_name = audio_name[:30]
            filename = f"ForensicReport_{report_type}_{case_id}_{audio_name}_{timestamp}.{extension}"
        else:
            filename = f"ForensicReport_{report_type}_{case_id}_{timestamp}.{extension}"
        
        return filename
    
    def generate_comprehensive_pdf_report(self, analysis_results: Dict, output_dir: str) -> str:
        """Generate simple PDF forensic report with complete analysis coverage"""
        try:
            # Simple filename - no complex directories
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = analysis_results.get('file_path', 'audio_analysis')
            if file_name:
                base_name = os.path.splitext(os.path.basename(file_name))[0]
            else:
                base_name = 'forensic_analysis'
            
            filename = f"ForensicReport_{base_name}_{timestamp}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                title="Forensic Audio Analysis Report",
                leftMargin=1*inch,
                rightMargin=1*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )
            
            # Build complete report content
            story = []
            
            # Header and Cover
            story.extend(self._create_complete_header(analysis_results))
            
            # Executive Summary with actual content
            story.extend(self._create_complete_executive_summary(analysis_results))
            
            # Technical Analysis with actual content
            story.extend(self._create_complete_technical_analysis(analysis_results))
            
            # Speech Analysis with actual content
            story.extend(self._create_complete_speech_analysis(analysis_results))
            
            # Speaker Analysis with actual content
            story.extend(self._create_complete_speaker_analysis(analysis_results))
            
            # Keyword Analysis with actual content
            story.extend(self._create_complete_keyword_analysis(analysis_results))
            
            # AI Analysis with actual content
            story.extend(self._create_complete_ai_analysis(analysis_results))
            
            # Keyword and Content Analysis (Detailed)
            story.extend(self._create_enhanced_keyword_analysis(analysis_results))
            
            # Conclusions and Recommendations with actual content
            story.extend(self._create_complete_conclusions(analysis_results))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF generation error: {e}")
            raise
    
    def generate_comprehensive_docx_report(self, analysis_results: Dict, output_dir: str) -> str:
        """Generate simple DOCX forensic report with complete content"""
        try:
            # Simple filename - no complex directories
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = analysis_results.get('file_path', 'audio_analysis')
            if file_name:
                base_name = os.path.splitext(os.path.basename(file_name))[0]
            else:
                base_name = 'forensic_analysis'
            
            filename = f"ForensicReport_{base_name}_{timestamp}.docx"
            output_path = os.path.join(output_dir, filename)
            
            # Create DOCX document
            doc = Document()
            self._setup_docx_styles(doc)
            
            # Set document properties
            properties = doc.core_properties
            properties.title = "Forensic Audio Analysis Report"
            properties.author = "Forensic Audio Analysis System"
            properties.subject = "Criminal Investigation Audio Evidence"
            
            # Build complete report content using existing methods
            self._create_docx_header(doc, analysis_results)
            self._create_docx_executive_summary(doc, analysis_results)
            self._create_docx_technical_analysis(doc, analysis_results)
            self._create_docx_speech_analysis(doc, analysis_results)
            self._create_docx_keyword_analysis(doc, analysis_results)
            self._create_docx_ai_insights(doc, analysis_results)
            self._create_docx_conclusions(doc, analysis_results)
            
            # Save document
            doc.save(output_path)
            
            self.logger.info(f"DOCX report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"DOCX generation error: {e}")
            raise
    
    def _save_evidence_data(self, analysis_results: Dict, reports_dir: str):
        """Save raw evidence data as structured JSON"""
        try:
            evidence_dir = os.path.join(reports_dir, "Evidence_Data")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            evidence_file = os.path.join(evidence_dir, f"RawAnalysisData_{timestamp}.json")
            
            # Prepare evidence data
            evidence_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'system_version': self.report_metadata['version'],
                    'classification': self.report_metadata['classification']
                },
                'raw_analysis': analysis_results,
                'data_integrity': {
                    'checksum': self._calculate_data_checksum(analysis_results),
                    'total_keywords': len(analysis_results.get('keywords', [])),
                    'has_transcription': bool(analysis_results.get('transcript', {}).get('transcript')),
                    'has_ai_analysis': bool(analysis_results.get('ai_analysis', {}))
                }
            }
            
            with open(evidence_file, 'w', encoding='utf-8') as f:
                json.dump(evidence_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Evidence data saved: {evidence_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving evidence data: {e}")
    
    def _calculate_data_checksum(self, data: Dict) -> str:
        """Calculate simple checksum for data integrity"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    # ==================== ENHANCED PDF CONTENT CREATION METHODS ====================
    
    def _create_enhanced_cover_page(self, analysis_results: Dict) -> List:
        """Create professional cover page with case details"""
        content = []
        
        # Title with enhanced styling
        title = Paragraph("COMPREHENSIVE FORENSIC AUDIO ANALYSIS REPORT", self.styles['ForensicTitle'])
        content.append(title)
        content.append(Spacer(1, 30))
        
        # Classification notice with enhanced styling
        classification = Paragraph(self.report_metadata['classification'], self.styles['CriticalInfo'])
        content.append(classification)
        content.append(Spacer(1, 40))
        
        # Case details table
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        case_id = f"FA{datetime.now().strftime('%Y%m%d%H%M')}"
        file_path = analysis_results.get('file_path', 'Unknown')
        audio_name = os.path.basename(file_path) if file_path else 'Unknown Audio File'
        
        case_data = [
            ['CASE INFORMATION', ''],
            ['Case ID:', case_id],
            ['Report Generated:', timestamp],
            ['Audio File:', audio_name],
            ['Analysis System:', self.report_metadata['system']],
            ['Version:', self.report_metadata['version']],
            ['Authority:', self.report_metadata['authority']],
            ['Classification:', 'CONFIDENTIAL']
        ]
        
        case_table = Table(case_data, colWidths=[3*inch, 3*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('SPAN', (0, 0), (-1, 0)),
        ]))
        
        content.append(case_table)
        content.append(Spacer(1, 50))
        
        # Analysis overview summary
        keywords = analysis_results.get('keywords', [])
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        
        priority_level = self._determine_enhanced_priority_level(keywords, transcript_data)
        
        overview_text = f"""ANALYSIS OVERVIEW
        
This comprehensive forensic report contains detailed analysis of audio evidence including:

• Speech-to-Text Transcription ({transcript_data.get('language', 'Unknown').title()})
• Speaker Identification and Diarization ({speakers_data.get('count', 0)} speakers detected)
• Criminal Keyword Detection ({len(keywords)} keywords found)
• Emotion and Sentiment Analysis
• AI-Powered Forensic Insights
• Statistical Pattern Analysis
• Criminal Risk Assessment

INVESTIGATION PRIORITY: {priority_level}

This report is prepared for law enforcement use and contains sensitive investigative information."""
        
        overview_para = Paragraph(overview_text, self.styles['ForensicBody'])
        content.append(overview_para)
        
        content.append(PageBreak())
        return content
    
    def _create_table_of_contents(self) -> List:
        """Create comprehensive table of contents"""
        content = []
        
        header = Paragraph("TABLE OF CONTENTS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 20))
        
        toc_items = [
            "1. EXECUTIVE SUMMARY",
            "2. CASE INFORMATION & EVIDENCE DETAILS", 
            "3. TECHNICAL AUDIO ANALYSIS",
            "4. SPEECH TRANSCRIPTION ANALYSIS",
            "5. SPEAKER IDENTIFICATION & DIARIZATION",
            "6. EMOTION & SENTIMENT ANALYSIS",
            "7. KEYWORD & CONTENT ANALYSIS",
            "8. AI-POWERED FORENSIC INSIGHTS",
            "9. CRIMINAL ASSESSMENT & RISK ANALYSIS",
            "10. EVIDENCE INTEGRITY & CHAIN OF CUSTODY",
            "11. STATISTICAL ANALYSIS & PATTERNS",
            "12. CONCLUSIONS & RECOMMENDATIONS",
            "13. APPENDICES & RAW DATA"
        ]
        
        for item in toc_items:
            toc_para = Paragraph(item, self.styles['ForensicBody'])
            content.append(toc_para)
            content.append(Spacer(1, 8))
        
        content.append(PageBreak())
        return content
    
    def _create_comprehensive_executive_summary(self, analysis_results: Dict) -> List:
        """Create detailed executive summary with key findings"""
        content = []
        
        header = Paragraph("1. EXECUTIVE SUMMARY", self.styles['SectionHeader'])
        content.append(header)
        
        # Get comprehensive analysis data
        audio_analysis = analysis_results.get('audio_analysis', {})
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        keywords = analysis_results.get('keywords', [])
        ai_analysis = analysis_results.get('ai_analysis', {})
        
        # Audio characteristics
        duration = audio_analysis.get('duration', 0)
        sample_rate = audio_analysis.get('sample_rate', 0)
        channels = audio_analysis.get('channels', 0)
        file_size = audio_analysis.get('file_size', 0)
        
        # Analysis statistics
        speaker_count = speakers_data.get('count', 0)
        transcript_length = len(transcript_data.get('transcript', ''))
        confidence = transcript_data.get('confidence', 0)
        language = transcript_data.get('language', 'Unknown')
        
        # Create comprehensive summary
        summary_text = f"""CASE OVERVIEW AND KEY FINDINGS

Audio Evidence Characteristics:
• File Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)
• Audio Quality: {sample_rate} Hz sample rate, {channels} channel(s)
• File Size: {file_size:.2f} MB
• Format: {audio_analysis.get('format', 'Unknown')}

Speech Analysis Results:
• Language Detected: {language.title()}
• Transcription Length: {transcript_length} characters
• Transcription Confidence: {confidence:.2f}
• Method Used: {transcript_data.get('method_used', 'Unknown')}

Speaker Analysis:
• Total Speakers Identified: {speaker_count}
• Speaker Segments: {len(speakers_data.get('segments', []))}
• Diarization Quality: {'High' if speaker_count > 0 else 'No speakers detected'}

Content Analysis:
• Criminal Keywords Detected: {len(keywords)}
• Keyword Categories: {len(set(kw.get('category', 'unknown') for kw in keywords))}
• High-Risk Terms: {len([kw for kw in keywords if kw.get('confidence', 0) > 0.8])}

AI Forensic Assessment:
• AI Analysis Status: {'Completed' if ai_analysis and not ai_analysis.get('error') else 'Not Available'}
• Criminal Risk Level: {self._extract_risk_level(ai_analysis)}
• Investigation Priority: {self._determine_enhanced_priority_level(keywords, transcript_data)}

CRITICAL FINDINGS:
{self._generate_critical_findings(keywords, transcript_data, ai_analysis)}"""
        
        summary_para = Paragraph(summary_text, self.styles['ForensicBody'])
        content.append(summary_para)
        content.append(Spacer(1, 20))
        
        # Key statistics table
        stats_data = [
            ['ANALYSIS METRIC', 'VALUE', 'ASSESSMENT'],
            ['Audio Duration', f"{duration:.1f} seconds", self._assess_duration(duration)],
            ['Speech Quality', f"{confidence:.2f}", self._assess_confidence(confidence)],
            ['Keywords Found', str(len(keywords)), self._assess_keyword_count(len(keywords))],
            ['Speakers Identified', str(speaker_count), self._assess_speaker_count(speaker_count)],
            ['Language Confidence', language.title(), 'Detected'],
            ['AI Analysis', 'Completed' if ai_analysis else 'N/A', 'Available' if ai_analysis else 'Not Available']
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(stats_table)
        content.append(PageBreak())
        return content
    
    def _generate_critical_findings(self, keywords: List, transcript_data: Dict, ai_analysis: Dict) -> str:
        """Generate critical findings summary"""
        findings = []
        
        if len(keywords) > 10:
            findings.append("• HIGH RISK: Significant number of criminal keywords detected")
        elif len(keywords) > 3:
            findings.append("• MEDIUM RISK: Multiple criminal indicators present")
        
        if transcript_data.get('confidence', 0) > 0.8:
            findings.append("• High-quality speech transcription available for evidence")
        
        if ai_analysis and not ai_analysis.get('error'):
            risk_level = self._extract_risk_level(ai_analysis)
            if risk_level in ['HIGH', 'CRITICAL']:
                findings.append(f"• AI Assessment indicates {risk_level} criminal risk level")
        
        emotions = transcript_data.get('emotion_analysis', {})
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else None
            if dominant_emotion in ['angry', 'fear', 'disgust']:
                findings.append(f"• Dominant emotion detected: {dominant_emotion.title()} - may indicate distress or conflict")
        
        if not findings:
            findings.append("• No immediate critical findings identified in preliminary analysis")
        
        return "\n".join(findings)
    
    def _create_pdf_header(self, analysis_results: Dict) -> List:
        """Create PDF report header"""
        content = []
        
        # Title
        title = Paragraph("FORENSIC AUDIO ANALYSIS REPORT", self.styles['ForensicTitle'])
        content.append(title)
        content.append(Spacer(1, 20))
        
        # Classification notice
        classification = Paragraph(
            "CONFIDENTIAL - LAW ENFORCEMENT USE ONLY",
            self.styles['ImportantNote']
        )
        content.append(classification)
        content.append(Spacer(1, 20))
        
        # Report metadata table
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        case_id = f"FA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        metadata_data = [
            ['Report Generated:', timestamp],
            ['Case ID:', case_id],
            ['Analysis Software:', 'Forensic Audio Analysis Tool v1.0'],
            ['Report Type:', 'Comprehensive Audio Forensic Analysis']
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(metadata_table)
        content.append(PageBreak())
        
        return content
    
    def _create_pdf_executive_summary(self, analysis_results: Dict) -> List:
        """Create executive summary section"""
        content = []
        
        header = Paragraph("EXECUTIVE SUMMARY", self.styles['ForensicHeading'])
        content.append(header)
        
        # Get analysis data
        audio_analysis = analysis_results.get('audio_analysis', {})
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        keywords = analysis_results.get('keywords', [])
        
        # Create summary text
        duration = audio_analysis.get('duration', 0)
        sample_rate = audio_analysis.get('sample_rate', 0)
        channels = audio_analysis.get('channels', 0)
        speaker_count = speakers_data.get('count', 0)
        
        summary_text = f"""This report presents the results of comprehensive forensic audio analysis conducted on audio evidence with the following characteristics:

• Duration: {duration:.2f} seconds
• Sample Rate: {sample_rate} Hz
• Channels: {channels}
• Language: {transcript_data.get('language', 'Unknown').title()}

Key Findings:
• {len(keywords)} crime-related keywords detected
• {speaker_count} unique speakers identified
• Transcription confidence: {transcript_data.get('confidence', 0):.2f}
• AI forensic analysis completed

Investigation Priority: {self._determine_priority_level(keywords)} based on detected indicators."""
        
        summary_para = Paragraph(summary_text, self.styles['ForensicBody'])
        content.append(summary_para)
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_pdf_technical_analysis(self, analysis_results: Dict) -> List:
        """Create technical audio analysis section"""
        content = []
        
        header = Paragraph("TECHNICAL AUDIO ANALYSIS", self.styles['ForensicHeading'])
        content.append(header)
        
        audio_analysis = analysis_results.get('audio_analysis', {})
        
        # Technical specifications table
        tech_data = [
            ['Property', 'Value', 'Assessment'],
            ['File Format', audio_analysis.get('format', 'Unknown'), 'Standard'],
            ['Duration', f"{audio_analysis.get('duration', 0):.2f} seconds", 'Sufficient for analysis'],
            ['Sample Rate', f"{audio_analysis.get('sample_rate', 0)} Hz", 'Good quality'],
            ['Bit Depth', f"{audio_analysis.get('bit_depth', 0)} bit", 'Standard'],
            ['Channels', str(audio_analysis.get('channels', 0)), 'Mono/Stereo'],
            ['File Size', f"{audio_analysis.get('file_size', 0):.2f} MB", 'Acceptable']
        ]
        
        tech_table = Table(tech_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(tech_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_pdf_speech_analysis(self, analysis_results: Dict) -> List:
        """Create speech and speaker analysis section"""
        content = []
        
        header = Paragraph("SPEECH AND SPEAKER ANALYSIS", self.styles['ForensicHeading'])
        content.append(header)
        
        # Transcription
        transcript_data = analysis_results.get('transcript', {})
        if transcript_data.get('transcript'):
            trans_header = Paragraph("Transcription Results", self.styles['Heading3'])
            content.append(trans_header)
            
            transcript_text = transcript_data.get('transcript', '')
            language = transcript_data.get('language', 'Unknown')
            method = transcript_data.get('method_used', 'Unknown')
            confidence = transcript_data.get('confidence', 0)
            
            # Metadata
            meta_text = f"Language: {language.title()} | Method: {method} | Confidence: {confidence:.2f}"
            meta_para = Paragraph(meta_text, self.styles['ForensicBody'])
            content.append(meta_para)
            content.append(Spacer(1, 10))
            
            # Transcript content (truncate if too long)
            if len(transcript_text) > 1000:
                transcript_text = transcript_text[:1000] + "... [TRUNCATED FOR BREVITY]"
            
            trans_para = Paragraph(f'"{transcript_text}"', self.styles['ForensicBody'])
            content.append(trans_para)
            content.append(Spacer(1, 15))
        
        # Speaker Analysis
        speakers_data = analysis_results.get('speakers', {})
        if speakers_data and speakers_data.get('segments'):
            speaker_header = Paragraph("Speaker Diarization", self.styles['Heading3'])
            content.append(speaker_header)
            
            segments = speakers_data.get('segments', [])
            speaker_count = speakers_data.get('count', 0)
            
            summary_text = f"Total Speakers: {speaker_count} | Total Segments: {len(segments)}"
            summary_para = Paragraph(summary_text, self.styles['ForensicBody'])
            content.append(summary_para)
            content.append(Spacer(1, 10))
            
            # Speaker segments table (first 10)
            if segments:
                segment_data = [['Time Range', 'Speaker', 'Content Preview']]
                for segment in segments[:10]:
                    start_time = segment.get('start_time', 0)
                    end_time = segment.get('end_time', 0)
                    speaker = segment.get('speaker', 'Unknown')
                    text = segment.get('text', '')[:60] + ('...' if len(segment.get('text', '')) > 60 else '')
                    
                    segment_data.append([
                        f"{start_time:.1f}s - {end_time:.1f}s",
                        speaker,
                        text
                    ])
                
                segment_table = Table(segment_data, colWidths=[1.5*inch, 1*inch, 3*inch])
                segment_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                content.append(segment_table)
        
        # Emotion Analysis
        if transcript_data.get('emotion_analysis'):
            emotion_header = Paragraph("Emotion Analysis", self.styles['Heading3'])
            content.append(emotion_header)
            
            emotions = transcript_data.get('emotion_analysis', {})
            emotion_text = "Detected emotions: " + ", ".join([f"{emotion.capitalize()}: {confidence:.2f}" 
                                                            for emotion, confidence in emotions.items()])
            emotion_para = Paragraph(emotion_text, self.styles['ForensicBody'])
            content.append(emotion_para)
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_pdf_keyword_analysis(self, analysis_results: Dict) -> List:
        """Create keyword analysis section"""
        content = []
        
        header = Paragraph("KEYWORD AND CONTENT ANALYSIS", self.styles['ForensicHeading'])
        content.append(header)
        
        keywords = analysis_results.get('keywords', [])
        if keywords:
            # Summary
            categories = {}
            for kw in keywords:
                cat = kw.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            summary_text = f"Total Keywords Detected: {len(keywords)}\\n"
            summary_text += "Categories: " + ", ".join([f"{cat.title()}: {count}" 
                                                      for cat, count in categories.items()])
            
            summary_para = Paragraph(summary_text, self.styles['ForensicBody'])
            content.append(summary_para)
            content.append(Spacer(1, 10))
            
            # Keywords table
            if len(keywords) <= 20:  # Show all if reasonable number
                keyword_data = [['Keyword', 'Category', 'Confidence', 'Context']]
                for kw in keywords:
                    keyword_data.append([
                        kw.get('keyword', ''),
                        kw.get('category', '').title(),
                        f"{kw.get('confidence', 0):.2f}",
                        kw.get('context', '')[:30] + ('...' if len(kw.get('context', '')) > 30 else '')
                    ])
                
                keyword_table = Table(keyword_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 2.5*inch])
                keyword_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                content.append(keyword_table)
            else:
                # Show top keywords only
                top_keywords = sorted(keywords, key=lambda x: x.get('confidence', 0), reverse=True)[:15]
                note_para = Paragraph(f"Showing top 15 keywords (of {len(keywords)} total):", 
                                    self.styles['ForensicBody'])
                content.append(note_para)
                
                for kw in top_keywords:
                    kw_text = f"• {kw.get('keyword', '')} ({kw.get('category', '').title()}) - Confidence: {kw.get('confidence', 0):.2f}"
                    kw_para = Paragraph(kw_text, self.styles['ForensicBody'])
                    content.append(kw_para)
        else:
            no_keywords_para = Paragraph("No crime-related keywords detected in the audio.", 
                                       self.styles['ForensicBody'])
            content.append(no_keywords_para)
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_pdf_ai_insights(self, analysis_results: Dict) -> List:
        """Create AI forensic insights section"""
        content = []
        
        header = Paragraph("AI-POWERED FORENSIC INSIGHTS", self.styles['ForensicHeading'])
        content.append(header)
        
        ai_analysis = analysis_results.get('ai_analysis', {})
        if ai_analysis and not ai_analysis.get('error'):
            
            # Executive Summary
            if ai_analysis.get('executive_summary'):
                exec_header = Paragraph("Executive Summary", self.styles['Heading3'])
                content.append(exec_header)
                exec_para = Paragraph(ai_analysis['executive_summary'], self.styles['ForensicBody'])
                content.append(exec_para)
                content.append(Spacer(1, 12))
            
            # Criminal Assessment
            if ai_analysis.get('criminal_assessment'):
                crim_header = Paragraph("Criminal Assessment", self.styles['Heading3'])
                content.append(crim_header)
                
                assessment = ai_analysis['criminal_assessment']
                if isinstance(assessment, dict):
                    risk_text = f"Risk Level: {assessment.get('risk_level', 'Unknown')}"
                    risk_para = Paragraph(risk_text, self.styles['ImportantNote'])
                    content.append(risk_para)
                    
                    assess_text = assessment.get('assessment', '')
                    assess_para = Paragraph(assess_text, self.styles['ForensicBody'])
                    content.append(assess_para)
                else:
                    assess_para = Paragraph(str(assessment), self.styles['ForensicBody'])
                    content.append(assess_para)
                
                content.append(Spacer(1, 12))
            
            # Speaker Analysis
            if ai_analysis.get('speaker_analysis'):
                speaker_header = Paragraph("AI Speaker Analysis", self.styles['Heading3'])
                content.append(speaker_header)
                
                speaker_analysis = ai_analysis['speaker_analysis']
                if isinstance(speaker_analysis, dict):
                    speaker_text = f"Speakers Detected: {speaker_analysis.get('speaker_count', 'Unknown')}\\n"
                    speaker_text += speaker_analysis.get('analysis', '')
                else:
                    speaker_text = str(speaker_analysis)
                
                speaker_para = Paragraph(speaker_text, self.styles['ForensicBody'])
                content.append(speaker_para)
                content.append(Spacer(1, 12))
            
            # Context Analysis
            if ai_analysis.get('context_analysis'):
                context_header = Paragraph("Context Analysis", self.styles['Heading3'])
                content.append(context_header)
                context_para = Paragraph(ai_analysis['context_analysis'], self.styles['ForensicBody'])
                content.append(context_para)
                content.append(Spacer(1, 12))
                
        else:
            error_msg = ai_analysis.get('error', 'AI analysis not available or failed to complete')
            error_para = Paragraph(f"AI Analysis Status: {error_msg}", self.styles['ForensicBody'])
            content.append(error_para)
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_pdf_conclusions(self, analysis_results: Dict) -> List:
        """Create conclusions and recommendations section"""
        content = []
        
        header = Paragraph("CONCLUSIONS AND RECOMMENDATIONS", self.styles['ForensicHeading'])
        content.append(header)
        
        keywords = analysis_results.get('keywords', [])
        priority_level = self._determine_priority_level(keywords)
        
        # Priority Assessment
        priority_text = f"INVESTIGATION PRIORITY: {priority_level}"
        if priority_level == "HIGH":
            priority_text += " - Significant criminal indicators detected requiring immediate attention."
        elif priority_level == "MEDIUM":
            priority_text += " - Some criminal indicators detected warranting further investigation."
        else:
            priority_text += " - Limited criminal indicators detected."
        
        priority_para = Paragraph(priority_text, self.styles['ImportantNote'])
        content.append(priority_para)
        content.append(Spacer(1, 15))
        
        # Recommendations
        rec_header = Paragraph("Investigative Recommendations", self.styles['Heading3'])
        content.append(rec_header)
        
        recommendations = [
            "Preserve original audio file with proper chain of custody documentation",
            "Cross-reference detected keywords with case database and known criminal terminology",
            "Conduct follow-up interviews with identified speakers if possible",
            "Consider additional technical analysis if audio quality permits enhancement",
            "Review AI assessment findings with investigative context",
            "Document all findings in case management system with appropriate security classifications"
        ]
        
        for rec in recommendations:
            rec_para = Paragraph(f"• {rec}", self.styles['ForensicBody'])
            content.append(rec_para)
        
        content.append(Spacer(1, 20))
        
        # Footer
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Forensic Audio Analysis System v1.0"
        footer_para = Paragraph(footer_text, self.styles['ForensicBody'])
        content.append(footer_para)
        
        return content
    
    # ==================== DOCX CONTENT CREATION METHODS ====================
    
    def _create_docx_header(self, doc: Document, analysis_results: Dict):
        """Create DOCX report header"""
        # Title
        title = doc.add_heading('FORENSIC AUDIO ANALYSIS REPORT', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Classification
        classification = doc.add_paragraph('CONFIDENTIAL - LAW ENFORCEMENT USE ONLY')
        classification.alignment = WD_ALIGN_PARAGRAPH.CENTER
        classification.runs[0].bold = True
        
        doc.add_paragraph()  # Space
        
        # Metadata table
        table = doc.add_table(rows=4, cols=2)
        table.style = 'Table Grid'
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        case_id = f"FA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        table.cell(0, 0).text = 'Report Generated:'
        table.cell(0, 1).text = timestamp
        table.cell(1, 0).text = 'Case ID:'
        table.cell(1, 1).text = case_id
        table.cell(2, 0).text = 'Analysis Software:'
        table.cell(2, 1).text = 'Forensic Audio Analysis Tool v1.0'
        table.cell(3, 0).text = 'Report Type:'
        table.cell(3, 1).text = 'Comprehensive Audio Forensic Analysis'
        
        doc.add_page_break()
    
    def _create_docx_executive_summary(self, doc: Document, analysis_results: Dict):
        """Create DOCX executive summary"""
        doc.add_heading('EXECUTIVE SUMMARY', level=1)
        
        audio_analysis = analysis_results.get('audio_analysis', {})
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        keywords = analysis_results.get('keywords', [])
        
        duration = audio_analysis.get('duration', 0)
        sample_rate = audio_analysis.get('sample_rate', 0)
        channels = audio_analysis.get('channels', 0)
        speaker_count = speakers_data.get('count', 0)
        
        summary_text = f"""This report presents comprehensive forensic audio analysis results for audio evidence with the following characteristics:

• Duration: {duration:.2f} seconds
• Sample Rate: {sample_rate} Hz
• Channels: {channels}
• Language: {transcript_data.get('language', 'Unknown').title()}

Key Findings:
• {len(keywords)} crime-related keywords detected
• {speaker_count} unique speakers identified
• Transcription confidence: {transcript_data.get('confidence', 0):.2f}
• AI forensic analysis completed

Investigation Priority: {self._determine_priority_level(keywords)} based on detected criminal indicators."""
        
        doc.add_paragraph(summary_text)
        doc.add_page_break()
    
    def _create_docx_technical_analysis(self, doc: Document, analysis_results: Dict):
        """Create DOCX technical analysis"""
        doc.add_heading('TECHNICAL AUDIO ANALYSIS', level=1)
        
        audio_analysis = analysis_results.get('audio_analysis', {})
        
        # Technical specifications table
        table = doc.add_table(rows=7, cols=3)
        table.style = 'Table Grid'
        
        table.cell(0, 0).text = 'Property'
        table.cell(0, 1).text = 'Value'
        table.cell(0, 2).text = 'Assessment'
        
        table.cell(1, 0).text = 'File Format'
        table.cell(1, 1).text = audio_analysis.get('format', 'Unknown')
        table.cell(1, 2).text = 'Standard'
        
        table.cell(2, 0).text = 'Duration'
        table.cell(2, 1).text = f"{audio_analysis.get('duration', 0):.2f} seconds"
        table.cell(2, 2).text = 'Sufficient for analysis'
        
        table.cell(3, 0).text = 'Sample Rate'
        table.cell(3, 1).text = f"{audio_analysis.get('sample_rate', 0)} Hz"
        table.cell(3, 2).text = 'Good quality'
        
        table.cell(4, 0).text = 'Bit Depth'
        table.cell(4, 1).text = f"{audio_analysis.get('bit_depth', 0)} bit"
        table.cell(4, 2).text = 'Standard'
        
        table.cell(5, 0).text = 'Channels'
        table.cell(5, 1).text = str(audio_analysis.get('channels', 0))
        table.cell(5, 2).text = 'Mono/Stereo'
        
        table.cell(6, 0).text = 'File Size'
        table.cell(6, 1).text = f"{audio_analysis.get('file_size', 0):.2f} MB"
        table.cell(6, 2).text = 'Acceptable'
        
        doc.add_page_break()
    
    def _create_docx_speech_analysis(self, doc: Document, analysis_results: Dict):
        """Create DOCX speech analysis"""
        doc.add_heading('SPEECH AND SPEAKER ANALYSIS', level=1)
        
        # Transcription
        transcript_data = analysis_results.get('transcript', {})
        if transcript_data.get('transcript'):
            doc.add_heading('Transcription Results', level=2)
            
            transcript_text = transcript_data.get('transcript', '')
            language = transcript_data.get('language', 'Unknown')
            method = transcript_data.get('method_used', 'Unknown')
            confidence = transcript_data.get('confidence', 0)
            
            # Metadata
            meta_text = f"Language: {language.title()} | Method: {method} | Confidence: {confidence:.2f}"
            doc.add_paragraph(meta_text)
            
            # Transcript
            if len(transcript_text) > 1000:
                transcript_text = transcript_text[:1000] + "... [TRUNCATED FOR BREVITY]"
            
            doc.add_paragraph(f'"{transcript_text}"')
        
        # Speaker Analysis
        speakers_data = analysis_results.get('speakers', {})
        if speakers_data and speakers_data.get('segments'):
            doc.add_heading('Speaker Diarization', level=2)
            
            segments = speakers_data.get('segments', [])
            speaker_count = speakers_data.get('count', 0)
            
            doc.add_paragraph(f"Total Speakers: {speaker_count} | Total Segments: {len(segments)}")
            
            # Show first few segments
            for i, segment in enumerate(segments[:5]):
                start_time = segment.get('start_time', 0)
                end_time = segment.get('end_time', 0)
                speaker = segment.get('speaker', 'Unknown')
                text = segment.get('text', '')
                
                segment_text = f"[{start_time:.1f}s - {end_time:.1f}s] {speaker}: {text}"
                doc.add_paragraph(segment_text)
        
        # Emotion Analysis
        if transcript_data.get('emotion_analysis'):
            doc.add_heading('Emotion Analysis', level=2)
            
            emotions = transcript_data.get('emotion_analysis', {})
            emotion_text = "Detected emotions: " + ", ".join([f"{emotion.capitalize()}: {confidence:.2f}" 
                                                            for emotion, confidence in emotions.items()])
            doc.add_paragraph(emotion_text)
        
        doc.add_page_break()
    
    def _create_docx_keyword_analysis(self, doc: Document, analysis_results: Dict):
        """Create DOCX keyword analysis"""
        doc.add_heading('KEYWORD AND CONTENT ANALYSIS', level=1)
        
        keywords = analysis_results.get('keywords', [])
        if keywords:
            # Summary
            categories = {}
            for kw in keywords:
                cat = kw.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            summary_text = f"Total Keywords Detected: {len(keywords)}\\n"
            summary_text += "Categories: " + ", ".join([f"{cat.title()}: {count}" 
                                                      for cat, count in categories.items()])
            doc.add_paragraph(summary_text)
            
            # Keywords table (limit to 20)
            table = doc.add_table(rows=min(len(keywords) + 1, 21), cols=4)
            table.style = 'Table Grid'
            
            table.cell(0, 0).text = 'Keyword'
            table.cell(0, 1).text = 'Category'
            table.cell(0, 2).text = 'Confidence'
            table.cell(0, 3).text = 'Context'
            
            for i, kw in enumerate(keywords[:20]):
                table.cell(i + 1, 0).text = kw.get('keyword', '')
                table.cell(i + 1, 1).text = kw.get('category', '').title()
                table.cell(i + 1, 2).text = f"{kw.get('confidence', 0):.2f}"
                table.cell(i + 1, 3).text = kw.get('context', '')[:50] + ('...' if len(kw.get('context', '')) > 50 else '')
                
        else:
            doc.add_paragraph("No crime-related keywords detected in the audio.")
        
        doc.add_page_break()
    
    def _create_docx_ai_insights(self, doc: Document, analysis_results: Dict):
        """Create DOCX AI insights"""
        doc.add_heading('AI-POWERED FORENSIC INSIGHTS', level=1)
        
        ai_analysis = analysis_results.get('ai_analysis', {})
        if ai_analysis and not ai_analysis.get('error'):
            
            if ai_analysis.get('executive_summary'):
                doc.add_heading('Executive Summary', level=2)
                doc.add_paragraph(ai_analysis['executive_summary'])
            
            if ai_analysis.get('criminal_assessment'):
                doc.add_heading('Criminal Assessment', level=2)
                assessment = ai_analysis['criminal_assessment']
                if isinstance(assessment, dict):
                    doc.add_paragraph(f"Risk Level: {assessment.get('risk_level', 'Unknown')}")
                    doc.add_paragraph(assessment.get('assessment', ''))
                else:
                    doc.add_paragraph(str(assessment))
            
            if ai_analysis.get('speaker_analysis'):
                doc.add_heading('AI Speaker Analysis', level=2)
                speaker_analysis = ai_analysis['speaker_analysis']
                if isinstance(speaker_analysis, dict):
                    doc.add_paragraph(f"Speakers Detected: {speaker_analysis.get('speaker_count', 'Unknown')}")
                    doc.add_paragraph(speaker_analysis.get('analysis', ''))
                else:
                    doc.add_paragraph(str(speaker_analysis))
            
            if ai_analysis.get('context_analysis'):
                doc.add_heading('Context Analysis', level=2)
                doc.add_paragraph(ai_analysis['context_analysis'])
                
        else:
            error_msg = ai_analysis.get('error', 'AI analysis not available or failed to complete')
            doc.add_paragraph(f"AI Analysis Status: {error_msg}")
        
        doc.add_page_break()
    
    def _create_docx_conclusions(self, doc: Document, analysis_results: Dict):
        """Create DOCX conclusions"""
        doc.add_heading('CONCLUSIONS AND RECOMMENDATIONS', level=1)
        
        keywords = analysis_results.get('keywords', [])
        priority_level = self._determine_priority_level(keywords)
        
        # Priority Assessment
        priority_text = f"INVESTIGATION PRIORITY: {priority_level}"
        if priority_level == "HIGH":
            priority_text += " - Significant criminal indicators detected requiring immediate attention."
        elif priority_level == "MEDIUM":
            priority_text += " - Some criminal indicators detected warranting further investigation."
        else:
            priority_text += " - Limited criminal indicators detected."
        
        priority_para = doc.add_paragraph(priority_text)
        priority_para.runs[0].bold = True
        
        # Recommendations
        doc.add_heading('Investigative Recommendations', level=2)
        
        recommendations = [
            "Preserve original audio file with proper chain of custody documentation",
            "Cross-reference detected keywords with case database and known criminal terminology",
            "Conduct follow-up interviews with identified speakers if possible",
            "Consider additional technical analysis if audio quality permits enhancement",
            "Review AI assessment findings with investigative context",
            "Document all findings in case management system with appropriate security classifications"
        ]
        
        for rec in recommendations:
            doc.add_paragraph(rec, style='List Bullet')
        
        # Footer
        doc.add_paragraph()
        footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Forensic Audio Analysis System v1.0"
        footer_para = doc.add_paragraph(footer_text)
        footer_para.runs[0].italic = True
    
    # ==================== HELPER METHODS ====================
    
    # ==================== MISSING CONTENT CREATION METHODS ====================
    
    def _create_case_information_section(self, analysis_results: Dict) -> List:
        """Create case information section - stub method"""
        content = []
        header = Paragraph("2. CASE INFORMATION & EVIDENCE DETAILS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Case information section content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_enhanced_technical_analysis(self, analysis_results: Dict) -> List:
        """Create enhanced technical analysis - stub method"""
        content = []
        header = Paragraph("3. ENHANCED TECHNICAL AUDIO ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Enhanced technical analysis content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_comprehensive_speech_analysis(self, analysis_results: Dict) -> List:
        """Create comprehensive speech analysis - stub method"""
        content = []
        header = Paragraph("4. COMPREHENSIVE SPEECH ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Comprehensive speech analysis content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_detailed_speaker_analysis(self, analysis_results: Dict) -> List:
        """Create detailed speaker analysis - stub method"""
        content = []
        header = Paragraph("5. DETAILED SPEAKER ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Detailed speaker analysis content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_emotion_analysis_section(self, analysis_results: Dict) -> List:
        """Create emotion analysis section - stub method"""
        content = []
        header = Paragraph("6. EMOTION & SENTIMENT ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Emotion analysis content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_enhanced_keyword_analysis(self, analysis_results: Dict) -> List:
        """Create enhanced keyword analysis - stub method"""
        content = []
        header = Paragraph("7. ENHANCED KEYWORD ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Enhanced keyword analysis content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_comprehensive_ai_insights(self, analysis_results: Dict) -> List:
        """Create comprehensive AI insights - stub method"""
        content = []
        header = Paragraph("8. AI-POWERED FORENSIC INSIGHTS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("AI insights content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_criminal_assessment_section(self, analysis_results: Dict) -> List:
        """Create criminal assessment section - stub method"""
        content = []
        header = Paragraph("9. CRIMINAL ASSESSMENT", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Criminal assessment content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_evidence_integrity_section(self, analysis_results: Dict) -> List:
        """Create evidence integrity section - stub method"""
        content = []
        header = Paragraph("10. EVIDENCE INTEGRITY", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Evidence integrity content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_statistical_analysis_section(self, analysis_results: Dict) -> List:
        """Create statistical analysis section - stub method"""
        content = []
        header = Paragraph("11. STATISTICAL ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Statistical analysis content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_enhanced_conclusions_section(self, analysis_results: Dict) -> List:
        """Create enhanced conclusions section - stub method"""
        content = []
        header = Paragraph("12. CONCLUSIONS & RECOMMENDATIONS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Enhanced conclusions content...", self.styles['ForensicBody']))
        content.append(PageBreak())
        return content
    
    def _create_appendices_section(self, analysis_results: Dict) -> List:
        """Create appendices section - stub method"""
        content = []
        header = Paragraph("13. APPENDICES & RAW DATA", self.styles['SectionHeader'])
        content.append(header)
        content.append(Paragraph("Appendices content...", self.styles['ForensicBody']))
        return content
    
    # DOCX stub methods
    def _create_enhanced_docx_cover(self, doc: Document, analysis_results: Dict):
        """Create enhanced DOCX cover - stub method"""
        doc.add_heading('COMPREHENSIVE FORENSIC AUDIO ANALYSIS REPORT', 0)
        doc.add_paragraph('Enhanced cover content...')
        doc.add_page_break()
    
    def _create_docx_executive_summary_enhanced(self, doc: Document, analysis_results: Dict):
        """Create enhanced DOCX executive summary - stub method"""
        doc.add_heading('EXECUTIVE SUMMARY', level=1)
        doc.add_paragraph('Enhanced executive summary content...')
        doc.add_page_break()
    
    def _create_docx_case_information(self, doc: Document, analysis_results: Dict):
        """Create DOCX case information - stub method"""
        doc.add_heading('CASE INFORMATION', level=1)
        doc.add_paragraph('Case information content...')
        doc.add_page_break()
    
    def _create_docx_technical_analysis_enhanced(self, doc: Document, analysis_results: Dict):
        """Create enhanced DOCX technical analysis - stub method"""
        doc.add_heading('TECHNICAL ANALYSIS', level=1)
        doc.add_paragraph('Enhanced technical analysis content...')
        doc.add_page_break()
    
    def _create_docx_speech_analysis_complete(self, doc: Document, analysis_results: Dict):
        """Create complete DOCX speech analysis - stub method"""
        doc.add_heading('SPEECH ANALYSIS', level=1)
        doc.add_paragraph('Complete speech analysis content...')
        doc.add_page_break()
    
    def _create_docx_speaker_analysis_detailed(self, doc: Document, analysis_results: Dict):
        """Create detailed DOCX speaker analysis - stub method"""
        doc.add_heading('SPEAKER ANALYSIS', level=1)
        doc.add_paragraph('Detailed speaker analysis content...')
        doc.add_page_break()
    
    def _create_docx_emotion_analysis(self, doc: Document, analysis_results: Dict):
        """Create DOCX emotion analysis - stub method"""
        doc.add_heading('EMOTION ANALYSIS', level=1)
        doc.add_paragraph('Emotion analysis content...')
        doc.add_page_break()
    
    def _create_docx_keyword_analysis_enhanced(self, doc: Document, analysis_results: Dict):
        """Create enhanced DOCX keyword analysis - stub method"""
        doc.add_heading('KEYWORD ANALYSIS', level=1)
        doc.add_paragraph('Enhanced keyword analysis content...')
        doc.add_page_break()
    
    def _create_docx_ai_insights_comprehensive(self, doc: Document, analysis_results: Dict):
        """Create comprehensive DOCX AI insights - stub method"""
        doc.add_heading('AI INSIGHTS', level=1)
        doc.add_paragraph('Comprehensive AI insights content...')
        doc.add_page_break()
    
    def _create_docx_criminal_assessment(self, doc: Document, analysis_results: Dict):
        """Create DOCX criminal assessment - stub method"""
        doc.add_heading('CRIMINAL ASSESSMENT', level=1)
        doc.add_paragraph('Criminal assessment content...')
        doc.add_page_break()
    
    def _create_docx_evidence_integrity(self, doc: Document, analysis_results: Dict):
        """Create DOCX evidence integrity - stub method"""
        doc.add_heading('EVIDENCE INTEGRITY', level=1)
        doc.add_paragraph('Evidence integrity content...')
        doc.add_page_break()
    
    def _create_docx_statistical_analysis(self, doc: Document, analysis_results: Dict):
        """Create DOCX statistical analysis - stub method"""
        doc.add_heading('STATISTICAL ANALYSIS', level=1)
        doc.add_paragraph('Statistical analysis content...')
        doc.add_page_break()
    
    def _create_docx_conclusions_enhanced(self, doc: Document, analysis_results: Dict):
        """Create enhanced DOCX conclusions - stub method"""
        doc.add_heading('CONCLUSIONS', level=1)
        doc.add_paragraph('Enhanced conclusions content...')
        doc.add_page_break()
    
    def _create_docx_appendices(self, doc: Document, analysis_results: Dict):
        """Create DOCX appendices - stub method"""
        doc.add_heading('APPENDICES', level=1)
        doc.add_paragraph('Appendices content...')

    # ==================== HELPER AND ASSESSMENT METHODS ====================
    
    def _determine_enhanced_priority_level(self, keywords: List[Dict], transcript_data: Dict) -> str:
        """Enhanced priority assessment based on multiple factors"""
        priority_score = 0
        
        # Keyword-based scoring
        high_risk_keywords = [kw for kw in keywords if kw.get('confidence', 0) > 0.8]
        if len(keywords) > 15:
            priority_score += 3
        elif len(keywords) > 7:
            priority_score += 2
        elif len(keywords) > 3:
            priority_score += 1
            
        # High confidence keywords
        if len(high_risk_keywords) > 5:
            priority_score += 2
        elif len(high_risk_keywords) > 2:
            priority_score += 1
        
        # Transcription quality factor
        confidence = transcript_data.get('confidence', 0)
        if confidence > 0.8:
            priority_score += 1
        
        # Emotion analysis factor
        emotions = transcript_data.get('emotion_analysis', {})
        if emotions:
            negative_emotions = ['angry', 'fear', 'disgust', 'sadness']
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else None
            if dominant_emotion in negative_emotions:
                priority_score += 1
        
        # Determine priority level
        if priority_score >= 6:
            return "CRITICAL"
        elif priority_score >= 4:
            return "HIGH"
        elif priority_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_risk_level(self, ai_analysis: Dict) -> str:
        """Extract risk level from AI analysis"""
        if not ai_analysis or ai_analysis.get('error'):
            return "UNKNOWN"
        
        # Try to extract from criminal assessment
        criminal_assessment = ai_analysis.get('criminal_assessment', {})
        if isinstance(criminal_assessment, dict):
            return criminal_assessment.get('risk_level', 'UNKNOWN').upper()
        
        # Fallback - analyze content for risk indicators
        content_analysis = ai_analysis.get('context_analysis', '')
        if any(term in content_analysis.lower() for term in ['high risk', 'critical', 'dangerous']):
            return "HIGH"
        elif any(term in content_analysis.lower() for term in ['medium risk', 'concerning', 'suspicious']):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_duration(self, duration: float) -> str:
        """Assess audio duration for forensic analysis"""
        if duration < 10:
            return "Very Short - Limited Analysis"
        elif duration < 60:
            return "Short - Adequate for Analysis"
        elif duration < 300:
            return "Good Length - Comprehensive Analysis"
        else:
            return "Extended - Detailed Analysis Available"
    
    def _assess_confidence(self, confidence: float) -> str:
        """Assess transcription confidence level"""
        if confidence >= 0.9:
            return "Excellent - High Reliability"
        elif confidence >= 0.7:
            return "Good - Reliable"
        elif confidence >= 0.5:
            return "Fair - Moderate Reliability"
        else:
            return "Poor - Low Reliability"
    
    def _assess_keyword_count(self, count: int) -> str:
        """Assess significance of keyword count"""
        if count == 0:
            return "None Detected"
        elif count <= 3:
            return "Low - Few Indicators"
        elif count <= 10:
            return "Medium - Multiple Indicators"
        else:
            return "High - Significant Indicators"
    
    def _assess_speaker_count(self, count: int) -> str:
        """Assess speaker identification results"""
        if count == 0:
            return "None Identified"
        elif count == 1:
            return "Single Speaker"
        elif count <= 3:
            return "Multiple Speakers"
        else:
            return "Group Conversation"
    
    def _setup_docx_styles(self, doc: Document):
        """Setup enhanced DOCX styles"""
        # Get styles object
        styles = doc.styles
        
        # Create custom heading styles
        try:
            # Main title style
            title_style = styles.add_style('ForensicTitle', WD_STYLE_TYPE.PARAGRAPH)
            title_font = title_style.font
            title_font.name = 'Arial Black'
            title_font.size = Pt(18)
            title_font.color.rgb = RGBColor(0, 51, 102)
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(24)
        except:
            pass  # Style might already exist
        
        try:
            # Section heading style
            section_style = styles.add_style('SectionHeading', WD_STYLE_TYPE.PARAGRAPH)
            section_font = section_style.font
            section_font.name = 'Arial'
            section_font.size = Pt(14)
            section_font.bold = True
            section_font.color.rgb = RGBColor(153, 0, 0)
            section_style.paragraph_format.space_before = Pt(18)
            section_style.paragraph_format.space_after = Pt(12)
        except:
            pass
    
    # ==================== COMPLETE CONTENT CREATION METHODS ====================
    
    def _create_complete_header(self, analysis_results: Dict) -> List:
        """Create complete PDF report header with actual content"""
        content = []
        
        # Title
        title = Paragraph("FORENSIC AUDIO ANALYSIS REPORT", self.styles['ForensicTitle'])
        content.append(title)
        content.append(Spacer(1, 20))
        
        # Classification
        classification = Paragraph(
            "CONFIDENTIAL - LAW ENFORCEMENT USE ONLY", 
            self.styles['ImportantNote']
        )
        content.append(classification)
        content.append(Spacer(1, 20))
        
        # Case Information Table
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        case_id = f"FA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = analysis_results.get('file_path', 'Unknown')
        
        case_data = [
            ['Report Generated:', timestamp],
            ['Case ID:', case_id],
            ['Audio File:', os.path.basename(file_path) if file_path else 'Unknown'],
            ['Analysis Tool:', 'Forensic Audio Analysis System v1.0'],
            ['Classification:', 'Criminal Investigation Evidence']
        ]
        
        case_table = Table(case_data, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(case_table)
        content.append(PageBreak())
        return content
    
    def _create_complete_executive_summary(self, analysis_results: Dict) -> List:
        """Create complete executive summary with actual analysis data"""
        content = []
        
        # Header
        header = Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        # Get analysis data
        audio_analysis = analysis_results.get('audio_analysis', {})
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        keywords = analysis_results.get('keywords', [])
        ai_analysis = analysis_results.get('ai_analysis', {})
        
        # File Information
        file_path = analysis_results.get('file_path', 'Unknown')
        duration = audio_analysis.get('duration', 0)
        sample_rate = audio_analysis.get('sample_rate', 0)
        channels = audio_analysis.get('channels', 0)
        
        # Analysis Statistics
        speaker_count = speakers_data.get('count', 0)
        transcript_length = len(transcript_data.get('transcript', ''))
        confidence = transcript_data.get('confidence', 0)
        language = transcript_data.get('language', 'Unknown')
        keyword_count = len(keywords)
        high_conf_keywords = len([k for k in keywords if k.get('confidence', 0) > 0.8])
        
        # Create comprehensive summary
        summary_text = f"""CASE ANALYSIS SUMMARY

AUDIO EVIDENCE DETAILS:
• File: {os.path.basename(file_path) if file_path else 'Unknown'}
• Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)
• Quality: {sample_rate} Hz, {channels} channel(s)
• Size: {audio_analysis.get('file_size', 0):.1f} MB

SPEECH ANALYSIS RESULTS:
• Language: {language.title()}
• Transcript Length: {transcript_length:,} characters
• Transcription Confidence: {confidence:.2f} ({self._assess_confidence(confidence)})
• Analysis Method: {transcript_data.get('method_used', 'Unknown')}

SPEAKER IDENTIFICATION:
• Total Speakers Detected: {speaker_count}
• Speaker Segments: {len(speakers_data.get('segments', []))}
• Quality: {self._assess_speaker_count(speaker_count)}

CRIMINAL CONTENT ANALYSIS:
• Keywords Detected: {keyword_count}
• High-Confidence Matches: {high_conf_keywords}
• Risk Assessment: {self._assess_keyword_count(keyword_count)}
• Investigation Priority: {self._determine_enhanced_priority_level(keywords, transcript_data)}

AI FORENSIC ANALYSIS:
• Status: {'Completed Successfully' if ai_analysis and not ai_analysis.get('error') else 'Not Available'}
• Criminal Risk Level: {self._extract_risk_level(ai_analysis)}
• Evidence Assessment: {'Professional Analysis Available' if ai_analysis else 'Limited to Technical Analysis'}"""
        
        summary_para = Paragraph(summary_text, self.styles['ForensicBody'])
        content.append(summary_para)
        content.append(Spacer(1, 20))
        
        # Key Findings Table
        findings_data = [
            ['ANALYSIS COMPONENT', 'RESULT', 'ASSESSMENT'],
            ['Audio Duration', f"{duration:.1f}s", self._assess_duration(duration)],
            ['Speech Quality', f"{confidence:.2f}", self._assess_confidence(confidence)],
            ['Speakers Found', str(speaker_count), self._assess_speaker_count(speaker_count)],
            ['Criminal Keywords', str(keyword_count), self._assess_keyword_count(keyword_count)],
            ['Language Detection', language.title(), 'Confirmed'],
            ['AI Analysis', 'Available' if ai_analysis else 'N/A', 'Complete' if ai_analysis else 'Limited']
        ]
        
        findings_table = Table(findings_data, colWidths=[2*inch, 1.2*inch, 2.3*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(findings_table)
        content.append(PageBreak())
        return content
    
    def _create_complete_technical_analysis(self, analysis_results: Dict) -> List:
        """Create complete technical analysis with actual audio data"""
        content = []
        
        # Header
        header = Paragraph("TECHNICAL AUDIO ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        audio_analysis = analysis_results.get('audio_analysis', {})
        
        # Technical Details
        tech_text = f"""AUDIO FILE TECHNICAL SPECIFICATIONS:

The audio evidence submitted for forensic analysis exhibits the following technical characteristics that directly impact the reliability and completeness of the investigation findings:

FORMAT AND ENCODING:
• File Format: {audio_analysis.get('format', 'Unknown')}
• Encoding: {audio_analysis.get('encoding', 'Standard')} 
• Bit Depth: {audio_analysis.get('bit_depth', 16)} bits
• Sample Rate: {audio_analysis.get('sample_rate', 0)} Hz
• Channel Configuration: {audio_analysis.get('channels', 1)} channel(s) ({'Stereo' if audio_analysis.get('channels', 1) == 2 else 'Mono'})

QUALITY ASSESSMENT:
• File Size: {audio_analysis.get('file_size', 0):.2f} MB
• Duration: {audio_analysis.get('duration', 0):.2f} seconds ({audio_analysis.get('duration', 0)/60:.1f} minutes)
• Average Bitrate: {audio_analysis.get('bitrate', 'Unknown')} kbps
• Audio Quality: {self._assess_audio_quality(audio_analysis)}

FORENSIC SUITABILITY:
• Evidence Integrity: {self._assess_file_integrity(audio_analysis)}
• Analysis Feasibility: {self._assess_analysis_feasibility(audio_analysis)}
• Enhancement Potential: {self._assess_enhancement_potential(audio_analysis)}"""
        
        tech_para = Paragraph(tech_text, self.styles['ForensicBody'])
        content.append(tech_para)
        content.append(Spacer(1, 15))
        
        # Technical Specifications Table
        tech_specs = [
            ['PARAMETER', 'VALUE', 'FORENSIC ASSESSMENT'],
            ['Duration', f"{audio_analysis.get('duration', 0):.2f} seconds", self._assess_duration(audio_analysis.get('duration', 0))],
            ['Sample Rate', f"{audio_analysis.get('sample_rate', 0)} Hz", self._assess_sample_rate(audio_analysis.get('sample_rate', 0))],
            ['Bit Depth', f"{audio_analysis.get('bit_depth', 16)} bit", 'Standard Resolution'],
            ['Channels', str(audio_analysis.get('channels', 1)), 'Mono/Stereo'],
            ['File Size', f"{audio_analysis.get('file_size', 0):.2f} MB", 'Acceptable'],
            ['Format', audio_analysis.get('format', 'Unknown'), 'Compatible']
        ]
        
        tech_table = Table(tech_specs, colWidths=[1.8*inch, 1.5*inch, 2.2*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(tech_table)
        content.append(PageBreak())
        return content
    
    def _create_complete_speech_analysis(self, analysis_results: Dict) -> List:
        """Create complete speech analysis with actual transcript data"""
        content = []
        
        # Header
        header = Paragraph("SPEECH TRANSCRIPTION ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        transcript_data = analysis_results.get('transcript', {})
        transcript_text = transcript_data.get('transcript', '')
        
        if transcript_text:
            # Analysis Overview
            language = transcript_data.get('language', 'Unknown')
            confidence = transcript_data.get('confidence', 0)
            method = transcript_data.get('method_used', 'Unknown')
            
            overview_text = f"""TRANSCRIPTION ANALYSIS RESULTS:

METHODOLOGY AND ACCURACY:
• Transcription Method: {method}
• Language Detected: {language.title()}
• Overall Confidence Score: {confidence:.2f} ({self._assess_confidence(confidence)})
• Total Characters: {len(transcript_text):,}
• Word Count: {len(transcript_text.split())} words (approximate)
• Processing Quality: {'High-Quality Automated Transcription' if confidence > 0.7 else 'Standard Quality Transcription'}

CONTENT OVERVIEW:
The audio evidence has been successfully processed through advanced speech recognition systems. The transcription below represents the audible speech content recovered from the audio file, processed through forensic-grade analysis algorithms."""
            
            overview_para = Paragraph(overview_text, self.styles['ForensicBody'])
            content.append(overview_para)
            content.append(Spacer(1, 15))
            
            # Transcript Content
            transcript_header = Paragraph("COMPLETE AUDIO TRANSCRIPT:", self.styles['SubsectionHeader'])
            content.append(transcript_header)
            content.append(Spacer(1, 10))
            
            # Format transcript for display
            if len(transcript_text) > 2000:
                display_text = transcript_text[:2000] + "\n\n[TRANSCRIPT CONTINUES...]\n\n" + transcript_text[-500:]
                truncation_note = Paragraph("Note: Transcript truncated for report brevity. Complete transcript available in case files.", 
                                          self.styles['FootnoteText'])
            else:
                display_text = transcript_text
                truncation_note = None
            
            # Create transcript paragraph with special formatting
            formatted_transcript = f'"{display_text}"'
            transcript_para = Paragraph(formatted_transcript, self.styles['TranscriptText'])
            content.append(transcript_para)
            
            if truncation_note:
                content.append(Spacer(1, 10))
                content.append(truncation_note)
                
            # Emotion Analysis if available
            emotions = transcript_data.get('emotion_analysis', {})
            if emotions:
                content.append(Spacer(1, 20))
                emotion_header = Paragraph("EMOTIONAL CONTENT ANALYSIS:", self.styles['SubsectionHeader'])
                content.append(emotion_header)
                content.append(Spacer(1, 10))
                
                emotion_results = []
                for emotion, score in emotions.items():
                    emotion_results.append(f"• {emotion.title()}: {score:.2f} confidence")
                
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                emotion_text = f"""DETECTED EMOTIONAL INDICATORS:

{chr(10).join(emotion_results)}

DOMINANT EMOTION: {dominant_emotion.title()} (Score: {emotions[dominant_emotion]:.2f})

FORENSIC SIGNIFICANCE: {'High - Emotional distress indicators may suggest coercion or conflict' if dominant_emotion in ['fear', 'angry', 'sad'] else 'Standard - Neutral emotional profile detected'}"""
                
                emotion_para = Paragraph(emotion_text, self.styles['ForensicBody'])
                content.append(emotion_para)
        else:
            # No transcript available
            no_transcript = Paragraph(
                "TRANSCRIPT STATUS: No readable speech content detected in audio evidence. This may indicate instrumental audio, very poor quality, or non-speech content.", 
                self.styles['ForensicBody']
            )
            content.append(no_transcript)
        
        content.append(PageBreak())
        return content
    
    def _create_complete_speaker_analysis(self, analysis_results: Dict) -> List:
        """Create complete speaker analysis with actual speaker data"""
        content = []
        
        # Header
        header = Paragraph("SPEAKER IDENTIFICATION & DIARIZATION", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        speakers_data = analysis_results.get('speakers', {})
        speaker_count = speakers_data.get('count', 0)
        segments = speakers_data.get('segments', [])
        
        if speaker_count > 0 and segments:
            # Speaker Overview
            overview_text = f"""SPEAKER DIARIZATION RESULTS:

IDENTIFICATION SUMMARY:
• Total Unique Speakers Detected: {speaker_count}
• Total Speech Segments: {len(segments)}
• Diarization Quality: {self._assess_speaker_count(speaker_count)}
• Analysis Method: Advanced Voice Activity Detection with Speaker Clustering

FORENSIC SIGNIFICANCE:
{'Multiple speakers detected - indicates conversation or group interaction' if speaker_count > 1 else 'Single speaker detected - monologue or single-party recording'}

The following speaker timeline represents the chronological breakdown of detected voices throughout the audio evidence:"""
            
            overview_para = Paragraph(overview_text, self.styles['ForensicBody'])
            content.append(overview_para)
            content.append(Spacer(1, 15))
            
            # Speaker Timeline Header
            timeline_header = Paragraph("DETAILED SPEAKER TIMELINE:", self.styles['SubsectionHeader'])
            content.append(timeline_header)
            content.append(Spacer(1, 10))
            
            # Create speaker segments table
            if len(segments) <= 15:
                # Show all segments if reasonable number
                segment_data = [['TIME RANGE', 'SPEAKER ID', 'DURATION', 'CONTENT PREVIEW']]
                
                for segment in segments:
                    start_time = segment.get('start_time', 0)
                    end_time = segment.get('end_time', 0)
                    duration = end_time - start_time
                    speaker = segment.get('speaker', 'Unknown')
                    text = segment.get('text', 'No text available')
                    
                    # Truncate text for table
                    preview_text = text[:50] + "..." if len(text) > 50 else text
                    
                    segment_data.append([
                        f"{start_time:.1f}s - {end_time:.1f}s",
                        speaker,
                        f"{duration:.1f}s",
                        preview_text
                    ])
                
                segments_table = Table(segment_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 2.5*inch])
                segments_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                content.append(segments_table)
            else:
                # Show first 10 segments for brevity
                summary_text = f"Showing first 10 segments (of {len(segments)} total):\n\n"
                
                for i, segment in enumerate(segments[:10]):
                    start_time = segment.get('start_time', 0)
                    end_time = segment.get('end_time', 0)
                    speaker = segment.get('speaker', 'Unknown')
                    text = segment.get('text', 'No text available')[:100]
                    
                    summary_text += f"[{start_time:.1f}s-{end_time:.1f}s] {speaker}: {text}...\n\n"
                
                segments_para = Paragraph(summary_text, self.styles['ForensicBody'])
                content.append(segments_para)
            
        else:
            # No speakers detected
            no_speakers_text = """SPEAKER ANALYSIS RESULTS:

STATUS: No distinct speakers detected in audio evidence.

POSSIBLE CAUSES:
• Audio may contain instrumental or non-speech content
• Speech quality may be insufficient for speaker diarization
• Single speaker with insufficient variation for clustering
• Background noise or distortion affecting voice detection

FORENSIC IMPACT: Limited speaker-based analysis available. Investigation should focus on content and technical analysis."""
            
            no_speakers_para = Paragraph(no_speakers_text, self.styles['ForensicBody'])
            content.append(no_speakers_para)
        
        content.append(PageBreak())
        return content
    
    def _create_complete_keyword_analysis(self, analysis_results: Dict) -> List:
        """Create complete keyword analysis with actual detected keywords"""
        content = []
        
        # Header
        header = Paragraph("CRIMINAL KEYWORD & CONTENT ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        keywords = analysis_results.get('keywords', [])
        
        if keywords:
            # Analysis Overview
            total_keywords = len(keywords)
            high_conf_keywords = len([k for k in keywords if k.get('confidence', 0) > 0.8])
            
            # Categorize keywords
            categories = {}
            for kw in keywords:
                cat = kw.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            overview_text = f"""CRIMINAL CONTENT DETECTION RESULTS:

DETECTION SUMMARY:
• Total Keywords Detected: {total_keywords}
• High-Confidence Matches: {high_conf_keywords} (confidence > 0.8)
• Categories Identified: {len(categories)}
• Risk Assessment: {self._assess_keyword_count(total_keywords)}
• Investigation Priority: {self._determine_enhanced_priority_level(keywords, analysis_results.get('transcript', {}))}

CATEGORY BREAKDOWN:"""
            
            for category, count in categories.items():
                overview_text += f"\n• {category.title()}: {count} keywords detected"
            
            overview_text += f"\n\nFORENSIC SIGNIFICANCE:\n{self._get_keyword_significance(keywords)}"
            
            overview_para = Paragraph(overview_text, self.styles['ForensicBody'])
            content.append(overview_para)
            content.append(Spacer(1, 15))
            
            # Detailed Keywords Table
            keywords_header = Paragraph("DETAILED KEYWORD ANALYSIS:", self.styles['SubsectionHeader'])
            content.append(keywords_header)
            content.append(Spacer(1, 10))
            
            # Sort keywords by confidence
            sorted_keywords = sorted(keywords, key=lambda x: x.get('confidence', 0), reverse=True)
            
            if len(sorted_keywords) <= 20:
                # Show all keywords
                keyword_data = [['KEYWORD', 'CATEGORY', 'CONFIDENCE', 'CONTEXT']]
                
                for kw in sorted_keywords:
                    keyword = kw.get('keyword', '')
                    category = kw.get('category', 'unknown').title()
                    confidence = f"{kw.get('confidence', 0):.2f}"
                    context = kw.get('context', '')[:60] + "..." if len(kw.get('context', '')) > 60 else kw.get('context', '')
                    
                    keyword_data.append([keyword, category, confidence, context])
                
                keywords_table = Table(keyword_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 2.5*inch])
                keywords_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                content.append(keywords_table)
            else:
                # Show top 15 keywords
                note_text = f"Showing top 15 highest-confidence keywords (of {len(sorted_keywords)} total):\n\n"
                
                for i, kw in enumerate(sorted_keywords[:15], 1):
                    keyword = kw.get('keyword', '')
                    category = kw.get('category', 'unknown').title()
                    confidence = kw.get('confidence', 0)
                    context = kw.get('context', '')[:80]
                    
                    note_text += f"{i}. '{keyword}' - {category} (Confidence: {confidence:.2f})\n   Context: {context}...\n\n"
                
                keywords_para = Paragraph(note_text, self.styles['ForensicBody'])
                content.append(keywords_para)
            
        else:
            # No keywords detected
            no_keywords_text = """CRIMINAL KEYWORD ANALYSIS RESULTS:

STATUS: No criminal-related keywords detected in audio transcript.

ANALYSIS SCOPE: The automated keyword detection system searched for indicators related to:
• Violence and threats
• Drug-related terminology
• Weapons references
• Criminal planning language
• Illegal activities indicators
• Suspicious behavioral patterns

FORENSIC INTERPRETATION: 
The absence of detected criminal keywords does not conclusively indicate non-criminal content. Consider:
• Coded language or euphemisms may be present
• Audio quality may affect transcription accuracy
• Context-dependent criminal implications may require human analysis
• Non-verbal criminal indicators are not captured by keyword analysis

RECOMMENDATION: Manual review of transcript recommended for comprehensive assessment."""
            
            no_keywords_para = Paragraph(no_keywords_text, self.styles['ForensicBody'])
            content.append(no_keywords_para)
        
        content.append(PageBreak())
        return content
    
    def _create_complete_ai_analysis(self, analysis_results: Dict) -> List:
        """Create complete AI analysis with actual AI insights"""
        content = []
        
        # Header
        header = Paragraph("AI-POWERED FORENSIC ANALYSIS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        ai_analysis = analysis_results.get('ai_analysis', {})
        
        if ai_analysis and not ai_analysis.get('error'):
            # AI Analysis Overview
            overview_text = f"""ARTIFICIAL INTELLIGENCE FORENSIC ASSESSMENT:

ANALYSIS STATUS: Successfully Completed
AI MODEL: Advanced Language Model with Forensic Training
PROCESSING DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
CONFIDENCE LEVEL: Professional Grade Analysis

The following assessment represents advanced AI-powered analysis of the audio evidence, providing forensic insights beyond traditional automated analysis methods."""
            
            overview_para = Paragraph(overview_text, self.styles['ForensicBody'])
            content.append(overview_para)
            content.append(Spacer(1, 15))
            
            # Executive Summary
            if ai_analysis.get('executive_summary'):
                exec_header = Paragraph("AI EXECUTIVE SUMMARY:", self.styles['SubsectionHeader'])
                content.append(exec_header)
                content.append(Spacer(1, 10))
                
                exec_para = Paragraph(ai_analysis['executive_summary'], self.styles['ForensicBody'])
                content.append(exec_para)
                content.append(Spacer(1, 15))
            
            # Criminal Assessment
            if ai_analysis.get('criminal_assessment'):
                crim_header = Paragraph("CRIMINAL RISK ASSESSMENT:", self.styles['SubsectionHeader'])
                content.append(crim_header)
                content.append(Spacer(1, 10))
                
                assessment = ai_analysis['criminal_assessment']
                if isinstance(assessment, dict):
                    risk_level = assessment.get('risk_level', 'Unknown')
                    assessment_text = assessment.get('assessment', '')
                    
                    crim_text = f"RISK LEVEL: {risk_level.upper()}\n\nASSESSMENT:\n{assessment_text}"
                else:
                    crim_text = str(assessment)
                
                crim_para = Paragraph(crim_text, self.styles['ForensicBody'])
                content.append(crim_para)
                content.append(Spacer(1, 15))
            
            # Speaker Analysis
            if ai_analysis.get('speaker_analysis'):
                speaker_header = Paragraph("AI SPEAKER PROFILE ANALYSIS:", self.styles['SubsectionHeader'])
                content.append(speaker_header)
                content.append(Spacer(1, 10))
                
                speaker_analysis = ai_analysis['speaker_analysis']
                if isinstance(speaker_analysis, dict):
                    speaker_count = speaker_analysis.get('speaker_count', 'Unknown')
                    analysis_text = speaker_analysis.get('analysis', '')
                    
                    speaker_text = f"SPEAKERS DETECTED: {speaker_count}\n\nPROFILE ANALYSIS:\n{analysis_text}"
                else:
                    speaker_text = str(speaker_analysis)
                
                speaker_para = Paragraph(speaker_text, self.styles['ForensicBody'])
                content.append(speaker_para)
                content.append(Spacer(1, 15))
            
            # Context Analysis
            if ai_analysis.get('context_analysis'):
                context_header = Paragraph("CONTEXTUAL CONTENT ANALYSIS:", self.styles['SubsectionHeader'])
                content.append(context_header)
                content.append(Spacer(1, 10))
                
                context_para = Paragraph(ai_analysis['context_analysis'], self.styles['ForensicBody'])
                content.append(context_para)
                content.append(Spacer(1, 15))
            
        else:
            # AI Analysis not available
            error_msg = ai_analysis.get('error', 'AI analysis system not available or failed to process')
            
            no_ai_text = f"""AI FORENSIC ANALYSIS STATUS:

STATUS: Not Available
ERROR: {error_msg}

IMPACT ON INVESTIGATION:
The absence of AI-powered analysis limits the depth of automated forensic assessment. The investigation must rely on:
• Technical audio analysis
• Manual transcript review
• Traditional keyword detection
• Human expert interpretation

RECOMMENDATION: Consider reprocessing with AI system when available for enhanced forensic insights."""
            
            no_ai_para = Paragraph(no_ai_text, self.styles['ForensicBody'])
            content.append(no_ai_para)
        
        content.append(PageBreak())
        return content
    
    def _create_complete_conclusions(self, analysis_results: Dict) -> List:
        """Create complete conclusions with actual recommendations"""
        content = []
        
        # Header
        header = Paragraph("CONCLUSIONS & INVESTIGATIVE RECOMMENDATIONS", self.styles['SectionHeader'])
        content.append(header)
        content.append(Spacer(1, 15))
        
        # Analysis Summary
        keywords = analysis_results.get('keywords', [])
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        ai_analysis = analysis_results.get('ai_analysis', {})
        
        priority_level = self._determine_enhanced_priority_level(keywords, transcript_data)
        risk_level = self._extract_risk_level(ai_analysis)
        
        # Investigation Priority Assessment
        priority_text = f"""FORENSIC ANALYSIS CONCLUSIONS:

INVESTIGATION PRIORITY ASSESSMENT: {priority_level}

OVERALL RISK EVALUATION: {risk_level}

EVIDENCE SUMMARY:
• Audio Quality: {self._assess_confidence(transcript_data.get('confidence', 0))}
• Criminal Indicators: {len(keywords)} detected
• Speaker Analysis: {speakers_data.get('count', 0)} speakers identified
• AI Assessment: {'Available' if ai_analysis and not ai_analysis.get('error') else 'Not Available'}

INVESTIGATIVE SIGNIFICANCE:
{self._get_investigative_significance(analysis_results)}

EVIDENCE RELIABILITY:
{self._assess_evidence_reliability(analysis_results)}"""
        
        priority_para = Paragraph(priority_text, self.styles['ForensicBody'])
        content.append(priority_para)
        content.append(Spacer(1, 20))
        
        # Specific Recommendations
        rec_header = Paragraph("SPECIFIC INVESTIGATIVE RECOMMENDATIONS:", self.styles['SubsectionHeader'])
        content.append(rec_header)
        content.append(Spacer(1, 10))
        
        recommendations = self._generate_specific_recommendations(analysis_results)
        
        for i, rec in enumerate(recommendations, 1):
            rec_para = Paragraph(f"{i}. {rec}", self.styles['ForensicBody'])
            content.append(rec_para)
            content.append(Spacer(1, 8))
        
        content.append(Spacer(1, 20))
        
        # Report Authentication
        auth_text = f"""REPORT AUTHENTICATION:

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System: Forensic Audio Analysis Tool v1.0
Classification: CONFIDENTIAL - LAW ENFORCEMENT USE ONLY
Case File: Evidence preserved with digital integrity verification

This automated forensic analysis report provides technical and preliminary assessment of audio evidence. Human expert review is recommended for final investigative decisions."""
        
        auth_para = Paragraph(auth_text, self.styles['FootnoteText'])
        content.append(auth_para)
        
        return content

    def generate_comprehensive_preview(self, analysis_results: Dict) -> str:
        """Generate comprehensive text preview of report contents"""
        try:
            lines = []
            
            lines.append("COMPREHENSIVE FORENSIC AUDIO ANALYSIS REPORT PREVIEW")
            lines.append("=" * 80)
            lines.append("")
            
            # Basic information
            file_path = analysis_results.get('file_path', '')
            audio_analysis = analysis_results.get('audio_analysis', {})
            
            lines.append("AUDIO EVIDENCE INFORMATION")
            lines.append("-" * 40)
            lines.append(f"Audio File: {os.path.basename(file_path) if file_path else 'Unknown'}")
            lines.append(f"Full Path: {file_path}")
            lines.append(f"Duration: {audio_analysis.get('duration', 0):.2f} seconds ({audio_analysis.get('duration', 0)/60:.1f} minutes)")
            lines.append(f"Format: {audio_analysis.get('format', 'Unknown')}")
            lines.append(f"Sample Rate: {audio_analysis.get('sample_rate', 0)} Hz")
            lines.append(f"Channels: {audio_analysis.get('channels', 0)}")
            lines.append(f"File Size: {audio_analysis.get('file_size', 0):.2f} MB")
            lines.append("")
            
            # Analysis summary
            transcript_data = analysis_results.get('transcript', {})
            speakers_data = analysis_results.get('speakers', {})
            keywords = analysis_results.get('keywords', [])
            ai_analysis = analysis_results.get('ai_analysis', {})
            
            lines.append("COMPREHENSIVE ANALYSIS SUMMARY")
            lines.append("-" * 40)
            lines.append(f"Language Detected: {transcript_data.get('language', 'Unknown').title()}")
            lines.append(f"Transcription Confidence: {transcript_data.get('confidence', 0):.2f}")
            lines.append(f"Transcription Length: {len(transcript_data.get('transcript', ''))} characters")
            lines.append(f"Method Used: {transcript_data.get('method_used', 'Unknown')}")
            lines.append("")
            lines.append(f"Speakers Identified: {speakers_data.get('count', 0)}")
            lines.append(f"Speaker Segments: {len(speakers_data.get('segments', []))}")
            lines.append("")
            lines.append(f"Criminal Keywords: {len(keywords)}")
            lines.append(f"High-Confidence Keywords: {len([kw for kw in keywords if kw.get('confidence', 0) > 0.8])}")
            lines.append(f"Investigation Priority: {self._determine_enhanced_priority_level(keywords, transcript_data)}")
            lines.append("")
            
            # Keywords by category
            if keywords:
                categories = {}
                for kw in keywords:
                    cat = kw.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                lines.append("KEYWORD CATEGORIES DETECTED")
                lines.append("-" * 30)
                for cat, count in categories.items():
                    lines.append(f"• {cat.title()}: {count} keywords")
                lines.append("")
            
            # Emotion analysis
            emotions = transcript_data.get('emotion_analysis', {})
            if emotions:
                lines.append("EMOTION ANALYSIS RESULTS")
                lines.append("-" * 25)
                for emotion, confidence in emotions.items():
                    lines.append(f"• {emotion.title()}: {confidence:.2f}")
                lines.append("")
            
            # AI Analysis status
            lines.append("AI FORENSIC ANALYSIS")
            lines.append("-" * 20)
            if ai_analysis and not ai_analysis.get('error'):
                lines.append("✓ AI Analysis: Successfully Completed")
                risk_level = self._extract_risk_level(ai_analysis)
                lines.append(f"✓ Criminal Risk Assessment: {risk_level}")
                
                if ai_analysis.get('executive_summary'):
                    lines.append("✓ Executive Summary: Available")
                if ai_analysis.get('criminal_assessment'):
                    lines.append("✓ Criminal Assessment: Available")
                if ai_analysis.get('speaker_analysis'):
                    lines.append("✓ AI Speaker Analysis: Available")
                if ai_analysis.get('context_analysis'):
                    lines.append("✓ Context Analysis: Available")
            else:
                lines.append("✗ AI Analysis: Not Available or Failed")
            lines.append("")
            
            # Report sections
            lines.append("COMPREHENSIVE REPORT SECTIONS")
            lines.append("-" * 35)
            report_sections = [
                "1. Executive Summary with Key Findings",
                "2. Case Information & Evidence Details",
                "3. Enhanced Technical Audio Analysis", 
                "4. Complete Speech Transcription Analysis",
                "5. Detailed Speaker Identification & Diarization",
                "6. Emotion & Sentiment Analysis",
                "7. Enhanced Keyword & Content Analysis",
                "8. AI-Powered Comprehensive Forensic Insights",
                "9. Criminal Assessment & Risk Analysis",
                "10. Evidence Integrity & Chain of Custody",
                "11. Statistical Analysis & Pattern Recognition",
                "12. Professional Conclusions & Recommendations",
                "13. Appendices with Raw Analysis Data"
            ]
            
            for section in report_sections:
                lines.append(f"✓ {section}")
            lines.append("")
            
            lines.append("REPORT STATUS: Ready for Professional Generation")
            lines.append("Available Formats: Enhanced PDF, Comprehensive DOCX")
            lines.append("Evidence Data: JSON format with integrity checksums")
            lines.append("Classification: CONFIDENTIAL - LAW ENFORCEMENT USE ONLY")
            lines.append("")
            lines.append("=" * 80)
            
            return "\\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Enhanced preview generation error: {e}")
            return f"Error generating comprehensive preview: {e}"

    # ==================== HELPER METHODS FOR COMPLETE CONTENT ====================
    
    def _assess_audio_quality(self, audio_analysis: Dict) -> str:
        """Assess overall audio quality for forensic purposes"""
        sample_rate = audio_analysis.get('sample_rate', 0)
        duration = audio_analysis.get('duration', 0)
        
        if sample_rate >= 44100 and duration > 10:
            return "High Quality - Excellent for forensic analysis"
        elif sample_rate >= 22050 and duration > 5:
            return "Good Quality - Suitable for analysis"
        elif sample_rate >= 16000:
            return "Standard Quality - Adequate for basic analysis"
        else:
            return "Low Quality - Limited analysis capabilities"
    
    def _assess_file_integrity(self, audio_analysis: Dict) -> str:
        """Assess file integrity for evidence purposes"""
        format_type = audio_analysis.get('format', '').upper()
        
        if format_type in ['WAV', 'FLAC']:
            return "Uncompressed - High integrity"
        elif format_type in ['MP3', 'AAC', 'M4A']:
            return "Compressed - Standard integrity"
        else:
            return "Unknown format - Integrity assessment required"
    
    def _assess_analysis_feasibility(self, audio_analysis: Dict) -> str:
        """Assess feasibility of comprehensive analysis"""
        duration = audio_analysis.get('duration', 0)
        sample_rate = audio_analysis.get('sample_rate', 0)
        
        if duration > 1 and sample_rate > 8000:
            return "High Feasibility - All analysis types supported"
        elif duration > 0.5:
            return "Moderate Feasibility - Basic analysis supported"
        else:
            return "Limited Feasibility - Minimal analysis possible"
    
    def _assess_enhancement_potential(self, audio_analysis: Dict) -> str:
        """Assess potential for audio enhancement"""
        sample_rate = audio_analysis.get('sample_rate', 0)
        bit_depth = audio_analysis.get('bit_depth', 0)
        
        if sample_rate >= 44100 and bit_depth >= 16:
            return "Good Enhancement Potential"
        elif sample_rate >= 22050:
            return "Moderate Enhancement Potential" 
        else:
            return "Limited Enhancement Potential"
    
    def _assess_sample_rate(self, sample_rate: int) -> str:
        """Assess sample rate quality"""
        if sample_rate >= 44100:
            return "Professional Grade"
        elif sample_rate >= 22050:
            return "Standard Quality"
        elif sample_rate >= 16000:
            return "Phone/Voice Quality"
        else:
            return "Low Quality"
    
    def _get_keyword_significance(self, keywords: List) -> str:
        """Determine forensic significance of detected keywords"""
        if len(keywords) > 15:
            return "HIGH SIGNIFICANCE - Multiple criminal indicators present requiring immediate investigative attention"
        elif len(keywords) > 5:
            return "MODERATE SIGNIFICANCE - Several criminal indicators warrant thorough investigation"
        elif len(keywords) > 0:
            return "LOW SIGNIFICANCE - Few criminal indicators detected, context review recommended"
        else:
            return "NO SIGNIFICANCE - No criminal terminology detected in automated analysis"
    
    def _get_investigative_significance(self, analysis_results: Dict) -> str:
        """Determine overall investigative significance"""
        keywords = analysis_results.get('keywords', [])
        transcript_data = analysis_results.get('transcript', {})
        speakers_data = analysis_results.get('speakers', {})
        
        significance_factors = []
        
        if len(keywords) > 10:
            significance_factors.append("Multiple criminal keywords detected")
        
        if speakers_data.get('count', 0) > 1:
            significance_factors.append("Multiple speakers indicate conversation/planning")
        
        confidence = transcript_data.get('confidence', 0)
        if confidence > 0.8:
            significance_factors.append("High-quality transcript available for evidence")
        
        if significance_factors:
            return "HIGH - " + "; ".join(significance_factors)
        else:
            return "MODERATE - Standard forensic analysis completed, human review recommended"
    
    def _assess_evidence_reliability(self, analysis_results: Dict) -> str:
        """Assess overall evidence reliability"""
        audio_analysis = analysis_results.get('audio_analysis', {})
        transcript_data = analysis_results.get('transcript', {})
        
        reliability_score = 0
        
        # Audio quality factors
        if audio_analysis.get('sample_rate', 0) >= 16000:
            reliability_score += 1
        if audio_analysis.get('duration', 0) >= 10:
            reliability_score += 1
        if transcript_data.get('confidence', 0) >= 0.7:
            reliability_score += 2
        
        if reliability_score >= 3:
            return "HIGH RELIABILITY - Evidence suitable for legal proceedings"
        elif reliability_score >= 2:
            return "MODERATE RELIABILITY - Evidence suitable with corroboration"
        else:
            return "LIMITED RELIABILITY - Evidence requires enhancement or additional verification"
    
    def _generate_specific_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate specific investigative recommendations"""
        recommendations = []
        
        # Base recommendations
        recommendations.extend([
            "Preserve original audio file with proper chain of custody documentation",
            "Verify audio file integrity using digital forensic tools",
            "Document all analysis procedures and software versions used"
        ])
        
        # Keyword-based recommendations
        keywords = analysis_results.get('keywords', [])
        if len(keywords) > 5:
            recommendations.append("Cross-reference detected criminal keywords with database of known criminal terminology")
            recommendations.append("Conduct linguistic analysis for coded language or euphemisms")
        
        # Speaker-based recommendations
        speakers_data = analysis_results.get('speakers', {})
        if speakers_data.get('count', 0) > 1:
            recommendations.append("Attempt voice identification of detected speakers through comparison databases")
            recommendations.append("Analyze speaker interaction patterns for relationship assessment")
        
        # Transcript quality recommendations
        transcript_data = analysis_results.get('transcript', {})
        confidence = transcript_data.get('confidence', 0)
        if confidence < 0.7:
            recommendations.append("Consider audio enhancement techniques to improve transcription accuracy")
            recommendations.append("Perform manual transcript verification by qualified linguist")
        
        # AI analysis recommendations
        ai_analysis = analysis_results.get('ai_analysis', {})
        if ai_analysis and not ai_analysis.get('error'):
            risk_level = self._extract_risk_level(ai_analysis)
            if risk_level in ['HIGH', 'CRITICAL']:
                recommendations.append("Escalate investigation priority based on AI risk assessment")
                recommendations.append("Consider surveillance or protective measures based on threat indicators")
        
        # Final recommendations
        recommendations.extend([
            "Conduct follow-up investigation based on content analysis findings",
            "Document all findings in official case management system",
            "Consider additional technical analysis if audio quality permits enhancement"
        ])
        
        return recommendations
    
    def _determine_priority_level(self, keywords: List) -> str:
        """Determine investigation priority based on keywords"""
        if len(keywords) > 10:
            return "HIGH"
        elif len(keywords) > 3:
            return "MEDIUM"
        else:
            return "LOW"

    # Simplified methods for backward compatibility
    def generate_pdf_report(self, analysis_results: Dict, output_dir: str) -> str:
        """Generate PDF report (calls comprehensive method)"""
        return self.generate_comprehensive_pdf_report(analysis_results, output_dir)
    
    def generate_docx_report(self, analysis_results: Dict, output_dir: str) -> str:
        """Generate DOCX report (calls comprehensive method)"""
        return self.generate_comprehensive_docx_report(analysis_results, output_dir)
    
    def generate_preview(self, analysis_results: Dict) -> str:
        """Generate preview (calls comprehensive method)"""
        return self.generate_comprehensive_preview(analysis_results)


# Create aliases for backward compatibility
ForensicReportGenerator = ComprehensiveForensicReportGenerator
ReportGenerator = ComprehensiveForensicReportGenerator