"""
Enhanced Keyword Detection Module - Multi-language crime keyword detection with advanced NLP analysis
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from textblob import TextBlob
from langdetect import detect, DetectorFactory
import logging
import json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Optional
import unicodedata

# Set seed for consistent language detection
DetectorFactory.seed = 0


class EnhancedKeywordDetector:
    """Enhanced keyword detector with multi-language support and contextual analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stemmer = PorterStemmer()
        
        # Download required NLTK data
        self.download_nltk_data()
        
        # Enhanced multi-language crime keywords
        self.crime_keywords = {
            'english': {
                'violence': ['murder', 'kill', 'death', 'shoot', 'stab', 'attack', 'assault', 'beat', 'torture', 'violence'],
                'weapons': ['gun', 'pistol', 'rifle', 'knife', 'blade', 'sword', 'bomb', 'explosive', 'weapon', 'ammunition'],
                'threats': ['threat', 'threaten', 'intimidate', 'blackmail', 'extort', 'revenge', 'retaliate', 'warn'],
                'crimes': ['steal', 'theft', 'robbery', 'burglary', 'fraud', 'scam', 'cheat', 'embezzle', 'smuggle'],
                'drugs': ['drugs', 'cocaine', 'heroin', 'marijuana', 'meth', 'opium', 'trafficking', 'dealer', 'addict'],
                'kidnapping': ['kidnap', 'abduct', 'ransom', 'hostage', 'captive', 'prisoner', 'tie up', 'lock up'],
                'conspiracy': ['plan', 'plot', 'scheme', 'conspiracy', 'organize', 'coordinate', 'arrange', 'setup']
            },
            'hindi': {
                'violence': ['हत्या', 'मारना', 'मार डालना', 'हत्यारा', 'मृत्यु', 'मरना', 'गोली मारना', 'छुरा मारना', 'हमला', 'मारपीट', 'हिंसा', 'यातना'],
                'weapons': ['बंदूक', 'पिस्तौल', 'राइफल', 'छुरी', 'ब्लेड', 'तलवार', 'बम', 'विस्फोटक', 'हथियार', 'गोलीबारी'],
                'threats': ['धमकी', 'धमकाना', 'डराना', 'ब्लैकमेल', 'जबरन वसूली', 'बदला', 'चेतावनी', 'सबक सिखाना'],
                'crimes': ['चोरी', 'डकैती', 'लूटना', 'धोखाधड़ी', 'ठगी', 'भ्रष्टाचार', 'रिश्वत', 'तस्करी'],
                'drugs': ['नशा', 'ड्रग्स', 'अफीम', 'गांजा', 'कोकीन', 'हेरोइन', 'तस्करी', 'नशेबाज़'],
                'kidnapping': ['अपहरण', 'किडनैप', 'फिरौती', 'बंधक', 'कैदी', 'बांधना', 'बंद करना'],
                'conspiracy': ['साज़िश', 'योजना', 'प्लान', 'षड्यंत्र', 'आयोजन', 'तैयारी']
            },
            'gujarati': {
                'violence': ['હત્યા', 'મારવું', 'મારી નાખવું', 'હત્યારો', 'મૃત્યુ', 'મરવું', 'ગોળી મારવી', 'છરી મારવી', 'હુમલો', 'મારામારી', 'હિંસા', 'યાતના'],
                'weapons': ['બંદૂક', 'પિસ્તોલ', 'રાઈફલ', 'છરી', 'બ્લેડ', 'તલવાર', 'બોમ્બ', 'વિસ્ફોટક', 'હથિયાર', 'ગોળીબાર'],
                'threats': ['ધમકી', 'ધમકાવવું', 'ડરાવવું', 'બ્લેકમેલ', 'જબરદસ્તી વસૂલાત', 'બદલો', 'ચેતવણી', 'સબક શીખવવું'],
                'crimes': ['ચોરી', 'લૂંટ', 'ડાકુ', 'છેતરપિંડી', 'ઠગાઈ', 'ભ્રષ્ટાચાર', 'લાંચ', 'દાણચોરી'],
                'drugs': ['નશો', 'ડ્રગ્સ', 'અફીણ', 'ગાંજો', 'કોકેઈન', 'હેરોઈન', 'દાણચોરી', 'નશેડી'],
                'kidnapping': ['અપહરણ', 'કિડનેપ', 'ખંડણી', 'બંધક', 'કેદી', 'બાંધવું', 'બંધ કરવું'],
                'conspiracy': ['કાવતરું', 'યોજના', 'પ્લાન', 'ષડયંત્ર', 'આયોજન', 'તૈયારી']
            }
        }
        
        # Severity levels for different keyword categories
        self.severity_levels = {
            'violence': 'CRITICAL',
            'weapons': 'HIGH',
            'threats': 'HIGH', 
            'kidnapping': 'HIGH',
            'drugs': 'MEDIUM',
            'crimes': 'MEDIUM',
            'conspiracy': 'MEDIUM'
        }
        
        # Context patterns that increase suspicion
        self.suspicious_patterns = {
            'english': [
                r'(going to|will|gonna)\s+(kill|murder|shoot)',
                r'(have|got)\s+a\s+(gun|knife|weapon)',
                r'(plan to|planning to)\s+(rob|steal|kidnap)',
                r'(meet at|come to)\s+.+\s+(tonight|tomorrow)',
                r'bring\s+(money|cash|drugs)',
                r'if you\s+(tell|report|go to police)'
            ],
            'hindi': [
                r'(जाना|करना|होगा)\s+(मार|हत्या|गोली)',
                r'(है|पास)\s+(बंदूक|छुरी|हथियार)',
                r'(योजना|प्लान)\s+(चोरी|अपहरण|लूट)',
                r'(मिलना|आना)\s+.+\s+(रात|कल)',
                r'(लाना|लेकर आना)\s+(पैसा|नकद|नशा)',
                r'अगर\s+(बताया|पुलिस|रिपोर्ट)'
            ],
            'gujarati': [
                r'(જવાનું|કરવું|થશે)\s+(મારવું|હત્યા|ગોળી)',
                r'(છે|પાસે)\s+(બંદૂક|છરી|હથિયાર)',
                r'(યોજના|પ્લાન)\s+(ચોરી|અપહરણ|લૂંટ)',
                r'(મળવું|આવવું)\s+.+\s+(રાત્રે|કાલે)',
                r'(લાવવું|લઈને આવવું)\s+(પૈસા|રોકડ|નશો)',
                r'જો\s+(કહ્યું|પોલીસ|રિપોર્ટ)'
            ]
        }
        
        # Initialize stop words for different languages
        self.stop_words = self.load_stop_words()
        
    def load_stop_words(self) -> Dict[str, set]:
        """Load stop words for different languages"""
        stop_words = {}
        try:
            stop_words['english'] = set(stopwords.words('english'))
        except:
            stop_words['english'] = set()
        
        # Add Hindi and Gujarati stop words
        stop_words['hindi'] = {'का', 'की', 'के', 'में', 'और', 'है', 'हैं', 'से', 'को', 'पर', 'यह', 'वह', 'एक', 'होना', 'करना', 'लेकिन', 'साथ', 'बाद', 'पहले', 'दूसरे'}
        stop_words['gujarati'] = {'ના', 'ની', 'ને', 'માં', 'અને', 'છે', 'થી', 'સાથે', 'પછી', 'પહેલાં', 'બીજા', 'એક', 'આ', 'તે', 'કરવું', 'થવું', 'પરંતુ'}
        
        return stop_words
    
    def download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            self.logger.warning(f"Error downloading NLTK data: {e}")
    
    def load_crime_keywords(self):
        """Load crime-related keywords in multiple languages"""
        keywords = {
            'english': {
                'violence': [
                    'murder', 'kill', 'death', 'shoot', 'gun', 'weapon', 'knife', 'stab',
                    'attack', 'assault', 'fight', 'violence', 'violent', 'blood', 'hurt',
                    'injure', 'wound', 'beating', 'hit', 'punch', 'slap', 'choke'
                ],
                'drugs': [
                    'drug', 'drugs', 'cocaine', 'heroin', 'marijuana', 'weed', 'meth',
                    'crystal', 'crack', 'pills', 'dealer', 'dealing', 'smuggle', 'trafficking',
                    'cartel', 'substance', 'narcotics', 'overdose', 'high', 'stash'
                ],
                'theft': [
                    'steal', 'theft', 'rob', 'robbery', 'burglary', 'burglar', 'thief',
                    'stolen', 'loot', 'heist', 'pickpocket', 'shoplifting', 'embezzle',
                    'fraud', 'scam', 'con', 'cheat', 'swindle'
                ],
                'terrorism': [
                    'terror', 'terrorism', 'terrorist', 'bomb', 'explosive', 'blast',
                    'jihad', 'radical', 'extremist', 'attack', 'plot', 'threat',
                    'target', 'destroy', 'explosion'
                ],
                'organized_crime': [
                    'gang', 'mafia', 'cartel', 'boss', 'hitman', 'contract', 'territory',
                    'turf', 'protection', 'extortion', 'racket', 'syndicate', 'crew',
                    'family', 'organization'
                ],
                'general_crime': [
                    'crime', 'criminal', 'illegal', 'law', 'police', 'arrest', 'jail',
                    'prison', 'court', 'judge', 'lawyer', 'evidence', 'witness',
                    'victim', 'suspect', 'guilty', 'innocent', 'charges'
                ]
            },
            'hindi': {
                'violence': [
                    'हत्या', 'मार', 'मौत', 'गोली', 'बंदूक', 'हथियार', 'चाकू',
                    'हमला', 'लड़ाई', 'हिंसा', 'खून', 'चोट', 'मारपीट'
                ],
                'drugs': [
                    'नशा', 'ड्रग्स', 'अफीम', 'गांजा', 'शराब', 'नशीला', 'तस्कर',
                    'तस्करी', 'माफिया', 'पदार्थ'
                ],
                'theft': [
                    'चोरी', 'लूट', 'डकैती', 'चोर', 'ठग', 'धोखा', 'फ्रॉड'
                ],
                'general_crime': [
                    'अपराध', 'अपराधी', 'गैरकानूनी', 'पुलिस', 'गिरफ्तार', 'जेल',
                    'कोर्ट', 'न्यायाधीश', 'गवाह', 'आरोप'
                ]
            },
            'gujarati': {
                'violence': [
                    'હત્યા', 'મારવું', 'મૃત્યુ', 'બંદૂક', 'હથિયાર', 'છરી',
                    'હુમલો', 'લડાઈ', 'હિંસા', 'લોહી', 'ઈજા'
                ],
                'drugs': [
                    'નશો', 'ડ્રગ્સ', 'અફીણ', 'ગાંજો', 'દારૂ', 'તસ્કરી'
                ],
                'theft': [
                    'ચોરી', 'લૂંટ', 'ડકૈતી', 'ચોર', 'ઠગ', 'છેતરપિંડી'
                ],
                'general_crime': [
                    'ગુનો', 'ગુનેગાર', 'ગેરકાયદેસર', 'પોલીસ', 'ધરપકડ',
                    'જેલ', 'કોર્ટ', 'ન્યાયાધીશ', 'સાક્ષી'
                ]
            }
        }
        
        return keywords
    
    def load_context_patterns(self):
        """Load contextual patterns that indicate criminal intent"""
        patterns = {
            'planning': [
                r'we need to.*',
                r'let\'s.*',
                r'going to.*',
                r'plan to.*',
                r'will.*',
                r'should.*',
                r'have to.*',
                r'meet at.*',
                r'bring.*',
                r'get.*'
            ],
            'threat': [
                r'i will.*',
                r'you will.*',
                r'if you don\'t.*',
                r'or else.*',
                r'watch out.*',
                r'be careful.*',
                r'you better.*',
                r'i\'m warning you.*'
            ],
            'location': [
                r'at the.*',
                r'near.*',
                r'behind.*',
                r'in front of.*',
                r'inside.*',
                r'outside.*',
                r'at.*street',
                r'at.*road',
                r'at.*place'
            ],
            'time': [
                r'at.*pm',
                r'at.*am',
                r'tonight',
                r'tomorrow',
                r'next week',
                r'this evening',
                r'midnight',
                r'after dark'
            ],
            'money': [
                r'\$\d+',
                r'rupees',
                r'cash',
                r'money',
                r'payment',
                r'pay.*',
                r'cost.*',
                r'price.*',
                r'thousand',
                r'million'
            ]
        }
        
        return patterns
    
    def detect_keywords(self, text, language='auto'):
        """Detect crime-related keywords in text"""
        try:
            if not text or len(text.strip()) == 0:
                return []
            
            # Detect language if auto
            if language == 'auto' or language == 'Multi-language':
                detected_lang = self.detect_language(text)
            else:
                detected_lang = language.lower()
            
            # Get appropriate keyword set
            keyword_set = self.get_keywords_for_language(detected_lang)
            
            # Clean and tokenize text
            text_lower = text.lower()
            tokens = word_tokenize(text_lower)
            
            # Remove punctuation and stop words
            clean_tokens = [token for token in tokens if token.isalpha() and 
                           token not in self.stop_words_en]
            
            # Find keyword matches
            detected_keywords = []
            keyword_positions = []
            
            for category, keywords in keyword_set.items():
                for keyword in keywords:
                    # Direct match
                    if keyword.lower() in text_lower:
                        detected_keywords.append({
                            'keyword': keyword,
                            'category': category,
                            'language': detected_lang,
                            'confidence': 1.0,
                            'positions': self.find_keyword_positions(text_lower, keyword.lower())
                        })
                    
                    # Stemmed match
                    keyword_stem = self.stemmer.stem(keyword.lower())
                    for token in clean_tokens:
                        if self.stemmer.stem(token) == keyword_stem:
                            detected_keywords.append({
                                'keyword': keyword,
                                'matched_word': token,
                                'category': category,
                                'language': detected_lang,
                                'confidence': 0.8,
                                'positions': self.find_keyword_positions(text_lower, token)
                            })
            
            # Remove duplicates
            unique_keywords = []
            seen = set()
            for kw in detected_keywords:
                key = (kw['keyword'], kw['category'])
                if key not in seen:
                    seen.add(key)
                    unique_keywords.append(kw)
            
            return unique_keywords
            
        except Exception as e:
            self.logger.error(f"Keyword detection error: {e}")
            return []
    
    def detect_language(self, text):
        """Detect the language of the text"""
        try:
            lang = detect(text)
            
            # Map language codes to our supported languages
            lang_mapping = {
                'en': 'english',
                'hi': 'hindi',
                'gu': 'gujarati'
            }
            
            return lang_mapping.get(lang, 'english')
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return 'english'
    
    def get_keywords_for_language(self, language):
        """Get keyword set for specified language"""
        if language in self.crime_keywords:
            return self.crime_keywords[language]
        else:
            # Fallback to English
            return self.crime_keywords['english']
    
    def find_keyword_positions(self, text, keyword):
        """Find all positions of a keyword in text"""
        positions = []
        start = 0
        while True:
            pos = text.find(keyword, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        return positions
    
    def analyze_context(self, text):
        """Analyze context around detected keywords"""
        try:
            if not text:
                return "No text available for context analysis"
            
            analysis = {
                'criminal_intent_score': 0.0,
                'threat_level': 'LOW',
                'flagged_sentences': [],
                'context_categories': [],
                'summary': ''
            }
            
            # Split into sentences
            sentences = sent_tokenize(text)
            
            flagged_sentences = []
            intent_indicators = 0
            
            for i, sentence in enumerate(sentences):
                sentence_flags = self.analyze_sentence(sentence)
                
                if sentence_flags['has_crime_keywords'] or sentence_flags['matches_patterns']:
                    flagged_sentences.append({
                        'sentence': sentence,
                        'index': i,
                        'crime_keywords': sentence_flags['crime_keywords'],
                        'matched_patterns': sentence_flags['matched_patterns'],
                        'intent_score': sentence_flags['intent_score']
                    })
                    
                    intent_indicators += sentence_flags['intent_score']
            
            # Calculate overall criminal intent score
            if len(sentences) > 0:
                analysis['criminal_intent_score'] = min(intent_indicators / len(sentences), 1.0)
            
            # Determine threat level
            if analysis['criminal_intent_score'] > 0.7:
                analysis['threat_level'] = 'HIGH'
            elif analysis['criminal_intent_score'] > 0.4:
                analysis['threat_level'] = 'MEDIUM'
            else:
                analysis['threat_level'] = 'LOW'
            
            analysis['flagged_sentences'] = flagged_sentences
            
            # Identify context categories
            analysis['context_categories'] = self.identify_context_categories(text)
            
            # Generate summary
            analysis['summary'] = self.generate_context_summary(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Context analysis error: {e}")
            return {'summary': f"Context analysis failed: {e}"}
    
    def analyze_sentence(self, sentence):
        """Analyze a single sentence for criminal content"""
        try:
            flags = {
                'has_crime_keywords': False,
                'matches_patterns': False,
                'crime_keywords': [],
                'matched_patterns': [],
                'intent_score': 0.0
            }
            
            sentence_lower = sentence.lower()
            
            # Check for crime keywords
            keywords = self.detect_keywords(sentence)
            if keywords:
                flags['has_crime_keywords'] = True
                flags['crime_keywords'] = [kw['keyword'] for kw in keywords]
                flags['intent_score'] += 0.3
            
            # Check for contextual patterns
            for category, patterns in self.context_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence_lower):
                        flags['matches_patterns'] = True
                        flags['matched_patterns'].append(category)
                        flags['intent_score'] += 0.2
            
            # Additional scoring based on sentence structure
            # Imperative sentences (commands) get higher score
            words = sentence.lower().split()
            if len(words) > 0:
                if words[0] in ['do', 'don\'t', 'get', 'bring', 'meet', 'go', 'come']:
                    flags['intent_score'] += 0.1
                
                # Questions about illegal activities
                if sentence.strip().endswith('?') and any(word in sentence_lower for word in 
                   ['where', 'when', 'how', 'who', 'what']):
                    flags['intent_score'] += 0.1
            
            # Normalize intent score
            flags['intent_score'] = min(flags['intent_score'], 1.0)
            
            return flags
            
        except Exception as e:
            self.logger.error(f"Sentence analysis error: {e}")
            return {'has_crime_keywords': False, 'matches_patterns': False, 
                   'crime_keywords': [], 'matched_patterns': [], 'intent_score': 0.0}
    
    def identify_context_categories(self, text):
        """Identify which contextual categories are present in the text"""
        categories = []
        text_lower = text.lower()
        
        for category, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if category not in categories:
                        categories.append(category)
                    break
        
        return categories
    
    def generate_context_summary(self, analysis):
        """Generate a human-readable summary of the context analysis"""
        try:
            summary_parts = []
            
            # Threat level
            summary_parts.append(f"THREAT LEVEL: {analysis['threat_level']}")
            summary_parts.append(f"Criminal Intent Score: {analysis['criminal_intent_score']:.2f}")
            summary_parts.append("")
            
            # Flagged sentences
            if analysis['flagged_sentences']:
                summary_parts.append("FLAGGED CONTENT:")
                for flag in analysis['flagged_sentences'][:5]:  # Limit to top 5
                    summary_parts.append(f"• {flag['sentence']}")
                    if flag['crime_keywords']:
                        summary_parts.append(f"  Keywords: {', '.join(flag['crime_keywords'])}")
                    if flag['matched_patterns']:
                        summary_parts.append(f"  Patterns: {', '.join(flag['matched_patterns'])}")
                    summary_parts.append("")
            
            # Context categories
            if analysis['context_categories']:
                summary_parts.append(f"Context Categories Detected: {', '.join(analysis['context_categories'])}")
                summary_parts.append("")
            
            # Recommendations
            if analysis['criminal_intent_score'] > 0.6:
                summary_parts.append("⚠️  HIGH PRIORITY: This content contains significant criminal indicators")
                summary_parts.append("   Recommended actions: Immediate investigation, evidence preservation")
            elif analysis['criminal_intent_score'] > 0.3:
                summary_parts.append("⚠️  MEDIUM PRIORITY: This content contains potential criminal indicators")
                summary_parts.append("   Recommended actions: Further analysis, monitor for additional evidence")
            else:
                summary_parts.append("ℹ️  LOW PRIORITY: Limited criminal indicators detected")
                summary_parts.append("   Recommended actions: Archive for reference")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Summary generation error: {e}")
            return "Context analysis summary generation failed"
    
    def highlight_keywords_in_text(self, text, keywords):
        """Highlight detected keywords in text for UI display"""
        try:
            if not keywords:
                return text
            
            highlighted_text = text
            
            # Sort keywords by length (longest first) to avoid partial replacements
            sorted_keywords = sorted(keywords, key=lambda x: len(x['keyword']), reverse=True)
            
            for kw in sorted_keywords:
                keyword = kw['keyword']
                # Use case-insensitive replacement with HTML highlighting
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                highlighted_text = pattern.sub(f"<mark style='background-color: red; color: white;'>{keyword}</mark>", 
                                             highlighted_text)
            
            return highlighted_text
            
        except Exception as e:
            self.logger.error(f"Text highlighting error: {e}")
            return text
    
    def get_keyword_statistics(self, keywords):
        """Get statistics about detected keywords"""
        try:
            stats = {
                'total_keywords': len(keywords),
                'categories': {},
                'languages': {},
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0
            }
            
            for kw in keywords:
                # Category stats
                category = kw.get('category', 'unknown')
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                
                # Language stats
                language = kw.get('language', 'unknown')
                stats['languages'][language] = stats['languages'].get(language, 0) + 1
                
                # Confidence stats
                confidence = kw.get('confidence', 0)
                if confidence >= 0.8:
                    stats['high_confidence'] += 1
                elif confidence >= 0.5:
                    stats['medium_confidence'] += 1
                else:
                    stats['low_confidence'] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Statistics generation error: {e}")
            return {}
    
    def export_keywords(self, keywords, output_path):
        """Export detected keywords to JSON file"""
        try:
            output_data = {
                'keywords': keywords,
                'statistics': self.get_keyword_statistics(keywords),
                'timestamp': self.get_current_timestamp()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Keywords exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Keyword export error: {e}")
    
    def get_current_timestamp(self):
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def create_keyword_report(self, keywords, context_analysis, text):
        """Create a comprehensive keyword analysis report"""
        try:
            report_lines = []
            
            # Header
            report_lines.append("KEYWORD DETECTION AND CONTEXT ANALYSIS REPORT")
            report_lines.append("=" * 60)
            report_lines.append("")
            
            # Statistics
            stats = self.get_keyword_statistics(keywords)
            report_lines.append("DETECTION STATISTICS:")
            report_lines.append(f"Total Keywords Detected: {stats['total_keywords']}")
            report_lines.append(f"High Confidence: {stats['high_confidence']}")
            report_lines.append(f"Medium Confidence: {stats['medium_confidence']}")
            report_lines.append(f"Low Confidence: {stats['low_confidence']}")
            report_lines.append("")
            
            # Categories
            if stats['categories']:
                report_lines.append("CATEGORIES DETECTED:")
                for category, count in stats['categories'].items():
                    report_lines.append(f"• {category.capitalize()}: {count} keywords")
                report_lines.append("")
            
            # Languages
            if stats['languages']:
                report_lines.append("LANGUAGES DETECTED:")
                for language, count in stats['languages'].items():
                    report_lines.append(f"• {language.capitalize()}: {count} keywords")
                report_lines.append("")
            
            # Detailed keywords
            if keywords:
                report_lines.append("DETECTED KEYWORDS:")
                for kw in keywords:
                    report_lines.append(f"• {kw['keyword']} ({kw['category']}) - Confidence: {kw['confidence']:.2f}")
                report_lines.append("")
            
            # Context analysis summary
            if isinstance(context_analysis, dict) and 'summary' in context_analysis:
                report_lines.append("CONTEXT ANALYSIS:")
                report_lines.append(context_analysis['summary'])
            elif isinstance(context_analysis, str):
                report_lines.append("CONTEXT ANALYSIS:")
                report_lines.append(context_analysis)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return "Keyword report generation failed"
    
    def detect_keywords_enhanced(self, text: str, language: str = 'english') -> List[Dict]:
        """Enhanced keyword detection with multi-language support and context analysis"""
        try:
            detected_keywords = []
            
            if not text or not text.strip():
                return detected_keywords
            
            # Normalize language
            language = language.lower()
            if language == 'auto_detect':
                language = self.detect_text_language(text)
            
            # Get keywords for the specified language
            if language not in self.crime_keywords:
                language = 'english'  # Fallback
            
            keywords_dict = self.crime_keywords[language]
            text_lower = text.lower()
            
            # Search for keywords by category
            for category, keywords in keywords_dict.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        # Find all occurrences with context
                        pattern = re.compile(r'.{0,50}' + re.escape(keyword.lower()) + r'.{0,50}', re.IGNORECASE)
                        matches = pattern.findall(text)
                        
                        for match in matches:
                            detected_keywords.append({
                                'keyword': keyword,
                                'category': category,
                                'language': language,
                                'context': match.strip(),
                                'severity': self.severity_levels.get(category, 'LOW'),
                                'confidence': 0.9,  # High confidence for exact matches
                                'position': text_lower.find(match.lower())
                            })
            
            # Check for suspicious patterns
            pattern_keywords = self.detect_suspicious_patterns(text, language)
            detected_keywords.extend(pattern_keywords)
            
            # Remove duplicates and sort by severity
            unique_keywords = []
            seen = set()
            for kw in detected_keywords:
                key = f"{kw['keyword']}_{kw['position']}"
                if key not in seen:
                    seen.add(key)
                    unique_keywords.append(kw)
            
            # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            unique_keywords.sort(key=lambda x: severity_order.get(x['severity'], 4))
            
            self.logger.info(f"Detected {len(unique_keywords)} keywords in {language}")
            return unique_keywords
            
        except Exception as e:
            self.logger.error(f"Enhanced keyword detection error: {e}")
            return []
    
    def detect_suspicious_patterns(self, text: str, language: str) -> List[Dict]:
        """Detect suspicious patterns using regex"""
        pattern_keywords = []
        
        if language not in self.suspicious_patterns:
            return pattern_keywords
        
        patterns = self.suspicious_patterns[language]
        
        for pattern in patterns:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    context = text[max(0, match.start()-30):match.end()+30]
                    pattern_keywords.append({
                        'keyword': match.group(),
                        'category': 'suspicious_pattern',
                        'language': language,
                        'context': context.strip(),
                        'severity': 'HIGH',
                        'confidence': 0.8,
                        'position': match.start()
                    })
            except Exception as e:
                self.logger.warning(f"Pattern matching error for {pattern}: {e}")
        
        return pattern_keywords
    
    def detect_text_language(self, text: str) -> str:
        """Detect language of text using character patterns"""
        try:
            # Check for script patterns
            gujarati_chars = re.search(r'[\u0A80-\u0AFF]+', text)
            if gujarati_chars:
                return 'gujarati'
            
            hindi_chars = re.search(r'[\u0900-\u097F]+', text) 
            if hindi_chars:
                return 'hindi'
            
            # Default to English
            return 'english'
            
        except Exception as e:
            self.logger.warning(f"Language detection error: {e}")
            return 'english'
