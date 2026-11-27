from cyber_crime.utils.validation import required_text


def print_line():
    print("-" * 70)


def print_title(title):
    print()
    print("=" * 70)
    print(title.center(70))
    print("=" * 70)


def pause():
    input("\nPress Enter to continue...")


def ask(prompt, validator=None, label="This field", optional=False):
    """Keeps asking until the answer is valid (friendly for beginners/elders)."""
    while True:
        value = input(prompt).strip()
        if not value and optional:
            return ""
        try:
            if validator:
                return validator(value)
            return required_text(value, label)
        except ValueError as error:
            print(f"  ! {error} Please try again.")


def ask_yes_no(prompt, default=None):
    hint = " (y/n): " if default is None else (" (Y/n): " if default else " (y/N): ")
    while True:
        value = input(prompt + hint).strip().lower()
        if not value and default is not None:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("  ! Please type y or n.")


def show_complaint(c, viewer="citizen", show_timeline=False):
    """
    viewer: citizen / officer / admin
    Officers never see the complainant's email or phone.
    """
    print_line()
    print(f"Complaint ID     : {c.complaint_id}")
    if viewer == "officer":
        print("Complainant      : Protected Complainant" if c.special_case
              else f"Complainant      : {c.citizen_name}")
    else:
        print(f"Citizen Name     : {c.citizen_name}")
        print(f"Citizen Email    : {c.citizen_email}")
    print(f"Category         : {c.category}")
    print(f"Description      : {c.description}")
    print(f"Location         : {c.location}")
    print(f"Status           : {c.status}")
    print(f"Priority         : {c.priority}")
    print(f"Assigned Officer : {c.assigned_officer or 'Not assigned yet'}")

    flags = []
    if c.is_minor:
        flags.append("MINOR")
    if c.special_case:
        flags.append("CONFIDENTIAL")
    if c.needs_assistance:
        flags.append("NEEDS ASSISTANCE")
    if flags and viewer != "citizen":
        print(f"Flags            : {', '.join(flags)}")

    if c.is_minor and c.guardian_name:
        print(f"Guardian         : {c.guardian_name}")
    if c.helper_name and viewer != "citizen":
        print(f"Helped By        : {c.helper_name}")
    if c.investigation_remark:
        print(f"Officer Remark   : {c.investigation_remark}")
    if c.info_due:
        print(f"Reply Due By     : {c.info_due}")
    print(f"Created At       : {c.created_at}")

    if show_timeline and c.timeline():
        print("\nProgress:")
        for time, event, by in c.timeline():
            print(f"  {time}  {event}  ({by})")


def show_messages(messages, title="MESSAGES"):
    print_title(title)
    if not messages:
        print("\nNo messages.")
        return
    for m in sorted(messages, key=lambda x: x.created_at, reverse=True):
        mark = "" if m.is_read else "  [NEW]"
        print_line()
        print(f"From      : {m.sender_name} ({m.sender_role}){mark}")
        print(f"Complaint : {m.complaint_id}")
        print(f"Time      : {m.created_at}")
        print(f"Message   : {m.message}")
    print_line()
