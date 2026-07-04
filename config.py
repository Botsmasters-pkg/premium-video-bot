import os
from dotenv import load_dotenv

# Load .env file from current directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
OWNER_ID = int(os.getenv('OWNER_ID', 0))
LOG_CHANNEL = int(os.getenv('LOG_CHANNEL', 0))

# Parse admin IDs
admin_ids_str = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(aid.strip()) for aid in admin_ids_str.split(',') if aid.strip()]

# Polling Configuration
POLL_TIMEOUT = int(os.getenv('POLL_TIMEOUT', 60))
LONG_POLLING_TIMEOUT = int(os.getenv('LONG_POLLING_TIMEOUT', 60))

# Database
DATABASE_FILE = 'database.json'
BACKUP_DIR = 'data/backups'
LOG_DIR = 'logs'
TEMP_DIR = 'temp'

# Create required directories
for directory in [BACKUP_DIR, LOG_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# System Configuration
FREE_VIDEOS_PER_USER = 2
VIDEOS_PER_POINT = 5
REFERRAL_POINT_VALUE = 1

# Validate BOT_TOKEN
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in .env file!")
