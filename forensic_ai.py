"""
Enhanced Forensic AI Module - ChatGPT API integration for comprehensive forensic analysis
"""

import openai
import json
import logging
from datetime import datetime
import os
from pathlib import Path
import time
import re
from typing import Dict, List, Optional, Tuple


class ForensicAI:
    """Enhanced AI-powered forensic analysis using ChatGPT API with retry logic and comprehensive analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.max_retries = 3
        self.retry_delay = 2
        self.setup_openai()
        
        # Enhanced analysis templates
        self.analysis_prompts = {
            'forensic_summary': self.get_forensic_summary_prompt(),
            'speaker_analysis': self.get_speaker_analysis_prompt(),
            'crime_analysis': self.get_crime_analysis_prompt(),
            'investigation_recommendations': self.get_investigation_prompt(),
            'criminal_intent_analysis': self.get_criminal_intent_prompt(),
            'context_analysis': self.get_context_analysis_prompt()
        }
        
        # Multi-language crime keywords
        self.crime_keywords = {
            'english': ['murder', 'kill', 'death', 'weapon', 'gun', 'knife', 'bomb', 'attack', 'threat', 
                       'kidnap', 'ransom', 'smuggling', 'drugs', 'cocaine', 'heroin', 'trafficking', 
                       'bribe', 'corruption', 'fraud', 'steal', 'robbery', 'burglary', 'assault', 
                       'violence', 'revenge', 'blackmail', 'extortion', 'conspiracy', 'plot'],
            'hindi': ['हत्या', 'मारना', 'मृत्यु', 'हथियार', 'बंदूक', 'छुरी', 'बम', 'हमला', 'धमकी', 
                     'अपहरण', 'फिरौती', 'तस्करी', 'नशा', 'ड्रग्स', 'रिश्वत', 'भ्रष्टाचार', 'धोखाधड़ी', 
                     'चोरी', 'डकैती', 'हमला', 'हिंसा', 'बदला', 'ब्लैकमेल', 'जबरन वसूली', 'साजिश'],
            'gujarati': ['હત્યા', 'મારવું', 'મૃત્યુ', 'હથિયાર', 'બંદૂક', 'છરી', 'બોમ્બ', 'હુમલો', 'ધમકી', 
                        'અપહરણ', 'ખંડણી', 'દાણચોરી', 'નશો', 'ડ્રગ્સ', 'લાંચ', 'ભ્રષ્ટાચાર', 'છેતરપિંડી', 
                        'ચોરી', 'લૂંટ', 'હુમલો', 'હિંસા', 'બદલો', 'બ્લેકમેલ', 'જબરજસ્તી', 'ષડયંત્ર']
        }
    
    def setup_openai(self):
        """Setup OpenAI client with enhanced error handling"""
        try:
            # Try to get API key from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                # Try to load from config file
                config_path = Path('config.json')
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        api_key = config.get('openai_api_key')
            
            if api_key and api_key.startswith('sk-'):
                self.client = openai.OpenAI(api_key=api_key)
                # Test the API key
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Test"}],
                        max_tokens=1
                    )
                    self.logger.info("OpenAI client initialized and tested successfully")
                except Exception as test_error:
                    self.logger.error(f"OpenAI API key test failed: {test_error}")
                    self.client = None
            else:
                self.logger.warning("Valid OpenAI API key not found. AI features will be limited.")
                self.client = None
                
        except Exception as e:
            self.logger.error(f"OpenAI setup error: {e}")
            self.client = None
    
    def call_openai_with_retry(self, messages: List[Dict], model: str = "gpt-3.5-turbo", max_tokens: int = 1000) -> Optional[str]:
        """Call OpenAI API with retry logic and error handling"""
        if not self.client:
            self.logger.warning("OpenAI client not available")
            return None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                
                if response.choices and response.choices[0].message:
                    return response.choices[0].message.content.strip()
                else:
                    self.logger.warning("Empty response from OpenAI API")
                    return None
                    
            except openai.RateLimitError as e:
                self.logger.warning(f"Rate limit exceeded (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    
            except openai.APIError as e:
                self.logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                self.logger.error(f"Unexpected error calling OpenAI (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        self.logger.error("Failed to get response from OpenAI after all retries")
        return None
    
    def generate_comprehensive_analysis(self, results: Dict) -> Dict:
        """Generate comprehensive forensic analysis from all available data"""
        try:
            if not self.client:
                return self.generate_fallback_comprehensive_analysis(results)
            
            # Extract key information
            transcript = results.get('transcript', {}).get('transcript', '')
            keywords = results.get('keywords', [])
            language = results.get('transcript', {}).get('language', 'english')
            
            # Perform comprehensive analysis
            analysis = {}
            
            # Executive summary
            if transcript:
                analysis['executive_summary'] = self.generate_executive_summary(transcript, keywords, language)
            
            # Speaker analysis
            if results.get('speakers'):
                analysis['speaker_analysis'] = self.analyze_speakers_comprehensive(results['speakers'], transcript)
            
            # Criminal content assessment  
            if keywords:
                analysis['criminal_assessment'] = self.assess_criminal_content_comprehensive(keywords, transcript, language)
            
            # Investigation recommendations
            analysis['recommendations'] = self.generate_investigation_recommendations(results)
            
            # Risk assessment
            analysis['risk_assessment'] = self.generate_risk_assessment(keywords, transcript)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis error: {e}")
            return self.generate_fallback_comprehensive_analysis(results)
    
    def generate_executive_summary(self, transcript: str, keywords: List[Dict], language: str) -> str:
        """Generate executive forensic summary"""
        if not transcript:
            return "No transcript available for analysis."
        
        try:
            keyword_summary = self.summarize_keywords(keywords)
            
            messages = [
                {"role": "system", "content": """You are a forensic audio analyst providing executive summaries for law enforcement. 
                Provide clear, professional analysis focusing on criminal indicators, threat levels, and investigative priorities."""},
                {"role": "user", "content": f"""
                Analyze this audio transcript and provide an executive forensic summary:
                
                TRANSCRIPT: {transcript[:2000]}...
                LANGUAGE: {language}
                CRIME KEYWORDS DETECTED: {keyword_summary}
                
                Provide:
                1. Executive summary (2-3 sentences)
                2. Key criminal indicators
                3. Threat level assessment
                4. Immediate concerns
                5. Investigation priority level
                """}
            ]
            
            response = self.call_openai_with_retry(messages, max_tokens=800)
            return response if response else "Unable to generate executive summary."
            
        except Exception as e:
            self.logger.error(f"Executive summary generation error: {e}")
            return "Executive summary generation failed."
    
    def analyze_speakers_comprehensive(self, speakers: Dict, transcript: str) -> Dict:
        """Comprehensive speaker analysis"""
        try:
            speaker_count = speakers.get('count', 1)
            segments = speakers.get('segments', [])
            
            if speaker_count <= 1:
                return {"analysis": "Single speaker detected. Limited diarization analysis available."}
            
            messages = [
                {"role": "system", "content": """You are a forensic analyst specializing in speaker behavior and conversation dynamics.
                Analyze speaker patterns, dominance, aggression, and interaction for investigative purposes."""},
                {"role": "user", "content": f"""
                Analyze this multi-speaker conversation:
                
                SPEAKER COUNT: {speaker_count}
                CONVERSATION SEGMENTS: {json.dumps(segments[:10], indent=2)}  # First 10 segments
                
                Provide analysis on:
                1. Speaker dominance patterns
                2. Emotional state indicators  
                3. Conversation dynamics
                4. Suspicious interaction patterns
                5. Potential relationship between speakers
                """}
            ]
            
            response = self.call_openai_with_retry(messages, max_tokens=600)
            
            return {
                "speaker_count": speaker_count,
                "analysis": response if response else "Speaker analysis unavailable",
                "dominant_speaker": self.identify_dominant_speaker(segments),
                "interaction_pattern": self.analyze_interaction_pattern(segments)
            }
            
        except Exception as e:
            self.logger.error(f"Speaker analysis error: {e}")
            return {"error": str(e)}
    
    def assess_criminal_content_comprehensive(self, keywords: List[Dict], transcript: str, language: str) -> Dict:
        """Comprehensive criminal content assessment"""
        try:
            if not keywords:
                return {"assessment": "No criminal keywords detected.", "risk_level": "LOW"}
            
            # Categorize keywords by severity
            critical_keywords = [kw for kw in keywords if kw.get('severity') == 'CRITICAL']
            high_keywords = [kw for kw in keywords if kw.get('severity') == 'HIGH']
            
            keyword_contexts = [kw['context'] for kw in keywords[:10]]  # Top 10 contexts
            
            messages = [
                {"role": "system", "content": """You are a criminal forensic analyst. Assess criminal content objectively, 
                focusing on actual criminal intent, threats, and actionable intelligence for law enforcement."""},
                {"role": "user", "content": f"""
                Assess the criminal content in this audio transcript:
                
                CRITICAL KEYWORDS: {len(critical_keywords)}
                HIGH-RISK KEYWORDS: {len(high_keywords)}
                TOTAL KEYWORDS: {len(keywords)}
                LANGUAGE: {language}
                
                KEY CONTEXTS:
                {json.dumps(keyword_contexts, indent=2, ensure_ascii=False)}
                
                Provide:
                1. Criminal intent likelihood (0-100%)
                2. Specific criminal activities indicated
                3. Threat assessment
                4. Evidence quality rating
                5. Legal considerations
                """}
            ]
            
            response = self.call_openai_with_retry(messages, max_tokens=800)
            
            # Calculate risk score
            risk_score = min((len(critical_keywords) * 30) + (len(high_keywords) * 15) + (len(keywords) * 5), 100)
            risk_level = "CRITICAL" if risk_score >= 80 else "HIGH" if risk_score >= 60 else "MEDIUM" if risk_score >= 30 else "LOW"
            
            return {
                "assessment": response if response else "Criminal assessment unavailable",
                "risk_score": risk_score,
                "risk_level": risk_level,
                "critical_indicators": len(critical_keywords),
                "high_risk_indicators": len(high_keywords),
                "total_indicators": len(keywords)
            }
            
        except Exception as e:
            self.logger.error(f"Criminal assessment error: {e}")
            return {"error": str(e)}
    
    def generate_fallback_comprehensive_analysis(self, results: Dict) -> Dict:
        """Generate fallback analysis when AI is not available"""
        keywords = results.get('keywords', [])
        transcript = results.get('transcript', {}).get('transcript', '')
        
        # Basic statistical analysis
        critical_count = sum(1 for kw in keywords if kw.get('severity') == 'CRITICAL')
        high_count = sum(1 for kw in keywords if kw.get('severity') == 'HIGH')
        
        risk_score = min((critical_count * 30) + (high_count * 20), 100)
        risk_level = "CRITICAL" if risk_score >= 70 else "HIGH" if risk_score >= 50 else "MEDIUM" if risk_score >= 25 else "LOW"
        
        return {
            "executive_summary": f"Audio analysis completed with {len(keywords)} criminal indicators detected. Risk level: {risk_level}",
            "criminal_assessment": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "critical_indicators": critical_count,
                "total_indicators": len(keywords)
            },
            "recommendations": self.get_basic_recommendations(risk_level),
            "note": "Advanced AI analysis unavailable - basic analysis provided"
        }
    
    def get_basic_recommendations(self, risk_level: str) -> str:
        """Get basic recommendations based on risk level"""
        recommendations = {
            "CRITICAL": "IMMEDIATE ACTION: High probability of criminal activity. Recommend emergency response and immediate investigation.",
            "HIGH": "URGENT: Significant criminal indicators. Immediate investigation and monitoring recommended.", 
            "MEDIUM": "ATTENTION REQUIRED: Suspicious activity detected. Investigation and further analysis recommended.",
            "LOW": "ROUTINE: Limited criminal indicators. Standard documentation and monitoring sufficient."
        }
        return recommendations.get(risk_level, "No specific recommendation available.")
    
    def test_api_connection(self):
        """Test OpenAI API connection"""
        try:
            if not self.client:
                return False, "OpenAI client not initialized"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Test connection - please respond with 'OK'"}
                ],
                max_tokens=10
            )
            
            return True, "API connection successful"
            
        except Exception as e:
            return False, f"API connection failed: {e}"
    
    def save_insights_to_file(self, insights, output_path):
        """Save generated insights to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)
            
            self.logger.info(f"Insights saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving insights: {e}")
    
    def configure_api_key(self, api_key):
        """Configure OpenAI API key"""
        try:
            if api_key and api_key.startswith('sk-'):
                self.client = openai.OpenAI(api_key=api_key)
                self.logger.info("API key configured successfully")
                return True
            else:
                self.logger.error("Invalid API key format")
                return False
        except Exception as e:
            self.logger.error(f"API key configuration error: {e}")
            return False
    
    def generate_insights(self, analysis_results):
        """Generate comprehensive forensic insights from analysis results"""
        try:
            if not self.client:
                return self.generate_fallback_insights(analysis_results)
            
            # Prepare data for AI analysis
            forensic_data = self.prepare_forensic_data(analysis_results)
            
            insights = {}
            
            # Generate different types of insights
            insights['summary'] = self.generate_forensic_summary(forensic_data)
            insights['speaker_analysis'] = self.analyze_speakers(forensic_data)
            insights['crime_assessment'] = self.assess_criminal_content(forensic_data)
            insights['recommendations'] = self.generate_recommendations(forensic_data)
            
            # Combine all insights
            combined_insights = self.combine_insights(insights)
            
            return combined_insights
            
        except Exception as e:
            self.logger.error(f"AI insights generation error: {e}")
            return self.generate_fallback_insights(analysis_results)
    
    def prepare_forensic_data(self, analysis_results):
        """Prepare analysis results for AI processing"""
        try:
            forensic_data = {
                'timestamp': datetime.now().isoformat(),
                'metadata': analysis_results.get('metadata', {}),
                'transcription': analysis_results.get('transcription', ''),
                'speakers': analysis_results.get('speaker_diarization', []),
                'keywords': analysis_results.get('keywords', []),
                'context_analysis': analysis_results.get('crime_context', {}),
                'emotion_analysis': analysis_results.get('emotion_analysis', {}),
                'anomalies': analysis_results.get('anomalies', []),
                'noise_analysis': analysis_results.get('noise_analysis', {})
            }
            
            return forensic_data
            
        except Exception as e:
            self.logger.error(f"Data preparation error: {e}")
            return {}
    
    def generate_forensic_summary(self, forensic_data):
        """Generate overall forensic summary using AI"""
        try:
            prompt = self.analysis_prompts['forensic_summary'].format(
                transcription=forensic_data.get('transcription', ''),
                keywords=json.dumps(forensic_data.get('keywords', []), indent=2),
                speakers=json.dumps(forensic_data.get('speakers', []), indent=2),
                duration=forensic_data.get('metadata', {}).get('duration', 0),
                anomalies=json.dumps(forensic_data.get('anomalies', []), indent=2)
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a forensic audio analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Forensic summary generation error: {e}")
            return "AI forensic summary generation failed"
    
    def analyze_speakers(self, forensic_data):
        """Analyze speaker characteristics and roles"""
        try:
            speakers_info = forensic_data.get('speakers', [])
            if not speakers_info:
                return "No speaker information available for analysis"
            
            prompt = self.analysis_prompts['speaker_analysis'].format(
                speakers=json.dumps(speakers_info, indent=2),
                emotion_data=json.dumps(forensic_data.get('emotion_analysis', {}), indent=2)
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a forensic speaker analysis specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Speaker analysis error: {e}")
            return "Speaker analysis failed"
    
    def assess_criminal_content(self, forensic_data):
        """Assess criminal content and intent"""
        try:
            keywords = forensic_data.get('keywords', [])
            transcription = forensic_data.get('transcription', '')
            context = forensic_data.get('context_analysis', {})
            
            prompt = self.analysis_prompts['crime_analysis'].format(
                transcription=transcription,
                keywords=json.dumps(keywords, indent=2),
                context_analysis=json.dumps(context, indent=2)
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a forensic criminal content analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Crime assessment error: {e}")
            return "Criminal content assessment failed"
    
    def generate_recommendations(self, forensic_data):
        """Generate investigation recommendations"""
        try:
            prompt = self.analysis_prompts['investigation_recommendations'].format(
                all_data=json.dumps(forensic_data, indent=2, default=str)
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a forensic investigation consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Recommendations generation error: {e}")
            return "Investigation recommendations generation failed"
    
    def combine_insights(self, insights):
        """Combine all insights into a comprehensive report"""
        try:
            combined = []
            
            combined.append("🔍 FORENSIC AI ANALYSIS REPORT")
            combined.append("=" * 50)
            combined.append("")
            combined.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            combined.append("")
            
            # Summary
            combined.append("📋 EXECUTIVE SUMMARY")
            combined.append("-" * 25)
            combined.append(insights.get('summary', 'No summary available'))
            combined.append("")
            
            # Speaker Analysis
            combined.append("👥 SPEAKER ANALYSIS")
            combined.append("-" * 20)
            combined.append(insights.get('speaker_analysis', 'No speaker analysis available'))
            combined.append("")
            
            # Criminal Content Assessment
            combined.append("⚠️  CRIMINAL CONTENT ASSESSMENT")
            combined.append("-" * 35)
            combined.append(insights.get('crime_assessment', 'No crime assessment available'))
            combined.append("")
            
            # Recommendations
            combined.append("📝 INVESTIGATION RECOMMENDATIONS")
            combined.append("-" * 35)
            combined.append(insights.get('recommendations', 'No recommendations available'))
            combined.append("")
            
            combined.append("=" * 50)
            combined.append("End of AI Analysis Report")
            
            return "\\n".join(combined)
            
        except Exception as e:
            self.logger.error(f"Insights combination error: {e}")
            return "Failed to combine AI insights"
    
    def generate_fallback_insights(self, analysis_results):
        """Generate insights without AI when API is not available"""
        try:
            insights = []
            
            insights.append("🔍 FORENSIC ANALYSIS REPORT (Local Analysis)")
            insights.append("=" * 50)
            insights.append("")
            
            # Basic summary
            metadata = analysis_results.get('metadata', {})
            insights.append("📋 BASIC SUMMARY")
            insights.append("-" * 15)
            insights.append(f"File Duration: {metadata.get('duration', 0):.2f} seconds")
            insights.append(f"Audio Quality: {metadata.get('sample_rate', 0)} Hz")
            
            # Keyword summary
            keywords = analysis_results.get('keywords', [])
            if keywords:
                insights.append(f"Keywords Detected: {len(keywords)} crime-related terms found")
                categories = set(kw.get('category', 'unknown') for kw in keywords)
                insights.append(f"Crime Categories: {', '.join(categories)}")
            else:
                insights.append("Keywords Detected: No crime-related keywords found")
            insights.append("")
            
            # Speaker summary
            speakers = analysis_results.get('speaker_diarization', [])
            if speakers:
                unique_speakers = set(s.get('speaker', 'Unknown') for s in speakers)
                insights.append("👥 SPEAKER INFORMATION")
                insights.append("-" * 20)
                insights.append(f"Speakers Detected: {len(unique_speakers)}")
                for speaker in unique_speakers:
                    segments = [s for s in speakers if s.get('speaker') == speaker]
                    total_time = sum(s.get('end', 0) - s.get('start', 0) for s in segments)
                    insights.append(f"• {speaker}: {total_time:.1f} seconds of speech")
            else:
                insights.append("👥 SPEAKER INFORMATION")
                insights.append("-" * 20)
                insights.append("Speaker separation not available")
            insights.append("")
            
            # Anomaly summary
            anomalies = analysis_results.get('anomalies', [])
            if anomalies:
                insights.append("⚠️  ANOMALIES DETECTED")
                insights.append("-" * 20)
                for anomaly in anomalies:
                    insights.append(f"• {anomaly.get('type', 'Unknown')}: {anomaly.get('confidence', 0):.2f} confidence")
            else:
                insights.append("⚠️  ANOMALIES DETECTED")
                insights.append("-" * 20)
                insights.append("No significant anomalies detected")
            insights.append("")
            
            # Basic recommendations
            insights.append("📝 RECOMMENDATIONS")
            insights.append("-" * 15)
            
            if keywords:
                insights.append("• High Priority: Crime-related keywords detected - immediate review recommended")
                insights.append("• Preserve original audio file as evidence")
                insights.append("• Consider professional forensic analysis")
            else:
                insights.append("• Low Priority: No obvious criminal indicators")
                insights.append("• Archive for future reference")
            
            if anomalies:
                insights.append("• Technical Analysis: Audio anomalies detected - verify authenticity")
            
            insights.append("")
            insights.append("Note: This is a basic analysis. For detailed AI insights, configure OpenAI API key.")
            insights.append("=" * 50)
            
            return "\\n".join(insights)
            
        except Exception as e:
            self.logger.error(f"Fallback insights error: {e}")
            return "Analysis report generation failed"
    
    def get_forensic_summary_prompt(self):
        """Get prompt template for forensic summary"""
        return '''
        As a forensic audio analysis expert, analyze the following audio evidence and provide a comprehensive summary:

        Audio Transcription:
        {transcription}

        Detected Keywords:
        {keywords}

        Speaker Information:
        {speakers}

        Audio Duration: {duration} seconds

        Detected Anomalies:
        {anomalies}

        Please provide:
        1. A brief overview of the audio content
        2. Assessment of potential criminal activity
        3. Key findings and their significance
        4. Overall threat assessment (Low/Medium/High)
        5. Notable patterns or behaviors

        Focus on forensic relevance and investigative value.
        '''
    
    def get_speaker_analysis_prompt(self):
        """Get prompt template for speaker analysis"""
        return '''
        As a forensic speaker analysis specialist, analyze the following speaker data:

        Speaker Diarization Data:
        {speakers}

        Emotion Analysis Data:
        {emotion_data}

        Please provide:
        1. Number of unique speakers identified
        2. Speaking patterns and turn-taking behavior
        3. Dominant speaker analysis
        4. Emotional states and stress indicators
        5. Potential relationships between speakers (caller/receiver, authority/subordinate, etc.)
        6. Any unusual vocal characteristics or behaviors

        Focus on investigative insights and behavioral analysis.
        '''
    
    def get_crime_analysis_prompt(self):
        """Get prompt template for crime analysis"""
        return '''
        As a forensic criminal content analysis expert, analyze the following for criminal indicators:

        Transcription:
        {transcription}

        Detected Keywords:
        {keywords}

        Context Analysis:
        {context_analysis}

        Please provide:
        1. Criminal activity assessment (type and severity)
        2. Intent analysis - is this planning, execution, or aftermath?
        3. Specific threats or violence indicators
        4. Drug-related, theft, or other crime category analysis
        5. Urgency level for law enforcement action
        6. Potential victims or targets mentioned
        7. Evidence of ongoing or planned criminal enterprise

        Be specific about criminal law violations and investigative priorities.
        '''
    
    def get_investigation_prompt(self):
        """Get prompt template for investigation recommendations"""
        return '''
        As a forensic investigation consultant, review this complete analysis and provide actionable recommendations:

        Complete Forensic Data:
        {all_data}

        Please provide specific recommendations for:
        1. Immediate actions required (if any)
        2. Additional evidence to collect
        3. Interview targets and key questions
        4. Surveillance or monitoring recommendations
        5. Legal considerations and warrant requirements
        6. Coordination with other agencies or departments
        7. Evidence preservation and chain of custody
        8. Timeline for investigation steps

        Prioritize recommendations by urgency and investigative value.
        '''
    
    def get_criminal_intent_prompt(self):
        """Get prompt template for criminal intent analysis"""
        return '''
        As a forensic criminal psychology expert, analyze this audio transcript for criminal intent indicators:

        Focus on:
        1. Explicit criminal planning or intent
        2. Threat assessment and credibility
        3. Psychological indicators of violent intent
        4. Communication patterns suggesting criminal organization
        5. Evidence of premeditation vs spontaneous criminal thought
        6. Risk assessment for potential violence or criminal acts
        7. Urgency level for law enforcement intervention

        Provide specific examples from the transcript and rate intent likelihood (0-100%).
        Consider cultural and linguistic context for accurate assessment.
        '''
    
    def get_context_analysis_prompt(self):
        """Get prompt template for contextual analysis"""
        return '''
        As a forensic context analyst, examine the broader context of this communication:

        Analyze:
        1. Relationship dynamics between speakers
        2. Power structures and hierarchies indicated
        3. Environmental context clues (background sounds, locations)
        4. Emotional state progression throughout conversation
        5. Communication patterns and behavioral indicators
        6. Cultural and social context affecting interpretation
        7. Timeline and sequence analysis
        8. External pressures or influences affecting behavior

        Provide insights that support investigation strategy and evidence interpretation.
        '''
    
    def test_api_connection(self):
        """Test OpenAI API connection"""
        try:
            if not self.client:
                return False, "OpenAI client not initialized"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Test connection - please respond with 'OK'"}
                ],
                max_tokens=10
            )
            
            return True, "API connection successful"
            
        except Exception as e:
            return False, f"API connection failed: {e}"
    
    def save_insights_to_file(self, insights, output_path):
        """Save generated insights to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(insights)
            
            self.logger.info(f"Insights saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving insights: {e}")
    
    def configure_api_key(self, api_key):
        """Configure OpenAI API key"""
        try:
            self.client = openai.OpenAI(api_key=api_key)
            
            # Test the connection
            success, message = self.test_api_connection()
            
            if success:
                # Save to config file
                config = {'openai_api_key': api_key}
                with open('config.json', 'w') as f:
                    json.dump(config, f)
                
                self.logger.info("OpenAI API key configured successfully")
                return True, "API key configured and tested successfully"
            else:
                self.client = None
                return False, f"API key test failed: {message}"
                
        except Exception as e:
            self.logger.error(f"API key configuration error: {e}")
            self.client = None
            return False, f"Configuration failed: {e}"
