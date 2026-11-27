from cyber_crime.services.complaint_service import ComplaintService
from cyber_crime.services.message_service import MessageService


class InvestigationService:
    """
    Officer operations. An officer can only see and act on
    complaints that are assigned to them.
    """

    def __init__(self):
        self.complaint_service = ComplaintService()
        self.messages = MessageService()

    def get_assigned_complaints(self, officer):
        return [c for c in self.complaint_service.get_all_complaints()
                if c.assigned_officer == officer.username]

    def get_complaint(self, complaint_id, officer):
        """Returns the complaint only if it belongs to this officer."""
        complaint = self.complaint_service.search_complaint(complaint_id)
        if complaint is None or complaint.assigned_officer != officer.username:
            return None
        return complaint

    def accept_complaint(self, complaint_id, officer):
        complaint = self.get_complaint(complaint_id, officer)
        if complaint is None:
            return False, "Complaint not found in your assigned list."
        if complaint.status != "SUBMITTED":
            return False, "Only newly submitted complaints can be accepted."
        return self.complaint_service.update_status(
            complaint_id, "UNDER INVESTIGATION", officer.username
        )

    def update_status(self, complaint_id, status, officer):
        if self.get_complaint(complaint_id, officer) is None:
            return False, "Complaint not found in your assigned list."
        return self.complaint_service.update_status(
            complaint_id, status, officer.username
        )

    def update_priority(self, complaint_id, priority, officer):
        if self.get_complaint(complaint_id, officer) is None:
            return False, "Complaint not found in your assigned list."
        return self.complaint_service.update_priority(
            complaint_id, priority, officer.username
        )

    def add_remark(self, complaint_id, remark, officer):
        if self.get_complaint(complaint_id, officer) is None:
            return False, "Complaint not found in your assigned list."
        return self.complaint_service.add_remark(
            complaint_id, remark, officer.username
        )

    def request_info(self, complaint_id, text, officer):
        return self.complaint_service.request_info(
            complaint_id, officer.username, officer.name, text
        )

    # ---------------- officer <-> admin ----------------
    def message_admin(self, complaint_id, text, officer):
        complaint_id = (complaint_id or "").strip().upper()
        if complaint_id and self.get_complaint(complaint_id, officer) is None:
            return False, "Complaint not found among your assigned complaints."
        return self.messages.send(
            complaint_id, "officer", officer.username, "admin",
            text, officer=officer.username, kind="NOTE"
        )

    def report_fake(self, complaint_id, officer):
        """Officer flags an assigned complaint as fake -> notification to admin."""
        complaint_id = complaint_id.strip().upper()
        if self.get_complaint(complaint_id, officer) is None:
            return False, "Complaint not found among your assigned complaints."
        for m in self.messages.for_admin():
            if m.kind == "FAKE" and m.complaint_id == complaint_id:
                return False, "This complaint is already reported as fake."
        return self.messages.send(
            complaint_id, "officer", officer.username, "admin",
            "Reported as fake complaint", officer=officer.username, kind="FAKE"
        )

    def inbox(self, officer):
        mine = {c.complaint_id for c in self.get_assigned_complaints(officer)}
        return [m for m in self.messages.for_officer(officer.username)
                if m.complaint_id == "GENERAL" or m.complaint_id in mine]
