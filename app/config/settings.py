"""
Configuration settings for SOC Phishing Detector
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseModel):
    """Application settings loaded from environment variables"""
    
    # API Keys
    virustotal_api_key: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    abuseipdb_api_key: str = os.getenv("ABUSEIPDB_API_KEY", "")
    
    # Application Settings
    app_name: str = os.getenv("APP_NAME", "SOC Phishing Detector")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", 8501))
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Rate Limiting
    vt_rate_limit: int = int(os.getenv("VT_RATE_LIMIT", 4))
    abuseipdb_rate_limit: int = int(os.getenv("ABUSEIPDB_RATE_LIMIT", 1000))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/soc_detector.log")
    
    # Session
    session_secret: str = os.getenv("SESSION_SECRET", "dev-secret-key")
    
    def validate_api_keys(self) -> tuple[bool, bool]:
        """Check if required API keys are present"""
        vt_valid = len(self.virustotal_api_key) > 10
        abuse_valid = len(self.abuseipdb_api_key) > 10
        return vt_valid, abuse_valid
    
    def get_api_status(self) -> dict:
        """Get API configuration status"""
        vt_valid, abuse_valid = self.validate_api_keys()
        return {
            "virustotal": {
                "configured": vt_valid,
                "status": "✅ Configured" if vt_valid else "❌ Missing API Key"
            },
            "abuseipdb": {
                "configured": abuse_valid,
                "status": "✅ Configured" if abuse_valid else "⚠️ Not Configured (Optional)"
            }
        }


# Global settings instance
settings = Settings()
