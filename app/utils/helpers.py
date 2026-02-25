"""
Helper utility functions
"""
import re
from datetime import datetime
from typing import Optional, List
import tldextract


def extract_domain(url_or_email: str) -> Optional[str]:
    """Extract domain from URL or email address"""
    try:
        if '@' in url_or_email:
            # It's an email
            return url_or_email.split('@')[1].strip()
        
        # It's a URL
        extracted = tldextract.extract(url_or_email)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
    except Exception:
        pass
    return None


def extract_ip_from_string(text: str) -> List[str]:
    """Extract IP addresses from text using regex"""
    # IPv4 pattern
    ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    
    # IPv6 pattern (simplified)
    ipv6_pattern = r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'
    
    ipv4_matches = re.findall(ipv4_pattern, text)
    ipv6_matches = re.findall(ipv6_pattern, text)
    
    return list(set(ipv4_matches + ipv6_matches))


def sanitize_text(text: str) -> str:
    """Sanitize text by removing special characters and extra whitespace"""
    if not text:
        return ""
    
    # Remove null bytes and other problematic characters
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def format_timestamp(timestamp: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_risk_score(threats: dict) ->
