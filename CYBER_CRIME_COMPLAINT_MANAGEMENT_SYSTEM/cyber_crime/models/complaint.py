from dataclasses import dataclass, field, asdict, fields
from datetime import datetime

from cyber_crime.utils.validation import to_bool

BOOL_FIELDS = ("is_minor", "is_sensitive", "special_case", "needs_assistance")


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Complaint:
    """
    A cyber crime complaint.
    special_case : minor or sensitive women/child case.
                   Only SPECIAL officers can handle it.
    history      : status timeline stored as 'time|event|by;time|event|by'
    """

    complaint_id: str
    citizen_name: str
    citizen_email: str
    category: str
    description: str
    location: str
    priority: str = "NORMAL"
    status: str = "SUBMITTED"
    assigned_officer: str = ""
    created_at: str = field(default_factory=_now)
    is_minor: bool = False
    is_sensitive: bool = False
    special_case: bool = False
    needs_assistance: bool = False
    guardian_name: str = ""
    guardian_phone: str = ""
    helper_name: str = ""
    helper_phone: str = ""
    investigation_remark: str = ""
    info_due: str = ""
    history: str = ""

    # ---------------- timeline ----------------
    def add_history(self, event, by="system"):
        entry = f"{_now()}|{event}|{by}".replace(";", ",")
        self.history = f"{self.history};{entry}" if self.history else entry

    def timeline(self):
        items = []
        for entry in self.history.split(";"):
            parts = entry.split("|")
            if len(parts) == 3:
                items.append(tuple(parts))
        return items

    # ---------------- storage ----------------
    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, record):
        names = [f.name for f in fields(cls)]
        data = {k: record.get(k, "") or "" for k in names}
        for key in BOOL_FIELDS:
            data[key] = to_bool(data[key])
        data["priority"] = data["priority"] or "NORMAL"
        data["status"] = data["status"] or "SUBMITTED"
        return cls(**data)
