from cyber_crime.config import ADMIN_EMAIL, ADMIN_PASSWORD, STATUSES, PRIORITIES
from cyber_crime.services.admin_service import AdminService
from cyber_crime.ui.helper import(
    print_title, print_line, pause, ask, ask_yes_no,
    show_complaint,show_messages
)

admin_service = AdminService()


# =========================================================
# LOGIN + MENU
# =========================================================
def admin_login():
    print_title("ADMIN LOGIN")
    email = input("Admin Email: ").strip()
    password = input("Admin Password: ").strip()

    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        print("\nInvalid admin email or password.")
        pause()
        return

    print("\nAdmin login successful!")
    pause()
    admin_menu()


def admin_menu():
    while True:
        s = admin_service.get_dashboard_statistics()

        print_title("ADMIN DASHBOARD")
        print(f"Users: {s['total_users']} (Citizens {s['citizens']}, Officers {s['officers']}, "
              f"Special {s['special_officers']})")
        print(f"Complaints: {s['total_complaints']}   Submitted: {s['submitted_complaints']}   "
              f"High/Urgent: {s['high_priority_complaints']}")
        print(f"Special (minor/sensitive) cases: {s['special_cases']}")
        print_line()
        print("ATTENTION:")
        print(f"  Officer approvals pending : {s['pending_officers']}")
        print(f"  Unassigned complaints     : {s['unassigned']}")
        print(f"  Assistance requests       : {s['assistance']}")
        print(f"  Unread officer messages   : {s['unread_messages']}")
        print(f"  New fake complaint reports: {s['fake_reports']}")
        print_line()
        print("1. View All Complaints")
        print("2. Search Complaint")
        print("3. Manage Users")
        print("4. Update Complaint")
        print("5. Officer Approvals (account / special cell)")
        print("6. Officers & Workload")
        print("7. Unassigned Complaints (auto-assign)")
        print("8. Assistance Requests (elderly / help needed)")
        print("9. Messages (officers)")
        print(f"10. Fake Complaints {'(' + str(s['fake_reports']) + ' new)' if s['fake_reports'] else ''}")
        print("0. Logout")

        choice = input("\nEnter your choice: ").strip()
        actions = {
            "1": display_all_complaints, "2": search_complaint,
            "3": manage_users, "4": update_complaint,
            "5": officer_approvals, "6": officers_workload,
            "7": unassigned_complaints, "8": assistance_requests,
            "9": admin_messages, "10": fake_complaints,
        }
        if choice in actions:
            actions[choice]()
        elif choice == "0":
            print("\nAdmin logged out successfully.")
            break
        else:
            print("\nInvalid choice. Please try again.")
            pause()


# =========================================================
# COMPLAINTS
# =========================================================
def display_all_complaints():
    print_title("ALL COMPLAINTS")
    complaints = admin_service.get_all_complaints()
    if not complaints:
        print("\nNo complaints found.")
    users = {u.email.lower(): u.user_id for u in admin_service.user_store.get_all()}
    for c in complaints:
        print_line()
        print(f"Complaint ID     : {c.complaint_id}")
        print(f"User ID          : {users.get(c.citizen_email.lower(), 'N/A')}")
        print(f"Citizen Name     : {c.citizen_name}")
        print(f"Citizen Email    : {c.citizen_email}")
        print(f"Location         : {c.location}")
        print(f"Status           : {c.status}")
        print(f"Priority         : {c.priority}")
        print(f"Assigned Officer : {c.assigned_officer or 'Not assigned yet'}")
        print(f"Created At       : {c.created_at}")
    print_line()
    pause()


def search_complaint():
    print_title("ADMIN - SEARCH COMPLAINT")
    complaint = admin_service.get_complaint_by_id(input("Enter Complaint ID: "))
    if complaint is None:
        print("\nComplaint not found.")
    else:
        show_complaint(complaint, "admin", show_timeline=True)
        print_line()
    pause()


def update_complaint():
    print_title("UPDATE COMPLAINT")
    complaint_id = input("Enter Complaint ID: ").strip().upper()
    complaint = admin_service.get_complaint_by_id(complaint_id)
    if complaint is None:
        print("\nComplaint not found.")
        pause()
        return

    print("\n1. Status\n2. Priority\n3. Assign Officer (manual)\n0. Back")
    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        for i, s in enumerate(STATUSES, 1):
            print(f"{i}. {s}")
        pick = input("Select status: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(STATUSES):
            print("\n" + admin_service.update_status(complaint_id, STATUSES[int(pick) - 1])[1])
        else:
            print("\nInvalid status.")

    elif choice == "2":
        for i, p in enumerate(PRIORITIES, 1):
            print(f"{i}. {p}")
        pick = input("Select priority: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(PRIORITIES):
            print("\n" + admin_service.update_priority(complaint_id, PRIORITIES[int(pick) - 1])[1])
        else:
            print("\nInvalid priority.")

    elif choice == "3":
        wanted = "SPECIAL" if complaint.special_case else "GENERAL"
        print(f"\nThis is a {wanted}-type case. Eligible officers:")
        eligible = [o for o in admin_service.get_officers()
                    if o.active and o.specialization == wanted]
        loads = admin_service.officer_loads()
        for o in eligible:
            print(f"  {o.username:<15} {o.name:<20} open cases: {loads.get(o.username, 0)}")
        if not eligible:
            print("  (none available)")
        username = input("\nOfficer username: ").strip().lower()
        print("\n" + admin_service.assign_officer(complaint_id, username)[1])

    elif choice == "0":
        return
    else:
        print("\nInvalid choice.")
    pause()


def unassigned_complaints():
    print_title("UNASSIGNED COMPLAINTS")
    waiting = admin_service.get_unassigned()
    if not waiting:
        print("\nAll complaints are assigned.")
        pause()
        return

    for c in waiting:
        kind = "SPECIAL officer needed" if c.special_case else "General officer needed"
        print(f"{c.complaint_id}  {c.priority:<7}  {c.category:<20}  [{kind}]")

    if ask_yes_no("\nRun automatic assignment now?", default=True):
        count = admin_service.auto_assign_pending()
        print(f"\n{count} complaint(s) assigned.")
        if count < len(waiting):
            print("Some cases still have no eligible officer - approve more officers.")
    pause()


def assistance_requests():
    print_title("ASSISTANCE REQUESTS")
    requests = admin_service.get_assistance_requests()
    if not requests:
        print("\nNo open assistance requests.")
        pause()
        return

    print("These complainants asked for guidance. Phone numbers are visible")
    print("to admin only (help-desk call-back).\n")
    for c, phone in requests:
        print_line()
        print(f"{c.complaint_id}  {c.citizen_name}  Phone: {phone or 'N/A'}")
        print(f"   {c.category}  |  {c.status}  |  Officer: {c.assigned_officer or '-'}")
        if c.helper_name:
            print(f"   Helper: {c.helper_name}")
    print_line()
    pause()


# =========================================================
# OFFICERS
# =========================================================
def officer_approvals():
    print_title("OFFICER APPROVALS")
    pending = admin_service.get_pending_officers()
    if not pending:
        print("\nNo pending officer requests.")
        pause()
        return

    for o in pending:
        print_line()
        print(f"User ID  : {o.user_id}")
        print(f"Name     : {o.name}   Username: {o.username}")
        print(f"Gender   : {o.gender}   Age: {o.age}")
        print(f"Account  : {'ACTIVE' if o.active else 'WAITING APPROVAL'}")
        print(f"Special  : {'REQUESTED' if o.special_request else '-'}")
    print_line()

    print("\n1. Approve officer account")
    print("2. Approve special cell request")
    print("3. Reject special cell request")
    print("4. Reject registration (delete)")
    print("0. Back")
    choice = input("\nEnter your choice: ").strip()
    if choice == "0":
        return

    user_id = input("Officer User ID: ").strip().upper()
    if choice == "1":
        print("\n" + admin_service.approve_officer(user_id)[1])
    elif choice == "2":
        print("\n" + admin_service.approve_special(user_id)[1])
    elif choice == "3":
        print("\n" + admin_service.reject_special(user_id)[1])
    elif choice == "4":
        print("\n" + admin_service.delete_user(user_id)[1])
    else:
        print("\nInvalid choice.")
    pause()


def officers_workload():
    print_title("OFFICERS & WORKLOAD")
    officers = admin_service.get_officers()
    if not officers:
        print("\nNo officers registered.")
        pause()
        return

    loads = admin_service.officer_loads()
    print(f"{'Username':<14}{'Name':<20}{'Type':<10}{'Status':<10}{'Open cases'}")
    print_line()
    for o in officers:
        print(f"{o.username:<14}{o.name:<20}{o.specialization:<10}"
              f"{'ACTIVE' if o.active else 'PENDING':<10}{loads.get(o.username, 0)}")
    print_line()
    pause()


# =========================================================
# MESSAGES
# =========================================================
def admin_messages():
    print_title("MESSAGES")
    print("1. Inbox (from officers)")
    print("2. Send message to an officer")
    print("0. Back")
    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        messages = admin_service.inbox()
        show_messages(messages, "INBOX - OFFICER MESSAGES")
        admin_service.messages.mark_read(messages)
    elif choice == "2":
        complaint = None
        while complaint is None:
            complaint = admin_service.get_complaint_by_id(ask("Complaint ID: ", label="Complaint ID"))
            if complaint is None:
                print("  ! Complaint ID not found. Please try again.")
        default = complaint.assigned_officer
        prompt = f"Officer username [{default}]: " if default else "Officer username: "
        username = input(prompt).strip().lower() or default
        if not username:
            print("\nNo officer assigned to this complaint. Enter an officer username.")
            pause()
            return
        if username != default:
            print(f"\n{username} is not assigned to {complaint.complaint_id}. Message not sent.")
            pause()
            return
        text = ask("Message: ", label="Message")
        print("\n" + admin_service.message_officer(username, complaint.complaint_id, text)[1])
    elif choice == "0":
        return
    else:
        print("\nInvalid choice.")
    pause()


def fake_complaints():
    print_title("FAKE COMPLAINTS")
    reports = admin_service.fake_reports()
    if not reports:
        print("\nNo fake complaint reports.")
        pause()
        return
    for m in sorted(reports, key=lambda x: x.created_at, reverse=True):
        print_line()
        print(f"Complaint ID        : {m.complaint_id}{'   [NEW]' if not m.is_read else ''}")
        print(f"User ID             : {admin_service.user_id_of(m.complaint_id)}")
        print(f"Reported by officer : {m.sender_name}")
    print_line()
    admin_service.messages.mark_read(reports)
    pause()


# =========================================================
# USER MANAGEMENT
# =========================================================
def manage_users():
    while True:
        print_title("MANAGE USERS")
        print("1. View All Users\n2. Search User\n3. Activate User")
        print("4. Deactivate User\n5. Delete User\n0. Back")
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            view_all_users()
        elif choice == "2":
            search_user()
        elif choice == "3":
            print("\n" + admin_service.activate_user(input("Enter User ID: ").strip().upper())[1])
            pause()
        elif choice == "4":
            print("\n" + admin_service.deactivate_user(input("Enter User ID: ").strip().upper())[1])
            pause()
        elif choice == "5":
            user_id = input("Enter User ID: ").strip().upper()
            if input("Are you sure? (yes/no): ").strip().lower() == "yes":
                print("\n" + admin_service.delete_user(user_id)[1])
            else:
                print("\nDeletion cancelled.")
            pause()
        elif choice == "0":
            break
        else:
            print("\nInvalid choice.")
            pause()


def _print_user(user):
    print_line()
    print(f"User ID     : {user.user_id}")
    print(f"Name        : {user.name}")
    print(f"Email       : {user.email}")
    print(f"Role        : {user.role}" + (f" ({user.specialization})" if user.role == "officer" else ""))
    print(f"Status      : {'ACTIVE' if user.active else 'INACTIVE'}")
    print(f"Created At  : {user.created_at}")


def view_all_users():
    print_title("ALL USERS")
    users = admin_service.get_all_users()
    if not users:
        print("\nNo users found.")
    for user in users:
        _print_user(user)
    print_line()
    pause()


def search_user():
    print_title("SEARCH USER")
    user = admin_service.get_user_by_id(input("Enter User ID: ").strip().upper())
    if user is None:
        print("\nUser not found.")
    else:
        _print_user(user)
        print_line()
    pause()
