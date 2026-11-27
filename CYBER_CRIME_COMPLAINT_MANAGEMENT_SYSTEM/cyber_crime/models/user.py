from dataclasses import dataclass, field, asdict
from datetime import datetime

from cyber_crime.utils.validation import to_bool, calculate_age

USER_FIELDS = [
    "user_id", "name", "email", "password", "role", "active",
    "created_at", "username", "phone", "dob", "gender",
    "specialization", "special_request",
    "failed_attempts", "locked_until",
]


@dataclass
class User:
    """
    A user of the system.
    role           : citizen / officer
    specialization : GENERAL / SPECIAL (officers only)
    special_request: officer asked to handle sensitive cases,
                     waiting for admin approval
    """

    user_id: str
    name: str
    email: str
    password: str
    role: str = "citizen"
    active: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    username: str = ""
    phone: str = ""
    dob: str = ""
    gender: str = ""
    specialization: str = "GENERAL"
    special_request: bool = False
    failed_attempts: int = 0
    locked_until: str = ""

    @property
    def age(self):
        return calculate_age(self.dob)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            password=data["password"],
            role=data.get("role") or "citizen",
            active=to_bool(data.get("active", True)),
            created_at=data.get("created_at", ""),
            username=data.get("username", ""),
            phone=data.get("phone", ""),
            dob=data.get("dob", ""),
            gender=data.get("gender", ""),
            specialization=data.get("specialization") or "GENERAL",
            special_request=to_bool(data.get("special_request", False)),
            failed_attempts=int(data.get("failed_attempts") or 0),
            locked_until=data.get("locked_until", ""),
        )
