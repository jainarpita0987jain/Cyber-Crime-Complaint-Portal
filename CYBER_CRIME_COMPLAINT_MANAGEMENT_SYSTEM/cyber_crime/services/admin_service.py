from cyber_crime.config import CLOSED_STATUSES
from cyber_crime.storage.user_store import UserStore
from cyber_crime.services.complaint_service import ComplaintService
from cyber_crime.services.message_service import MessageService


class AdminService:
    """Administrative operations."""

    def __init__(self):
        self.user_store = UserStore()
        self.complaint_service = ComplaintService()
        self.messages = MessageService()

    # =====================================================
    # USERS
    # =====================================================
    def get_all_users(self):
        return self.user_store.get_all()

    def get_user_by_id(self, user_id):
        return self.user_store.get_by_id(user_id)

    def get_user_by_email(self, email):
        return self.user_store.get_by_email(email)

    def activate_user(self, user_id):
        user = self.user_store.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        if user.active:
            return False, "User is already active."
        return self.user_store.activate(user_id)

    def deactivate_user(self, user_id):
        user = self.user_store.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        if not user.active:
            return False, "User is already inactive."
        result = self.user_store.deactivate(user_id)
        if user.role == "officer":
            self.complaint_service.release_officer_cases(user.username)
        return result

    def delete_user(self, user_id):
        user = self.user_store.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        result = self.user_store.delete(user_id)
        if user.role == "officer":
            self.complaint_service.release_officer_cases(user.username)
        return result

    # =====================================================
    # OFFICER APPROVALS
    # =====================================================
    def get_officers(self):
        return self.user_store.get_officers()

    def get_pending_officers(self):
        """Officers waiting for account approval or special approval."""
        return [o for o in self.get_officers()
                if not o.active or o.special_request]

    def approve_officer(self, user_id):
        officer = self.user_store.get_by_id(user_id)
        if officer is None or officer.role != "officer":
            return False, "Officer not found."
        officer.active = True
        self.user_store.update(officer)
        assigned = self.complaint_service.auto_assign_pending()
        return True, f"Officer approved. {assigned} waiting complaint(s) assigned."

    def approve_special(self, user_id):
        officer = self.user_store.get_by_id(user_id)
        if officer is None or officer.role != "officer":
            return False, "Officer not found."
        if not officer.special_request:
            return False, "This officer has no pending special request."
        if officer.gender != "FEMALE":
            return False, "Special cell requests are for female officers."
        officer.specialization = "SPECIAL"
        officer.special_request = False
        officer.active = True
        self.user_store.update(officer)
        assigned = self.complaint_service.auto_assign_pending()
        return True, f"Special officer approved. {assigned} waiting complaint(s) assigned."

    def reject_special(self, user_id):
        officer = self.user_store.get_by_id(user_id)
        if officer is None or officer.role != "officer":
            return False, "Officer not found."
        officer.special_request = False
        self.user_store.update(officer)
        return True, "Special request rejected. Officer stays GENERAL."

    def officer_loads(self):
        return self.complaint_service.assignment.officer_load(
            self.get_all_complaints()
        )

    # =====================================================
    # COMPLAINTS
    # =====================================================
    def get_all_complaints(self):
        return self.complaint_service.get_all_complaints()

    def get_complaint_by_id(self, complaint_id):
        return self.complaint_service.search_complaint(complaint_id)

    def get_complaints_by_status(self, status):
        return [c for c in self.get_all_complaints()
                if c.status.upper() == status.strip().upper()]

    def get_complaints_by_priority(self, priority):
        return [c for c in self.get_all_complaints()
                if c.priority.upper() == priority.strip().upper()]

    def get_unassigned(self):
        return self.complaint_service.get_unassigned()

    def auto_assign_pending(self):
        return self.complaint_service.auto_assign_pending()

    def assign_officer(self, complaint_id, username):
        return self.complaint_service.assign_officer(complaint_id, username)

    def update_status(self, complaint_id, status):
        return self.complaint_service.update_status(
            complaint_id, status, "admin"
        )

    def update_priority(self, complaint_id, priority):
        return self.complaint_service.update_priority(
            complaint_id, priority, "admin"
        )

    def get_assistance_requests(self):
        """Complaints where the citizen wants help. Returns (complaint, phone)."""
        result = []
        for c in self.get_all_complaints():
            if c.needs_assistance and c.status not in CLOSED_STATUSES:
                user = self.user_store.get_by_email(c.citizen_email)
                result.append((c, user.phone if user else ""))
        return result

    # =====================================================
    # MESSAGES (admin <-> officer)
    # =====================================================
    def inbox(self):
        return [m for m in self.messages.for_admin() if m.kind != "FAKE"]

    def fake_reports(self):
        return [m for m in self.messages.for_admin() if m.kind == "FAKE"]

    def user_id_of(self, complaint_id):
        c = self.get_complaint_by_id(complaint_id)
        if c is None:
            return "N/A"
        users = {u.email.lower(): u.user_id for u in self.user_store.get_all()}
        return users.get(c.citizen_email.lower(), "N/A")

    def message_officer(self, username, complaint_id, text):
        officer = self.user_store.get_by_username(username)
        if officer is None or officer.role != "officer":
            return False, "Officer not found."
        complaint = self.get_complaint_by_id(complaint_id)
        if complaint is None:
            return False, "Complaint not found."
        if complaint.assigned_officer != officer.username:
            return False, (f"{complaint.complaint_id} is not assigned to "
                           f"{officer.username}. Message not sent.")
        return self.messages.send(
            complaint_id, "admin", "admin", "officer",
            text, officer=officer.username, kind="NOTE"
        )

    # =====================================================
    # DASHBOARD
    # =====================================================
    def get_dashboard_statistics(self):
        users = self.get_all_users()
        complaints = self.get_all_complaints()
        officers = [u for u in users if u.role == "officer"]
        citizens = [u for u in users if u.role == "citizen"]

        return {
            "total_users": len(users),
            "active_users": sum(1 for u in users if u.active),
            "inactive_users": sum(1 for u in users if not u.active),
            "citizens": len(citizens),
            "officers": len(officers),
            "special_officers": sum(1 for o in officers if o.specialization == "SPECIAL" and o.active),
            "pending_officers": len(self.get_pending_officers()),
            "total_complaints": len(complaints),
            "submitted_complaints": sum(1 for c in complaints if c.status == "SUBMITTED"),
            "high_priority_complaints": sum(1 for c in complaints if c.priority in ("HIGH", "URGENT")),
            "special_cases": sum(1 for c in complaints if c.special_case),
            "unassigned": len(self.get_unassigned()),
            "assistance": len(self.get_assistance_requests()),
            "unread_messages": self.messages.unread_count(self.inbox()),
            "fake_reports": self.messages.unread_count(self.fake_reports()),
        }
