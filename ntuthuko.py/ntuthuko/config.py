import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DATABASE = os.environ.get("DATABASE", os.path.join(BASE_DIR, "ntuthuko.db"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Seeded on first run. Change the password right after your first login.
    SEED_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@ntuthuko.local")
    SEED_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")
