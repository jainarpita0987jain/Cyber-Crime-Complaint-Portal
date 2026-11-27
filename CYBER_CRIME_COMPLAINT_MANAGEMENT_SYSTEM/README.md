# Cyber Crime Complaint Management System (Console)

Run from this folder:   python run.py     (or: python -m cyber_crime.main)

## Demo logins
Admin            : keerthi@gmail.com / 1234
General officer  : username kiki  / 9090
Special officer  : username meera / 9090   (women & child cell)
Citizens         : register from the Citizen menu

## What was added
- Minors (<18) and sensitive women cases (harassment, stalking, sextortion,
  morphed images, child abuse content) -> URGENT, confidential, handled only
  by admin-approved SPECIAL officers. Hacking / online fraud stay general.
- Officer self-registration. Account needs admin approval; female officers
  can request the sensitive-case role, admin approves/rejects.
- Fair auto-assignment: fewest open cases first, within the right pool.
- Elderly-friendly filing: plain-language categories, guided questions,
  review-before-submit, assistance request, helper details.
- Minors: guardian details recorded.
- In-app messaging, no phone/email shared:
  officer -> citizen "Request more info", citizen -> officer reply (one way),
  officer <-> admin messages (reassign request, escalation).
- Progress timeline for every complaint, duplicate-complaint warning.
- Privacy: officers see only their assigned cases and never the
  complainant's email/phone; citizens can only track their own complaints.
