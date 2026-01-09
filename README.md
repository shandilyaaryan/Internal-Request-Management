# Internal Request Management – Frappe App

This project is a custom Frappe application built as part of a take‑home assignment to demonstrate the ability to learn and apply Frappe Framework concepts correctly.

The app implements an **Internal Request Management System** with DocTypes, workflows, roles, permissions, and server‑side validations.

---

## 1. High‑Level Overview

Employees can create internal requests (IT, HR, Admin, etc.).
Each request follows an approval workflow enforced using:

* Frappe Workflows
* Role‑based permissions
* Server‑side Python logic

Key guarantees:

* Any logged‑in user can create and submit a request
* Only Managers can approve or reject
* A user cannot approve their own request

---

## 2. Infrastructure Setup

* OS: Ubuntu (fresh VM)
* Database: MariaDB
* Cache / Queue: Redis
* Framework: Frappe
* Tooling: Bench

### Bench Installation

```bash
bench init frappe-bench
cd frappe-bench
bench new-site internal_req_mgmt.localhost
bench start
```

The site is accessed in the browser via port forwarding to `localhost:8000`.

---

## 3. Custom App Creation

```bash
bench new-app irm
bench --site internal_req_mgmt.localhost install-app irm
```

All functionality lives inside the **irm** app. No manual site‑level changes were made.

---

## 4. DocType: Internal Request

**DocType Name:** Internal Request
**Module:** Internal Request Management

### Fields

| Field          | Type        | Notes               |
| -------------- | ----------- | ------------------- |
| Subject        | Data        | Required            |
| Description    | Text Editor | Required            |
| Request Type   | Select      | IT / HR / Admin     |
| Priority       | Select      | Low / Medium / High |
| Workflow State | Data        | Managed by workflow |
| Requested By   | Link (User) | Auto‑set            |
| Approved By    | Link (User) | Set on approval     |
| Creation       | Datetime    | System generated    |

Defaults and validations are applied where applicable.

---

## 5. Workflow

### States

1. Draft
2. Submitted
3. Approved
4. Rejected

### Rules

* Draft → Submitted: Any logged‑in user
* Submitted → Approved: Manager only
* Submitted → Rejected: Manager only

Self‑approval is blocked at the server level.

---

## 6. Roles & Permissions

### Roles

* Requester
* Manager

### Permission Logic

| Role          | Access                            |
| ------------- | --------------------------------- |
| Requester     | Create and view own requests      |
| Manager       | View all requests, approve/reject |
| Administrator | Full access                       |

Workflow permissions prevent bypassing approval logic.

---

## 7. Server‑Side Logic

Implemented using DocType controller hooks.

Features:

* Auto‑set `requested_by` on creation
* Prevent self‑approval during validation
* Set `approved_by` on approval

Logic is enforced in Python, not only via UI restrictions.

---

## 8. Testing the Workflow

### Test Users

**Requester**

* Email: [requester@test.com](mailto:requester@test.com)
* Role: Requester

**Manager**

* Email: [manager@test.com](mailto:manager@test.com)
* Role: Manager

### Test Steps

1. Login as Requester
2. Create and submit a request
3. Login as Manager
4. Approve or reject the request
5. Attempt self‑approval (blocked)

---

## 9. Notes & Limitations

* Production nginx/supervisor setup is optional and not enabled
* UI kept minimal; focus is on correctness and backend enforcement

---

## 10. Submission Contents

* Custom Frappe App (`irm`)
* DocType definitions
* Workflow configuration
* Roles & permissions
* Server‑side Python logic
* This README
