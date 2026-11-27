from cyber_crime.config import CATEGORIES, ELDERLY_AGE
from cyber_crime.services.auth_service import AuthService
from cyber_crime.services.complaint_service import ComplaintService
from cyber_crime.services.message_service import MessageService
from cyber_crime.utils.validation import (
    required_text, validate_email, validate_phone, validate_dob,
    validate_gender, validate_amount
)
from cyber_crime.ui.helper import (
    print_title, print_line, pause, ask, ask_yes_no,
    show_complaint, show_messages
)

auth_service = AuthService()
complaint_service = ComplaintService()
message_service = MessageService()


# =========================================================
# AUTH
# =========================================================
def citizen_auth_menu():
    while True:
        print_title("CITIZEN")
        print("1. Register")
        print("2. Login")
        print("3. Forgot Password")
        print("0. Back")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            register_citizen()
        elif choice == "2":
            login_citizen()
        elif choice == "3":
            forgot_password_citizen()
        elif choice == "0":
            break
        else:
            print("\nInvalid choice.")


def register_citizen():
    print_title("CITIZEN REGISTRATION")

    name = ask("Name: ", label="Name")
    email = ask("Email: ", validate_email)
    phone = ask("Phone (10 digits): ", validate_phone)
    dob = ask("Date of birth (DD-MM-YYYY): ", validate_dob)
    gender = ask("Gender (M/F/O): ", validate_gender)

    while True:
        password = ask("Password: ", label="Password")
        if password == input("Confirm Password: ").strip():
            break
        print("  ! Passwords do not match. Please try again.")

    success, result = auth_service.register(
        name, email, password, phone, dob, gender
    )
    print_line()
    if success:
        print("\nRegistration successful!")
        print(f"User ID : {result.user_id}")
        print(f"Name    : {result.name}")
        print(f"Email   : {result.email}")
    else:
        print(f"\nRegistration failed: {result}")
    pause()


def login_citizen():
    print_title("CITIZEN LOGIN")
    email = input("Email: ").strip()
    password = input("Password: ").strip()

    success, result = auth_service.login(email, password)
    if not success:
        print(f"\nLogin failed: {result}")
        pause()
        return

    print(f"\nWelcome, {result.name}!")
    pause()
    citizen_menu(result)


# =========================================================
# MENU
# =========================================================
def citizen_menu(user):
    while True:
        unread = message_service.unread_count(
            message_service.for_citizen(user.email)
        )
        print_title("CYBER CRIME MANAGEMENT")
        print(f"Logged in as: {user.name}   (ID: {user.user_id})")
        if unread:
            print(f"*** You have {unread} new message(s) from the officer ***")
        print()
        print("1. File Complaint")
        print("2. Track Complaint")
        print("3. Display My Complaints")
        print(f"4. Messages / Reply to Officer {'(' + str(unread) + ' new)' if unread else ''}")
        print("5. Change Password")
        print("0. Logout")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            file_complaint(user)
        elif choice == "2":
            track_complaint(user)
        elif choice == "3":
            display_complaints(user)
        elif choice == "4":
            citizen_inbox(user)
        elif choice == "5":
            change_password(user)
        elif choice == "0":
            print("\nLogged out successfully.")
            break
        else:
            print("\nInvalid choice.")


# =========================================================
# FILE COMPLAINT
# =========================================================
def _complete_profile(user):
    """Old accounts may not have date of birth / gender / phone."""
    if user.dob and user.gender and user.phone:
        return
    print("\nPlease complete your profile first (one time only).")
    user.dob = user.dob or ask("Date of birth (DD-MM-YYYY): ", validate_dob)
    user.gender = user.gender or ask("Gender (M/F/O): ", validate_gender)
    user.phone = user.phone or ask("Phone (10 digits): ", validate_phone)
    auth_service.update_profile(user.user_id, user.dob, user.gender, user.phone)


def _choose_category():
    print("\nWhat happened to you? Choose the closest option:\n")
    for number, (name, plain, sensitive) in enumerate(CATEGORIES, 1):
        star = "  [confidential]" if sensitive else ""
        print(f"{number:>2}. {plain}{star}")

    while True:
        choice = input("\nEnter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1][0]
        print("  ! Please enter a number from the list.")


def _guided_description():
    """Step by step questions so nobody has to write a long complaint."""
    print("\nI will ask a few simple questions. Just answer one by one.\n")
    what = ask("1. What happened? (a few words): ", label="This answer")
    when = ask("2. When did it happen? (today / 2 days ago / date): ", label="This answer")
    who = ask("3. Which app, website, phone number or person was involved?\n"
              "   (press Enter if you don't know): ", optional=True)
    money = ask("4. Did you lose money? Enter amount, or 0 if none: ", validate_amount)

    mode = ""
    if money > 0:
        mode = ask("   How did you pay? (UPI / card / bank / other): ", optional=True)
    extra = ask("5. Anything else the officer should know? (optional): ", optional=True)

    parts = [f"What happened: {what}", f"When: {when}"]
    if who:
        parts.append(f"Involved: {who}")
    if money > 0:
        parts.append(f"Money lost: Rs {money:g}" + (f" via {mode}" if mode else ""))
    if extra:
        parts.append(f"Extra: {extra}")
    return " | ".join(parts)


def file_complaint(user):
    print_title("FILE CYBER CRIME COMPLAINT")
    _complete_profile(user)

    category = _choose_category()

    # ---- how to describe ----
    print("\nHow do you want to describe it?")
    print("1. Guided questions (easy, recommended)")
    print("2. I will write it myself")
    if input("\nEnter your choice (1/2): ").strip() == "2":
        description = ask("\nComplaint Description: ", label="Description")
    else:
        description = _guided_description()

    location = ask("\nLocation (city, district, state): ", label="Location")

    # ---- assistance / helper ----
    default_help = user.age is not None and user.age >= ELDERLY_AGE
    needs_assistance = ask_yes_no(
        "\nWould you like an officer to guide/assist you?", default=default_help
    )
    helper_name = helper_phone = ""
    if ask_yes_no("Is someone helping you file this complaint?", default=False):
        helper_name = ask("Helper's name: ", label="Name")
        helper_phone = ask("Helper's phone: ", validate_phone)

    # ---- guardian for minors ----
    guardian_name = guardian_phone = ""
    if user.age is not None and user.age < 18:
        print("\nYou are under 18. A parent/guardian must be recorded.")
        guardian_name = ask("Guardian's name: ", label="Name")
        guardian_phone = ask("Guardian's phone: ", validate_phone)

    # ---- duplicate warning ----
    duplicate = complaint_service.recent_duplicate(user.email, category)
    if duplicate:
        print(f"\nYou already filed a similar complaint today ({duplicate.complaint_id}).")
        if not ask_yes_no("Do you still want to file a new one?", default=False):
            print("\nCancelled. You can track the earlier complaint instead.")
            pause()
            return

    # ---- review ----
    print_line()
    print("PLEASE CHECK YOUR COMPLAINT")
    print(f"Category    : {category}")
    print(f"Description : {description}")
    print(f"Location    : {location}")
    print(f"Assistance  : {'Yes' if needs_assistance else 'No'}")
    print_line()
    if not ask_yes_no("Is everything correct? Submit now?", default=True):
        print("\nNot submitted. You can start again from the menu.")
        pause()
        return

    complaint = complaint_service.add_complaint(
        user, category, description, location, needs_assistance,
        guardian_name, guardian_phone, helper_name, helper_phone
    )

    print_line()
    print("\nComplaint submitted successfully!")
    print(f"Complaint ID : {complaint.complaint_id}   (please note this down)")
    print(f"Priority     : {complaint.priority}")
    if complaint.assigned_officer:
        print(f"Assigned To  : Officer {complaint.assigned_officer}")
    else:
        print("Assigned To  : An officer will be assigned shortly")
    if complaint.special_case:
        print("\nYour case will be handled confidentially by a specially")
        print("designated officer.")
    if needs_assistance:
        print("\nAn officer will guide you. Check 'Messages' regularly.")
    pause()


# =========================================================
# TRACK / LIST
# =========================================================
def track_complaint(user):
    print_title("TRACK COMPLAINT")
    complaint_id = input("Enter Complaint ID: ").strip()

    complaint = complaint_service.search_complaint(complaint_id)
    # citizens can only see their own complaints
    if complaint is None or complaint.citizen_email.lower() != user.email.lower():
        print("\nComplaint not found.")
        pause()
        return

    show_complaint(complaint, "citizen", show_timeline=True)
    print_line()
    pause()


def display_complaints(user):
    print_title("MY COMPLAINTS")
    mine = complaint_service.get_by_citizen(user.email)
    if not mine:
        print("\nYou have not filed any complaints.")
        pause()
        return

    for complaint in mine:
        show_complaint(complaint, "citizen")
    print_line()
    pause()


# =========================================================
# MESSAGES (officer -> citizen requests, citizen -> officer replies)
# =========================================================
def citizen_inbox(user):
    messages = message_service.for_citizen(user.email)
    show_messages(messages, "MESSAGES FROM OFFICER")
    message_service.mark_read(messages)

    waiting = [c for c in complaint_service.get_by_citizen(user.email)
               if c.status == "INFO REQUIRED"]
    if not waiting:
        pause()
        return

    print("\nThe officer needs more information for:")
    for c in waiting:
        print(f"  {c.complaint_id}  (reply by {c.info_due})")

    if not ask_yes_no("\nDo you want to reply now?", default=True):
        pause()
        return

    complaint_id = input("Complaint ID: ").strip().upper()
    text = ask("Your reply: ", label="Reply")
    success, message = complaint_service.reply_to_request(
        complaint_id, user.email, text
    )
    print(f"\n{message}")
    pause()


def change_password(user):
    print_title("CHANGE PASSWORD")
    old = input("Current Password: ").strip()
    new = input("New Password: ").strip()
    confirm = input("Confirm New Password: ").strip()

    if new != confirm:
        print("\nNew passwords do not match.")
    else:
        success, message = auth_service.change_password(user.user_id, old, new)
        print(f"\n{message}")
        if success:
            user.password = new
    pause()


def forgot_password_citizen():
    print_title("FORGOT PASSWORD")
    email = ask("Email: ", label="Email")
    dob = ask("Date of birth (DD-MM-YYYY): ", validate_dob)
    while True:
        new = ask("New Password: ", label="Password")
        if new == input("Confirm New Password: ").strip():
            break
        print("  ! Passwords do not match. Please try again.")
    ok, msg = auth_service.reset_password(email, dob, new)
    print(f"\n{msg}")
    pause()
