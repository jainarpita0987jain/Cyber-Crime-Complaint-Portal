from cyber_crime.config import CLOSED_STATUSES
from cyber_crime.storage.user_store import UserStore


class AssignmentService:
    """
    Automatic, fair distribution of complaints.

    Pool rule:
      special case  -> only approved SPECIAL officers
      general case  -> only GENERAL officers
    Fairness rule: officer with the fewest open cases gets it;
    on a tie, the officer who was assigned a case longest ago.
    """

    def __init__(self):
        self.user_store = UserStore()

    def eligible_officers(self, special_case):
        wanted = "SPECIAL" if special_case else "GENERAL"
        return [
            u for u in self.user_store.get_officers()
            if u.active and u.specialization == wanted
        ]

    def pick_officer(self, special_case, complaints):
        officers = self.eligible_officers(special_case)
        if not officers:
            return ""

        def load(officer):
            mine = [c for c in complaints
                    if c.assigned_officer == officer.username]
            open_count = sum(
                1 for c in mine if c.status not in CLOSED_STATUSES
            )
            last = max((c.created_at for c in mine), default="")
            return (open_count, last)

        return min(officers, key=load).username

    def officer_load(self, complaints):
        """Returns {username: open_case_count} for all officers."""
        result = {}
        for officer in self.user_store.get_officers():
            result[officer.username] = sum(
                1 for c in complaints
                if c.assigned_officer == officer.username
                and c.status not in CLOSED_STATUSES
            )
        return result
