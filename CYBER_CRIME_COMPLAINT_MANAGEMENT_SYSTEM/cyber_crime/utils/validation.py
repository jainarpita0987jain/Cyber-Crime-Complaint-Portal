from datetime import datetime, date

from cyber_crime.config import CATEGORIES


def required_text(value, field_name):
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty.")
    return value


def validate_email(email):
    email = email.strip()
    if "@" not in email or "." not in email:
        raise ValueError("Enter a valid email address.")
    return email


def validate_category(category):
    category = category.strip().upper()
    if category not in [c[0] for c in CATEGORIES]:
        raise ValueError("Invalid complaint category.")
    return category


def validate_phone(phone):
    phone = phone.strip().replace(" ", "")
    if not (phone.isdigit() and len(phone) == 10):
        raise ValueError("Enter a valid 10 digit phone number.")
    return phone


def validate_gender(value):
    value = value.strip().upper()
    mapping = {"M": "MALE", "F": "FEMALE", "O": "OTHER"}
    if value not in mapping:
        raise ValueError("Enter M (male), F (female) or O (other).")
    return mapping[value]


def validate_username(value):
    value = value.strip().lower()
    if len(value) < 3 or not value.isalnum():
        raise ValueError("Username must be 3+ letters/numbers, no spaces.")
    return value


def validate_dob(value):
    """Accepts DD-MM-YYYY and returns YYYY-MM-DD."""
    try:
        dob = datetime.strptime(value.strip(), "%d-%m-%Y").date()
    except ValueError:
        raise ValueError("Enter date as DD-MM-YYYY (example 25-12-1990).")
    age = calculate_age(dob.isoformat())
    if dob > date.today() or age > 110:
        raise ValueError("Enter a valid date of birth.")
    return dob.isoformat()


def validate_amount(value):
    try:
        amount = float(value.strip())
    except ValueError:
        raise ValueError("Enter a number (0 if no money was lost).")
    if amount < 0:
        raise ValueError("Amount cannot be negative.")
    return amount


def calculate_age(dob):
    """dob is YYYY-MM-DD. Returns None if missing/invalid."""
    try:
        born = datetime.strptime(dob, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    today = date.today()
    return today.year - born.year - (
        (today.month, today.day) < (born.month, born.day)
    )


def to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")
