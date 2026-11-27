from dataclasses import fields
from datetime import datetime, timedelta

from cyber_crime.config import (
    DATA_DIR, SENSITIVE_CATEGORIES, HIGH_PRIORITY_CATEGORIES,
    STATUSES, PRIORITIES, CLOSED_STATUSES, INFO_REPLY_DAYS
)
from cyber_crime.models.complaint import Complaint
from cyber_crime.storage.csv_store import CSVStore
from cyber_crime.storage.user_store import UserStore
from cyber_crime.services.assignment_service import AssignmentService
from cyber_crime.services.message_service import MessageService


class ComplaintService:

    def __init__(self):
        self.store = CSVStore(
            DATA_DIR / "complaints.csv",
            [f.name for f in fields(Complaint)],
            "complaint_id"
        )
        self.assignment = AssignmentService()
        self.messages = MessageService()
        self.user_store = UserStore()

    # =====================================================
    # CREATE
    # =====================================================
    def generate_complaint_id(self):
        numbers = []
        for record in self.store.get_all():
            try:
                numbers.append(int(record["complaint_id"][6:]))
            except ValueError:
                pass
        year = datetime.now().year
        return f"CC{year}{(max(numbers) + 1 if numbers else 1):04d}"

    @staticmethod
    def classify(category, user):
        """
        Returns (is_minor, is_sensitive, special_case, priority).
        Special case = minor complainant, OR a sensitive (harassment type)
        case filed by a woman, OR child abuse content report.
        """
        is_minor = user.age is not None and user.age < 18
        is_sensitive = category in SENSITIVE_CATEGORIES
        special = is_minor or (
            is_sensitive and (
                user.gender == "FEMALE" or category == "CHILD ABUSE CONTENT"
            )
        )

        if special:
            priority = "URGENT"
        elif category in HIGH_PRIORITY_CATEGORIES:
            priority = "HIGH"
        else:
            priority = "NORMAL"
        return is_minor, is_sensitive, special, priority

    def add_complaint(self, user, category, description, location,
                      needs_assistance=False, guardian_name="",
                      guardian_phone="", helper_name="", helper_phone=""):

        is_minor, is_sensitive, special, priority = self.classify(category, user)

        complaint = Complaint(
            complaint_id=self.generate_complaint_id(),
            citizen_name=user.name,
            citizen_email=user.email,
            category=category,
            description=description,
            location=location,
            priority=priority,
            is_minor=is_minor,
            is_sensitive=is_sensitive,
            special_case=special,
            needs_assistance=needs_assistance,
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            helper_name=helper_name,
            helper_phone=helper_phone,
        )
        complaint.add_history("SUBMITTED", "citizen")

        officer = self.assignment.pick_officer(
            special, self.get_all_complaints()
        )
        if officer:
            complaint.assigned_officer = officer
            complaint.add_history(f"ASSIGNED to {officer}", "system")
        else:
            complaint.add_history("WAITING FOR OFFICER", "system")

        self.store.add(complaint.to_dict())
        return complaint

    def recent_duplicate(self, email, category, hours=24):
        """Warn if the same person filed the same category recently."""
        limit = datetime.now() - timedelta(hours=hours)
        for c in self.get_by_citizen(email):
            created = datetime.strptime(c.created_at, "%Y-%m-%d %H:%M:%S")
            if c.category == category and created >= limit:
                return c
        return None

    # =====================================================
    # READ
    # =====================================================
    def get_all_complaints(self):
        return [Complaint.from_dict(r) for r in self.store.get_all()]

    def search_complaint(self, complaint_id):
        record = self.store.find_by_key(complaint_id.strip().upper())
        return Complaint.from_dict(record) if record else None

    def get_by_citizen(self, email):
        email = email.lower()
        return [c for c in self.get_all_complaints()
                if c.citizen_email.lower() == email]

    def get_unassigned(self):
        return [c for c in self.get_all_complaints()
                if not c.assigned_officer and c.status not in CLOSED_STATUSES]

    # =====================================================
    # UPDATE
    # =====================================================
    def update_complaint(self, complaint):
        return self.store.update(complaint.complaint_id, complaint.to_dict())

    def update_status(self, complaint_id, status, by="system"):
        complaint = self.search_complaint(complaint_id)
        if complaint is None:
            return False, "Complaint not found."

        status = status.strip().upper()
        if status not in STATUSES:
            return False, "Invalid status."

        complaint.status = status
        complaint.add_history(status, by)
        self.update_complaint(complaint)
        return True, "Complaint status updated successfully."

    def update_priority(self, complaint_id, priority, by="system"):
        complaint = self.search_complaint(complaint_id)
        if complaint is None:
            return False, "Complaint not found."

        priority = priority.strip().upper()
        if priority not in PRIORITIES:
            return False, "Invalid priority."

        complaint.priority = priority
        complaint.add_history(f"PRIORITY {priority}", by)
        self.update_complaint(complaint)
        return True, "Priority updated successfully."

    def add_remark(self, complaint_id, remark, by="system"):
        complaint = self.search_complaint(complaint_id)
        if complaint is None:
            return False, "Complaint not found."
        remark = remark.strip().replace("\n", " ")
        if not remark:
            return False, "Remark cannot be empty."

        complaint.investigation_remark = remark
        complaint.add_history("REMARK ADDED", by)
        self.update_complaint(complaint)
        return True, "Investigation remark added successfully."

    # =====================================================
    # ASSIGNMENT
    # =====================================================
    def assign_officer(self, complaint_id, username, by="admin"):
        """Manual (admin) assignment. Pool rules still apply."""
        complaint = self.search_complaint(complaint_id)
        if complaint is None:
            return False, "Complaint not found."

        officer = self.user_store.get_by_username(username)
        if officer is None or officer.role != "officer" or not officer.active:
            return False, "Active officer not found."

        wanted = "SPECIAL" if complaint.special_case else "GENERAL"
        if officer.specialization != wanted:
            if complaint.special_case:
                return False, "Sensitive/minor cases go only to SPECIAL officers."
            return False, "General cases cannot go to SPECIAL officers."

        complaint.assigned_officer = officer.username
        complaint.add_history(f"ASSIGNED to {officer.username}", by)
        self.update_complaint(complaint)
        return True, f"Complaint assigned to {officer.username}."

    def auto_assign_pending(self):
        """Assign every waiting complaint using the fair rule."""
        complaints = self.get_all_complaints()
        count = 0
        for complaint in complaints:
            if complaint.assigned_officer or complaint.status in CLOSED_STATUSES:
                continue
            officer = self.assignment.pick_officer(
                complaint.special_case, complaints
            )
            if officer:
                complaint.assigned_officer = officer
                complaint.add_history(f"ASSIGNED to {officer}", "system")
                self.update_complaint(complaint)
                count += 1
        return count

    def release_officer_cases(self, username):
        """Used when an officer is deactivated/deleted."""
        for complaint in self.get_all_complaints():
            if (complaint.assigned_officer == username
                    and complaint.status not in CLOSED_STATUSES):
                complaint.assigned_officer = ""
                complaint.add_history(f"UNASSIGNED from {username}", "admin")
                self.update_complaint(complaint)
        return self.auto_assign_pending()

    # =====================================================
    # OFFICER <-> CITIZEN (indirect)
    # =====================================================
    def request_info(self, complaint_id, officer_username, officer_name, text):
        complaint = self.search_complaint(complaint_id)
        if complaint is None:
            return False, "Complaint not found."
        if complaint.assigned_officer != officer_username:
            return False, "This complaint is not assigned to you."
        if not text.strip():
            return False, "Message cannot be empty."

        due = (datetime.now() + timedelta(days=INFO_REPLY_DAYS)).strftime("%Y-%m-%d")
        complaint.status = "INFO REQUIRED"
        complaint.info_due = due
        complaint.add_history("INFO REQUIRED", officer_username)
        self.update_complaint(complaint)

        self.messages.send(
            complaint.complaint_id, "officer", officer_name, "citizen",
            text, officer=officer_username,
            citizen_email=complaint.citizen_email, kind="REQUEST"
        )
        return True, f"Request sent. Complainant should reply by {due}."

    def reply_to_request(self, complaint_id, citizen_email, text):
        complaint = self.search_complaint(complaint_id)
        if complaint is None or complaint.citizen_email.lower() != citizen_email.lower():
            return False, "Complaint not found."
        if complaint.status != "INFO REQUIRED":
            return False, "The officer has not asked for more information."
        if not text.strip():
            return False, "Reply cannot be empty."

        self.messages.send(
            complaint.complaint_id, "citizen", complaint.citizen_name,
            "officer", text, officer=complaint.assigned_officer,
            citizen_email=complaint.citizen_email, kind="REPLY"
        )
        complaint.status = "UNDER INVESTIGATION"
        complaint.info_due = ""
        complaint.add_history("INFO PROVIDED", "citizen")
        self.update_complaint(complaint)
        return True, "Your reply was sent to the investigating officer."
