from dataclasses import dataclass, field, asdict, fields
from datetime import datetime

from cyber_crime.utils.validation import to_bool

MESSAGE_FIELDS = [
    "msg_id", "complaint_id", "sender_role", "sender_name",
    "receiver_role", "officer", "citizen_email", "kind",
    "message", "created_at", "is_read",
]


@dataclass
class Message:
    """
    In-app message. Nobody sees anybody's phone/email.
    kind: REQUEST (officer -> citizen info request)
          REPLY   (citizen -> officer)
          NOTE    (officer <-> admin)
    """

    msg_id: str
    complaint_id: str
    sender_role: str
    sender_name: str
    receiver_role: str
    officer: str = ""
    citizen_email: str = ""
    kind: str = "NOTE"
    message: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    is_read: bool = False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, record):
        names = [f.name for f in fields(cls)]
        data = {k: record.get(k, "") or "" for k in names}
        data["is_read"] = to_bool(data["is_read"])
        return cls(**data)
