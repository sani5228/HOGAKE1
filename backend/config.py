import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    # Environment
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'

    # Database
    try:
        import psycopg
        has_psycopg = True
    except ImportError:
        has_psycopg = False

    pg_driver = 'postgresql+psycopg' if has_psycopg else 'postgresql+pg8000'
    default_db_url = f"{pg_driver}://postgres:utkarsh@127.0.0.1:5432/procurement_db"

    DATABASE_URL = os.getenv('DATABASE_URL', default_db_url)
    # Ensure supported dialect prefix
    if DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', f"{pg_driver}://", 1)
    elif not has_psycopg and DATABASE_URL.startswith('postgresql+psycopg://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql+pg8000://', 1)

    # Security
    JWT_SECRET = os.getenv('JWT_SECRET', 'sih2026-fasal-prototype-secret-key-development')
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '24'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5500,http://127.0.0.1:5500,http://localhost:5000,http://127.0.0.1:5000').split(',')

    # Business Rules Constants (Authoritative from rules.md and PRD.md)
    DAILY_PLANNING_HOURS = 7
    DAILY_PLANNING_MINUTES = 420       # 7 hours normal planning capacity
    SHIFT_PLANNING_MINUTES = 210       # 210 minutes per shift (Shift 1 & Shift 2)
    DAILY_OPERATIONAL_HOURS = 8
    DAILY_OPERATIONAL_MINUTES = 480    # ~8 hours physical operating window
    HARD_CEILING_MINUTES = 510         # ~8.5 hours absolute operational ceiling for late arrivals

    # Working Shift Hours
    SHIFT_1_START = "09:00"
    SHIFT_1_END = "12:30"
    SHIFT_2_START = "14:00"
    SHIFT_2_END = "17:30"

    # Current Agricultural Season (Default Kharif, configurable by Admin)
    CURRENT_SEASON = os.getenv('CURRENT_SEASON', 'Kharif')
