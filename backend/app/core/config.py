import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # AI Analysis Configuration
    AI_ANALYSIS_ENABLED = os.getenv("AI_ANALYSIS_ENABLED", "true").lower() == "true"
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4000"))
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.1"))
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


config = Config()
