from cyber_crime.ui.menus import (
    citizen_auth_menu,
    admin_login,
    officer_auth_menu
)


from cyber_crime.ui import citizen_ui, officer_ui, admin_ui, helper
from cyber_crime.utils.escape import install, EscapeInput

install(citizen_ui, officer_ui, admin_ui)
citizen_auth_menu = citizen_ui.citizen_auth_menu
officer_auth_menu = officer_ui.officer_auth_menu
admin_login = admin_ui.admin_login


def run_app():
    try:
        _run()
    except EscapeInput:
        print("\nThank you for using the system!")


def _run():

    while True:

        print()

        print("=" * 60)
        print("           CYBER CRIME MANAGEMENT SYSTEM")
        print("=" * 60)

        print("1. Citizen")
        print("2. Admin")
        print("3. Investigation Officer")
        print("0. Exit")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        # -------------------------------------------------
        # CITIZEN
        # -------------------------------------------------

        if choice == "1":

            citizen_auth_menu()

        # -------------------------------------------------
        # ADMIN
        # -------------------------------------------------

        elif choice == "2":

            admin_login()

        # -------------------------------------------------
        # INVESTIGATION OFFICER
        # -------------------------------------------------

        elif choice == "3":

            officer_auth_menu()

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        elif choice == "0":

            print(
                "\nThank you for using the system!"
            )

            break

        # -------------------------------------------------
        # INVALID CHOICE
        # -------------------------------------------------

        else:

            print(
                "\nInvalid choice. Please enter 1, 2, 3, or 0."
            )