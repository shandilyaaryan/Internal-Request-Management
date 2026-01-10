# Internal Request Management – Frappe App

This repository contains a custom Frappe application built as part of an internal request management system assignment. The goal of the project was to understand Frappe fundamentals (apps, DocTypes, workflows, roles, permissions) and deliver a working end‑to‑end setup that can be reproduced on a fresh machine.

---

## High Level VM Setup

The project was developed and tested on a fresh Ubuntu virtual machine. A full, reproducible setup guide is provided in the **Installing This App on a Fresh VM** section below.

---

## Frappe Installation

Frappe was installed using **bench** as per the official documentation. The exact commands and environment setup are documented in the **Installing This App on a Fresh VM** section below.

---

## 3. Custom App Creation

A custom Frappe app was created to ensure all functionality lives outside the core Frappe app.

Steps:

```bash
bench new-app irm
```

The app was then installed on the site:

```bash
bench --site internal_req_mgmt.localhost install-app irm
```

All DocTypes, workflows, permissions, and server‑side logic are implemented inside this custom app. No manual site‑level changes are required.

---

## Installing the App on a New Site

The IRM app is designed to be installed on any Frappe site using standard `bench install-app` commands. A complete step‑by‑step installation guide is included later in this README.

---

## 5. Testing the Workflow

### Roles

Two main roles are used:

* **Requester** – creates and submits requests
* **Manager** – approves or rejects requests

### Users

Create at least two users:

* One user with `Requester` role
* One user with `Manager` role

### Workflow States

* Draft
* Submitted
* Approved
* Rejected

### Testing Steps

1. Login as **Requester**

   * Create a new Internal Request
   * Submit the request

2. Login as **Manager**

   * View submitted requests
   * Approve or reject requests

3. Validation Check

   * A user cannot approve their own request (enforced server‑side)
   * Workflow transitions cannot be bypassed using permissions

---

## 6. Server‑Side Logic

The following logic is implemented using DocType hooks:

* `Requested By` is automatically set to the logged‑in user on creation
* Self‑approval is blocked during validation
* Workflow actions are enforced at the backend, not just via UI permissions

---

## 7. Assumptions, Shortcuts, and Limitations

* This setup is intended for development/testing, not production
* Supervisor and Nginx were not configured (optional per assignment)
* Email setup was skipped; passwords were set manually for test users
* UI customization was kept minimal to focus on backend correctness
* Error handling is basic but sufficient for the assignment scope

---

## 8. Credentials (for Testing)

* **Requester User**: provided separately
* **Manager User**: provided separately

---

## Notes

This project was treated as a real‑world learning exercise rather than a tutorial follow‑along. Design decisions were made to keep the app simple, clean, and aligned with Frappe best practices while meeting all assignment requirements.

## VM Setup & Reproducible Installation (Using bench get-app)

This section explains how to install and run the **Internal Request Management (IRM)** app on a brand new Ubuntu virtual machine in a fully reproducible way, using standard Frappe and Bench commands.

### 1. Provision a Fresh VM

* OS: **Ubuntu 20.04+**
* Ensure the VM has:

  * Internet access
  * SSH access
  * At least **2 GB RAM** (4 GB recommended)

SSH into the VM:

```bash
ssh user@<vm-ip>
```

---

### 2. System Dependencies

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  git redis-server mariadb-server mariadb-client \
  libmariadb-dev pkg-config xvfb libfontconfig
```

Secure MariaDB and create a dedicated `frappe` user:

```bash
sudo mariadb-secure-installation
```

Inside MariaDB:

```sql
CREATE USER 'frappe'@'localhost' IDENTIFIED BY 'frappe';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

---

### 3. Install Node.js, Python, and Bench

#### Node.js (via NVM)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc

nvm install 24
npm install -g yarn
```

#### Python (via UV)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

uv python install 3.14 --default
```

#### Install Bench

```bash
uv tool install frappe-bench
```

---

### 4. Initialize Bench and Create Site

```bash
bench init frappe-bench
cd frappe-bench
source env/bin/activate
```

Create a new site:

```bash
bench new-site internal_req_mgmt.localhost
```

* MariaDB username: `frappe`
* MariaDB password: `frappe`
* Set Administrator password as prompted

---

### 5. Fetch and Install the IRM App (bench get-app)

From inside the bench directory:

```bash
bench get-app https://github.com/shandilyaaryan/Internal-Request-Management

bench --site internal_req_mgmt.localhost install-app irm

bench migrate

bench use internal_req_mgmt.localhost

bench set-config -g developer_mode 1
```

---

### 6. Start the Application

```bash
bench start
```

Open the browser:

```
http://<vm-ip>:8000
```

If the setup wizard UI appears broken (known dev issue), skip it:

```bash
bench --site internal_req_mgmt.localhost set-config setup_complete 1
bench restart
```

Then go directly to:

```
http://<vm-ip>:8000/desk
```

---

### 7. Final Verification

* Log in as **Administrator**
* Confirm:

  * `Internal Request` DocType exists
  * Workflow actions (Submit / Approve / Reject) are visible
  * Roles (`Requester`, `Manager`) are present
  * Self-approval is blocked correctly

At this point, the app is fully installed and functional on a new VM.
