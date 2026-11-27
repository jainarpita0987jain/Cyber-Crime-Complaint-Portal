"""
Menu entry points. The screens are split by role:
  citizen_ui.py  - citizens
  officer_ui.py  - investigation officers
  admin_ui.py    - admin
"""
from cyber_crime.ui.citizen_ui import citizen_auth_menu
from cyber_crime.ui.officer_ui import officer_auth_menu
from cyber_crime.ui.admin_ui import admin_login

__all__ = ["citizen_auth_menu", "officer_auth_menu", "admin_login"]
