from cyber_crime.config import DATA_DIR
from cyber_crime.models.message import Message, MESSAGE_FIELDS
from cyber_crime.storage.csv_store import CSVStore


class MessageService:
    """
    All in-app communication.
      officer  -> citizen : info request (kind REQUEST)
      citizen  -> officer : reply        (kind REPLY)  [one way]
      officer <-> admin   : notes        (kind NOTE)
    """

    def __init__(self):
        self.store = CSVStore(
            DATA_DIR / "messages.csv",
            MESSAGE_FIELDS,
            "msg_id"
        )

    def _all(self):
        return [Message.from_dict(r) for r in self.store.get_all()]

    def _next_id(self):
        numbers = []
        for m in self._all():
            try:
                numbers.append(int(m.msg_id[1:]))
            except ValueError:
                pass
        return f"M{(max(numbers) + 1 if numbers else 1):05d}"

    def send(self, complaint_id, sender_role, sender_name, receiver_role,
             text, officer="", citizen_email="", kind="NOTE"):
        text = text.strip().replace("\n", " ")
        if not text:
            return False, "Message cannot be empty."

        message = Message(
            msg_id=self._next_id(),
            complaint_id=complaint_id or "GENERAL",
            sender_role=sender_role,
            sender_name=sender_name,
            receiver_role=receiver_role,
            officer=officer,
            citizen_email=citizen_email.lower(),
            kind=kind,
            message=text,
        )
        self.store.add(message.to_dict())
        return True, "Message sent."

    # ---------------- inboxes ----------------
    def for_citizen(self, email):
        email = email.lower()
        return [m for m in self._all()
                if m.receiver_role == "citizen" and m.citizen_email == email]

    def for_officer(self, username):
        return [m for m in self._all()
                if m.receiver_role == "officer" and m.officer == username]

    def for_admin(self):
        return [m for m in self._all() if m.receiver_role == "admin"]

    def unread_count(self, messages):
        return sum(1 for m in messages if not m.is_read)

    def mark_read(self, messages):
        ids = {m.msg_id for m in messages if not m.is_read}
        if not ids:
            return
        records = self.store.get_all()
        for record in records:
            if record["msg_id"] in ids:
                record["is_read"] = "True"
        self.store.save_all(records)
