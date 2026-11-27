from cyber_crime.services.auth_service import AuthService
from cyber_crime.services.investigation_service import InvestigationService
from cyber_crime.utils.validation import (
    validate_email, validate_phone, validate_dob,
    validate_gender, validate_username
)
from cyber_crime.ui.helper import (
    print_title, print_line, pause, ask, ask_yes_no,
    show_complaint, show_messages
)

auth_service = AuthService()
investigation_service = InvestigationService()

OFFICER_STATUSES = {
    "1": "UNDER INVESTIGATION",
    "2": "RESOLVED",
    "3": "CLOSED",
}
PRIORITIES = {"1": "LOW", "2": "NORMAL", "3": "HIGH", "4": "URGENT"}


# =========================================================
# AUTH
# =========================================================
def officer_auth_menu():
    while True:
        print_title("INVESTIGATION OFFICER")
        print("1. Register")
        print("2. Login")
        print("3. Forgot Password")
        print("0. Back")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            register_officer()
        elif choice == "2":
            login_officer()
        elif choice == "3":
            forgot_password_officer()
        elif choice == "0":
            break
        else:
            print("\nInvalid choice.")


def register_officer():
    print_title("OFFICER REGISTRATION")

    name = ask("Full name: ", label="Name")
    email = ask("Email: ", validate_email)
    phone = ask("Phone (10 digits): ", validate_phone)
    dob = ask("Date of birth (DD-MM-YYYY): ", validate_dob)
    gender = ask("Gender (M/F/O): ", validate_gender)

    special_request = False
    if gender == "FEMALE":
        print("\nSensitive cases (women & child harassment cases) need")
        print("specially designated officers.")
        special_request = ask_yes_no(
            "Are you interested in taking charge of sensitive cases?"
        )

    username = ask("\nChoose a username: ", validate_username)
    while True:
        password = ask("Choose a password: ", label="Password")
        if password == input("Confirm password: ").strip():
            break
        print("  ! Passwords do not match. Please try again.")

    success, result = auth_service.register_officer(
        name, email, phone, dob, gender, username, password, special_request
    )
    print_line()
    if success:
        print("\nRegistration submitted!")
        print("You can log in after the admin approves your account.")
        if special_request:
            print("Your sensitive-case request will also be reviewed by the admin.")
    else:
        print(f"\nRegistration failed: {result}")
    pause()


def login_officer():
    print_title("OFFICER LOGIN")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    success, result = auth_service.login_officer(username, password)
    if not success:
        print(f"\nLogin failed: {result}")
        pause()
        return

    print(f"\nWelcome, {result.name}!")
    pause()
    investigation_officer_menu(result)


# =========================================================
# MENU
# =========================================================
def investigation_officer_menu(officer):
    while True:
        unread = investigation_service.messages.unread_count(
            investigation_service.inbox(officer)
        )
        role = "SPECIAL CELL (Women/Child)" if officer.specialization == "SPECIAL" else "GENERAL"

        print_title("INVESTIGATION OFFICER DASHBOARD")
        print(f"Officer: {officer.name} ({officer.username})   Type: {role}")
        if unread:
            print(f"*** {unread} new message(s) in your inbox ***")
        print_line()
        print("1. View Assigned Complaints")
        print("2. View Complaint Details")
        print("3. Accept Complaint")
        print("4. Update Investigation Status")
        print("5. Update Complaint Priority")
        print("6. Add Remark")
        print("7. Request More Info from Complainant")
        print(f"8. Inbox {'(' + str(unread) + ' new)' if unread else ''}")
        print("9. Message Admin")
        print("10. Fake Complaint")
        print("0. Logout")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            view_assigned(officer)
        elif choice == "2":
            view_complaint(officer)
        elif choice == "3":
            accept_complaint(officer)
        elif choice == "4":
            update_status(officer)
        elif choice == "5":
            update_priority(officer)
        elif choice == "6":
            add_remark(officer)
        elif choice == "7":
            request_info(officer)
        elif choice == "8":
            inbox(officer)
        elif choice == "9":
            message_admin(officer)
        elif choice == "10":
            fake_complaint(officer)
        elif choice == "0":
            print("\nInvestigation Officer logged out.")
            pause()
            break
        else:
            print("\nInvalid choice.")
            pause()


# =========================================================
# ACTIONS
# =========================================================
def view_assigned(officer):
    print_title("ASSIGNED COMPLAINTS")
    complaints = investigation_service.get_assigned_complaints(officer)
    if not complaints:
        print("\nNo complaints assigned to you.")
        pause()
        return

    # urgent first
    order = {"URGENT": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
    complaints.sort(key=lambda c: order.get(c.priority, 2))

    for c in complaints:
        print_line()
        who = "Protected Complainant" if c.special_case else c.citizen_name
        assist = "   [NEEDS ASSISTANCE]" if c.needs_assistance else ""
        print(f"{c.complaint_id}  |  {c.priority}  |  {c.status}{assist}")
        print(f"   {c.category}  -  {who}  -  {c.location}")
    print_line()
    pause()


def view_complaint(officer):
    print_title("COMPLAINT DETAILS")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    complaint = investigation_service.get_complaint(complaint_id, officer)
    if complaint is None:
        print("\nComplaint not found in your assigned list.")
        pause()
        return
    show_complaint(complaint, "officer", show_timeline=True)
    print_line()
    pause()


def accept_complaint(officer):
    print_title("ACCEPT COMPLAINT")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    success, message = investigation_service.accept_complaint(complaint_id, officer)
    print(f"\n{message}")
    pause()


def update_status(officer):
    print_title("UPDATE INVESTIGATION STATUS")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    print("\n1. UNDER INVESTIGATION\n2. RESOLVED\n3. CLOSED")
    choice = input("\nSelect status: ").strip()
    if choice not in OFFICER_STATUSES:
        print("\nInvalid status choice.")
    else:
        success, message = investigation_service.update_status(
            complaint_id, OFFICER_STATUSES[choice], officer
        )
        print(f"\n{message}")
    pause()


def update_priority(officer):
    print_title("UPDATE COMPLAINT PRIORITY")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    print("\n1. LOW\n2. NORMAL\n3. HIGH\n4. URGENT")
    choice = input("\nSelect priority: ").strip()
    if choice not in PRIORITIES:
        print("\nInvalid priority choice.")
    else:
        success, message = investigation_service.update_priority(
            complaint_id, PRIORITIES[choice], officer
        )
        print(f"\n{message}")
    pause()


def add_remark(officer):
    print_title("ADD REMARK")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    remark = ask("Remark: ", label="Remark")
    success, message = investigation_service.add_remark(complaint_id, remark, officer)
    print(f"\n{message}")
    pause()


def request_info(officer):
    print_title("REQUEST MORE INFO FROM COMPLAINANT")
    print("The complainant will see your question in the app.")
    print("No phone/email is shared with either side.\n")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    text = ask("What information do you need? ", label="Message")
    success, message = investigation_service.request_info(complaint_id, text, officer)
    print(f"\n{message}")
    pause()


def inbox(officer):
    messages = investigation_service.inbox(officer)
    show_messages(messages, "INBOX (Complainant replies & Admin messages)")
    investigation_service.messages.mark_read(messages)
    pause()


def fake_complaint(officer):
    print_title("REPORT FAKE COMPLAINT")
    complaint_id = ask("Complaint ID: ", label="Complaint ID").strip().upper()
    if not ask_yes_no(f"Report {complaint_id} as a fake complaint to admin?", default=False):
        print("\nCancelled.")
        pause()
        return
    print("\n" + investigation_service.report_fake(complaint_id, officer)[1])
    pause()


def message_admin(officer):
    print_title("MESSAGE ADMIN")
    print("1. General message")
    print("2. Request reassignment of a case")
    print("3. Escalate / report a delay")
    choice = input("\nSelect type: ").strip()

    prefix = {"1": "", "2": "[REASSIGN REQUEST] ", "3": "[ESCALATION] "}.get(choice)
    if prefix is None:
        print("\nInvalid choice.")
        pause()
        return

    complaint_id = ""
    if choice != "1" or ask_yes_no("Is it about a particular complaint?", default=False):
        complaint_id = input("Complaint ID: ").strip().upper()

    text = ask("Message: ", label="Message")
    success, message = investigation_service.message_admin(
        complaint_id, prefix + text, officer
    )
    print(f"\n{message}")
    pause()


def forgot_password_officer():
    print_title("FORGOT PASSWORD")
    username = ask("Username: ", label="Username")
    dob = ask("Date of birth (DD-MM-YYYY): ", validate_dob)
    while True:
        new = ask("New Password: ", label="Password")
        if new == input("Confirm New Password: ").strip():
            break
        print("  ! Passwords do not match. Please try again.")
    ok, msg = auth_service.reset_password(username, dob, new, officer=True)
    print(f"\n{msg}")
    pause()
