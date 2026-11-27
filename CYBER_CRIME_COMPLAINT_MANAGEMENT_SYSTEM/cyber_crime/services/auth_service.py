from datetime import datetime, timedelta

from cyber_crime.models.user import User
from cyber_crime.storage.user_store import UserStore


MAX_ATTEMPTS = 5
LOCK_HOURS = 5
FMT = "%Y-%m-%d %H:%M:%S"


class AuthService:
    """Registration and login for citizens and officers."""

    def __init__(self):
        self.user_store = UserStore()

    # ---------------- citizen ----------------
    def register(self, name, email, password, phone="", dob="", gender=""):
        name, email, password = name.strip(), email.strip().lower(), password.strip()

        if not name:
            return False, "Name is required."
        if not email:
            return False, "Email is required."
        if not password:
            return False, "Password is required."

        user = User(
            user_id=self.user_store.generate_user_id(),
            name=name,
            email=email,
            password=password,
            role="citizen",
            phone=phone,
            dob=dob,
            gender=gender,
        )
        ok, message = self.user_store.add(user)
        return (True, user) if ok else (False, message)

    # ---------------- officer ----------------
    def register_officer(self, name, email, phone, dob, gender,
                         username, password, special_request=False):
        """
        Officer accounts are INACTIVE until admin approves.
        Everyone starts as GENERAL; SPECIAL only after admin approval.
        """
        if not password.strip():
            return False, "Password is required."

        user = User(
            user_id=self.user_store.generate_user_id(),
            name=name.strip(),
            email=email.strip().lower(),
            password=password.strip(),
            role="officer",
            active=False,
            username=username.strip().lower(),
            phone=phone,
            dob=dob,
            gender=gender,
            specialization="GENERAL",
            special_request=special_request,
        )
        ok, message = self.user_store.add(user)
        return (True, user) if ok else (False, message)

    # ---------------- login ----------------
    def login(self, email, password):
        """Citizen login (email + password)."""
        user = self.user_store.get_by_email(email)
        if user is None or user.role != "citizen":
            return False, "Invalid email or password."
        return self._check(user, password)

    def login_officer(self, username, password):
        """Officer login (username + password)."""
        user = self.user_store.get_by_username(username)
        if user is None or user.role != "officer":
            return False, "Invalid username or password."
        return self._check(user, password, officer=True)

    def _check(self, user, password, officer=False):
        now = datetime.now()

        # Currently locked?
        if user.locked_until:
            try:
                until = datetime.strptime(user.locked_until, FMT)
            except ValueError:
                until = now
            if now < until:
                left = until - now
                h, m = left.seconds // 3600 + left.days * 24, left.seconds % 3600 // 60
                return False, (f"Account deactivated due to {MAX_ATTEMPTS} failed "
                               f"attempts. Try again in {h}h {m}m.")
            # Lock expired: reactivate and reset counter
            user.locked_until, user.failed_attempts = "", 0
            self.user_store.update(user)

        if user.password != password.strip():
            user.failed_attempts += 1
            if user.failed_attempts >= MAX_ATTEMPTS:
                user.locked_until = (now + timedelta(hours=LOCK_HOURS)).strftime(FMT)
                self.user_store.update(user)
                return False, (f"Too many failed attempts. Account deactivated "
                               f"for {LOCK_HOURS} hours.")
            self.user_store.update(user)
            left = MAX_ATTEMPTS - user.failed_attempts
            return False, f"Invalid login details. {left} attempt(s) left."

        if not user.active:
            if officer:
                return False, "Your account is waiting for admin approval."
            return False, "Your account is inactive."

        if user.failed_attempts:
            user.failed_attempts = 0
            self.user_store.update(user)
        return True, user

    # ---------------- profile ----------------
    def find_by_id(self, user_id):
        return self.user_store.get_by_id(user_id)

    def update_profile(self, user_id, dob, gender, phone):
        user = self.user_store.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        user.dob, user.gender, user.phone = dob, gender, phone
        return self.user_store.update(user)

    def change_password(self, user_id, old_password, new_password):
        user = self.user_store.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        if user.password != old_password:
            return False, "Old password is incorrect."
        if not new_password.strip():
            return False, "New password cannot be empty."
        user.password = new_password.strip()
        return self.user_store.update(user)[0], "Password changed successfully."

    def reset_password(self, identifier, dob, new_password, officer=False):
        """Forgot password: verify identity with date of birth (YYYY-MM-DD)."""
        identifier = identifier.strip().lower()
        user = (self.user_store.get_by_username(identifier) if officer
                else self.user_store.get_by_email(identifier))
        role = "officer" if officer else "citizen"
        if user is None or user.role != role or not user.dob or user.dob != dob:
            return False, "Details do not match our records."
        if not new_password.strip():
            return False, "New password cannot be empty."
        user.password = new_password.strip()
        user.failed_attempts, user.locked_until = 0, ""
        ok, _ = self.user_store.update(user)
        return ok, "Password reset successfully. You can now login." if ok else "Could not reset password."
