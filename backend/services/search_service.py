from typing import List, Dict
import re


class SearchService:
    def __init__(self):
        # Common stopwords to restrict
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
            'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
            'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more',
            'very', 'after', 'words', 'long', 'than', 'first', 'been', 'call',
            'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get',
            'come', 'made', 'may', 'part', 'i', 'you', 'we', 'she', 'my',
            'me', 'him', 'his', 'her', 'our', 'your', 'their', 'its', 'us',
            'them', 'myself', 'yourself', 'himself', 'herself', 'ourselves',
            'yourselves', 'themselves', 'what', 'which', 'who', 'whom',
            'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'will', 'would', 'shall', 'should', 'may', 'might',
            'must', 'can', 'could', 'ought', 'need', 'dare', 'also', 'just', 'even', 'only', 'still', 'yet', 'ever', 'never'
        }
    
    def is_stopword(self, keyword: str) -> bool:
        """Check if keyword is a stopword"""
        keyword_lower = keyword.lower().strip()
        return keyword_lower in self.stopwords or len(keyword_lower) < 2
    
    def search_keyword(self, transcript: List[Dict], keyword: str) -> Dict:
        """Search for keyword in transcript and return matches with segments"""
        keyword_lower = keyword.lower()
        matches = []
        segments = []
        
        for segment in transcript:
            text_lower = segment["text"].lower()
            if keyword_lower in text_lower:
                # Find all occurrences in this segment
                start_pos = 0
                while True:
                    pos = text_lower.find(keyword_lower, start_pos)
                    if pos == -1:
                        break
                    matches.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"],
                        "match_position": pos
                    })
                    start_pos = pos + 1
                
                # Add segment if not already added
                if segment not in segments:
                    segments.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"]
                    })
        
        return {
            "matches": matches,
            "segments": segments,
            "total_count": len(matches)
        }

