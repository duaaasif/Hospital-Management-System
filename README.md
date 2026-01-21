# Hospital-Management-System

## Project Overview

A comprehensive hospital management system implementing the **CIA Triad** (Confidentiality, Integrity, Availability) with full **GDPR Article 5** compliance. Inspired by RSA Conference 2024 presentation on data privacy evolution.

### Key Features

- **Confidentiality**: bcrypt password hashing, Fernet encryption, data masking
- **Integrity**: Comprehensive audit logging, database constraints, RBAC
- **Availability**: Error handling, CSV exports, session management
- **GDPR Compliance**: Consent banner, data retention, pseudonymisation
- **Bonus Features**: Real-time activity graphs, automated data deletion

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
git clone https://github.com/YOUR_USERNAME/hospital-management-system.git
cd hospital-management-system


2. **Create virtual environment**
Windows
python -m venv venv
venv\Scripts\activate

3. **Install dependencies**
pip install -r requirements.txt

4. **Run the application**
streamlit run app.py

5. **Access the app**
Open browser at: http://localhost:8501

##  Default Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| **Admin** | `admin` | `admin123` | Full system access, raw data, audit logs |
| **Doctor** | `dr_bob` | `doc123` | Anonymized patient data only |
| **Receptionist** | `alice_recep` | `rec123` | Add/edit patients, no viewing |

## 🛡️ CIA Triad Implementation

### Confidentiality
- **bcrypt** password hashing with salt
- **Fernet** (AES-128) encryption for reversible anonymization
- Data masking: `ANON_xxxx`, `XXX-XXX-4592`
- Role-based access control (RBAC)
- 30-minute session timeout

### Integrity
- Comprehensive audit logging (all actions tracked)
- Database constraints: `CHECK`, `FOREIGN KEY`
- `PRAGMA foreign_keys=ON` enforcement
- Input validation and sanitization
- Admin-only audit log access

### Availability
- Try-except error handling on all operations
- CSV export for data backup/recovery
- Uptime monitoring and display
- Graceful degradation on failures

## Testing

Run the application and test all roles:

1. Login as **Admin** → View raw data, trigger anonymization, check audit logs
2. Login as **Doctor** → Verify only anonymized data visible
3. Login as **Receptionist** → Add patient, verify cannot view records
4. Wait 30 minutes → Verify session timeout
5. Settings page → Test data retention deletion

