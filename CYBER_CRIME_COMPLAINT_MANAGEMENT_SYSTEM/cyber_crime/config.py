from pathlib import Path


# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Data folder (all CSV files live here)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Admin credentials
ADMIN_EMAIL = "keerthi@gmail.com"
ADMIN_PASSWORD = "1234"

# ---------------------------------------------------------
# COMPLAINT CATEGORIES
# (name, plain-language description, is_sensitive)
# Sensitive = harassment type cases (not hacking / money theft)
# ---------------------------------------------------------
CATEGORIES = [
    ("ONLINE FRAUD", "Someone cheated me of money online / UPI / shopping", False),
    ("PHISHING", "Fake call, SMS, email or link asking for my details", False),
    ("IDENTITY THEFT", "Someone is using my name, photo or documents", False),
    ("HACKING", "My account, phone or computer was hacked", False),
    ("SOCIAL MEDIA CRIME", "Fake profile / social media misuse", False),
    ("CYBER BULLYING", "Someone is bullying or insulting me online", False),
    ("CYBER HARASSMENT", "Someone is harassing or threatening me online", True),
    ("STALKING", "Someone is following / tracking me online", True),
    ("MORPHED IMAGES", "My photos were edited or shared without consent", True),
    ("SEXTORTION", "Someone is blackmailing me with private photos/videos", True),
    ("CHILD ABUSE CONTENT", "Report content that harms a child", True),
    ("OTHER", "Something else", False),
]

SENSITIVE_CATEGORIES = [c[0] for c in CATEGORIES if c[2]]
HIGH_PRIORITY_CATEGORIES = ["ONLINE FRAUD", "IDENTITY THEFT", "PHISHING"]

STATUSES = [
    "SUBMITTED",
    "UNDER INVESTIGATION",
    "INFO REQUIRED",
    "RESOLVED",
    "CLOSED",
]
CLOSED_STATUSES = ["RESOLVED", "CLOSED"]
PRIORITIES = ["LOW", "NORMAL", "HIGH", "URGENT"]

ELDERLY_AGE = 60
INFO_REPLY_DAYS = 7
