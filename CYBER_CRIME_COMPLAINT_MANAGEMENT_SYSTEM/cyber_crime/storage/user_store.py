from cyber_crime.config import DATA_DIR
from cyber_crime.models.user import User, USER_FIELDS
from cyber_crime.storage.csv_store import CSVStore


class UserStore:
    """Stores and retrieves users from users.csv."""

    def __init__(self):
        self.store = CSVStore(
            DATA_DIR / "users.csv",
            USER_FIELDS,
            "user_id"
        )

    def get_all(self):
        return [User.from_dict(r) for r in self.store.get_all()]

    def get_by_id(self, user_id):
        for user in self.get_all():
            if user.user_id == user_id:
                return user
        return None

    def get_by_email(self, email):
        email = email.strip().lower()
        for user in self.get_all():
            if user.email.lower() == email:
                return user
        return None

    def get_by_username(self, username):
        username = username.strip().lower()
        for user in self.get_all():
            if user.username and user.username.lower() == username:
                return user
        return None

    def get_officers(self):
        return [u for u in self.get_all() if u.role == "officer"]

    def add(self, user):
        if self.get_by_id(user.user_id):
            return False, "User ID already exists."
        if self.get_by_email(user.email):
            return False, "Email already exists."
        if user.username and self.get_by_username(user.username):
            return False, "Username already taken."
        self.store.add(user.to_dict())
        return True, "User added successfully."

    def update(self, user):
        if self.store.update(user.user_id, user.to_dict()):
            return True, "User updated successfully."
        return False, "User not found."

    def delete(self, user_id):
        if self.get_by_id(user_id) is None:
            return False, "User not found."
        self.store.delete(user_id)
        return True, "User deleted successfully."

    def activate(self, user_id):
        user = self.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        user.active = True
        return self.update(user)

    def deactivate(self, user_id):
        user = self.get_by_id(user_id)
        if user is None:
            return False, "User not found."
        user.active = False
        return self.update(user)

    def generate_user_id(self):
        numbers = []
        for user in self.get_all():
            if user.user_id.startswith("U"):
                try:
                    numbers.append(int(user.user_id[1:]))
                except ValueError:
                    pass
        return f"U{(max(numbers) + 1 if numbers else 1):04d}"
