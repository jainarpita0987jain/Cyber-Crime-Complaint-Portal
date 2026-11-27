# 🛡️ Cyber Crime Complaint Management System

A Python-based, command-line application designed to simplify cybercrime complaint registration, tracking, assignment, and investigation management. The system provides separate interfaces for citizens, officers, and administrators, with special handling for sensitive cases involving women and minors.

## 📌 Project Overview

The Cyber Crime Complaint Management System is a console-based application built using Python. It aims to organize complaint-handling workflows through role-based access, complaint tracking, officer assignment, investigation updates, and internal messaging.

The application runs directly in the terminal or Command Prompt without requiring a web browser or graphical user interface.

## ✨ Features

### 👤 Citizen Module
- Citizen registration and login
- Password recovery and password change
- Cybercrime complaint submission
- Guided complaint filing for easier reporting
- Complaint tracking using complaint IDs
- View previously submitted complaints
- In-app messaging and replies to officers
- Assistance requests for users who need help filing complaints
- Duplicate complaint warnings

### 👮 Officer Module
- Officer self-registration with administrator approval
- View and manage assigned complaints
- Update investigation progress
- Request additional information from citizens
- Communicate with administrators
- Request complaint reassignment or escalation
- Special officer role for eligible sensitive cases

### 🔐 Administrator Module
- View and search all complaints
- Manage citizen and officer accounts
- Approve or reject officer registrations
- Approve or reject special-cell role requests
- Update complaint status and priority
- Assign officers manually
- Monitor officer workloads
- Review assistance requests
- Manage reports of suspected fake complaints
- View complaint statistics and pending tasks

### 🚨 Sensitive Case Handling
- Urgent handling for complaints involving minors and specified sensitive categories
- Special-cell assignment for eligible cases
- Guardian details recorded for minors
- Restricted access to sensitive complaints
- Priority-based complaint management

### 🔒 Privacy and Communication
- Role-based access control
- Citizens can track only their own complaints
- Officers can access only their assigned cases
- Officers do not see citizens' email addresses or phone numbers through the officer interface
- Internal messaging without sharing personal contact details

## 🛠️ Technologies Used

- **Language:** Python
- **Interface:** Command Line Interface (CLI)
- **Data Storage:** CSV files
- **Architecture:** Modular design with separate models, services, storage, and user interfaces

## 📂 Project Structure

```text
CYBER_CRIME_COMPLAINT_MANAGEMENT_SYSTEM/
├── cyber_crime/
│   ├── models/
│   │   ├── user.py
│   │   ├── complaint.py
│   │   └── message.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── complaint_service.py
│   │   ├── admin_service.py
│   │   ├── officer_service.py
│   │   ├── assignment_service.py
│   │   ├── investigation_service.py
│   │   └── message_service.py
│   ├── storage/
│   │   ├── user_store.py
│   │   └── csv_store.py
│   ├── ui/
│   │   ├── admin_ui.py
│   │   ├── citizen_ui.py
│   │   ├── officer_ui.py
│   │   ├── menus.py
│   │   └── helper.py
│   ├── utils/
│   ├── data/
│   │   ├── users.csv
│   │   ├── complaints.csv
│   │   └── messages.csv
│   ├── app.py
│   ├── config.py
│   └── main.py
├── run.py
└── README.md
```

*Note: The structure above summarizes the project modules; verify individual filenames against the repository before using this tree as an exact representation.*

## ⚙️ Requirements

- Python 3
- Command Prompt, Linux terminal, or another compatible shell
- No web server or browser required

## 🚀 Installation and Execution

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
```

### 2. Navigate to the project directory

```bash
cd CYBER_CRIME_COMPLAINT_MANAGEMENT_SYSTEM
```

### 3. Run the application

```bash
python run.py
```

Alternatively, run:

```bash
python -m cyber_crime.main
```

Use `python3` instead of `python` if required by your system.

## 🧪 Demo Accounts

The project README includes the following demonstration accounts:

| Role | Login | Password |
|---|---|---|
| Administrator | `keerthi@gmail.com` | `1234` |
| General Officer | `kiki` | `9090` |
| Special Officer | `meera` | `9090` |

Citizens can register through the Citizen menu.

**Security warning:** These are demonstration credentials, not production-safe credentials. Change or remove them before public deployment, and never use real personal information in demonstration data.

## 🎯 Project Objectives

- Develop a practical Python-based complaint management application.
- Demonstrate modular programming and separation of concerns.
- Implement role-based workflows for citizens, officers, and administrators.
- Organize complaint records using CSV-based storage.
- Provide complaint tracking, investigation updates, and internal communication.
- Apply priority-based handling and access restrictions to sensitive cases.

## 🔮 Future Enhancements

- Database integration using SQLite or PostgreSQL
- Secure password hashing and improved authentication
- A graphical or web-based interface
- Audit logs and stronger access controls
- Automated notifications and reporting
- Automated testing and deployment support

## ⚠️ Disclaimer

This project is intended for educational and demonstration purposes. It is not an official government cybercrime reporting portal and does not submit complaints to law enforcement authorities.

The application should not be used to store real victims' sensitive information without appropriate security, privacy protections, and authorization.

## 👨‍💻 Author

**Arpita Jain**

Developed as a Python project focused on command-line application development, cybercrime complaint workflows, and role-based complaint management.
