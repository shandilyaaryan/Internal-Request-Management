# Internal Request Management (IRM) System

A custom Frappe app for managing internal requests with an approval workflow that prevents self-approval.

## Table of Contents
- [Prerequisites](#prerequisites)
- [VM Setup](#vm-setup)
- [Frappe Installation](#frappe-installation)
- [App Installation](#app-installation)
- [Development Workflow](#development-workflow)
- [Testing the Workflow](#testing-the-workflow)
- [Key Features](#key-features)
- [Troubleshooting](#troubleshooting)

## Prerequisites
- Fresh Ubuntu VM (20.04 or later recommended)
- SSH access to the VM
- Basic command line knowledge

## VM Setup

### 1. Update System Packages
```bash
# SSH into your VM
ssh user@your-vm-ip

# Update packages
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Dependencies
```bash
# Install core dependencies
sudo apt install git redis-server libmariadb-dev mariadb-server mariadb-client pkg-config -y

# Install wkhtmltopdf dependencies
sudo apt install xvfb libfontconfig -y
```

### 3. Secure MariaDB Installation
```bash
sudo mariadb-secure-installation
```

**Important:** During MariaDB setup:
- Create a user named `frappe` with password `frappe`
- Using `root` user may cause permission issues
- Grant all privileges to the frappe user
```sql
# Run these in MariaDB console
sudo mariadb
CREATE USER 'frappe'@'localhost' IDENTIFIED BY 'frappe';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

## Frappe Installation

### 1. Install Node.js using NVM
```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Reload shell configuration
source ~/.bashrc

# Install Node.js 24
nvm install 24

# Install Yarn package manager
npm install -g yarn
# If permission denied, use: sudo npm install -g yarn
```

### 2. Install Python using UV
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell
source ~/.bashrc

# Install Python 3.14 and set as default
uv python install 3.14 --default
```

**Troubleshooting:** If UV installation fails:
```bash
# Create and activate a virtual environment first
python3 -m venv ~/frappe-env
source ~/frappe-env/bin/activate
# Then retry UV installation
```

### 3. Install Frappe Bench
```bash
uv tool install frappe-bench
```

### 4. Initialize Frappe Bench
```bash
# Initialize bench (this creates frappe-bench directory)
bench init frappe-bench

# Navigate to bench directory
cd frappe-bench

# Activate the virtual environment
source env/bin/activate
```

### 5. Create a New Site
```bash
bench new-site internal-req-mgmt.localhost
```

When prompted, enter the MariaDB credentials:
- MySQL root password: `frappe`
- Administrator password: (choose a strong password for the site admin)

**Note:** The site name uses underscores in the actual directory: `internal_req_mgmt.localhost`

## App Installation

### 1. Install UV in Virtual Environment (Required for bench new-app)
```bash
# Make sure you're in frappe-bench directory with env activated
pip install uv
```

### 2. Create the Custom App
```bash
bench new-app irm
```

When prompted:
- App Title: Internal Request Management
- App Description: Internal request management with approval workflow
- App Publisher: (your name/company)
- App Email: (your email)
- App License: MIT

### 3. Install the App on Your Site
```bash
bench --site internal_req_mgmt.localhost install-app irm
```

### 4. Set the Current Site
```bash
# Set default site to avoid typing --site flag repeatedly
bench use internal_req_mgmt.localhost
```

### 5. Enable Developer Mode
```bash
# Method 1: Using bench command
bench set-config -g developer_mode 1

# Method 2: Manually edit site_config.json
# Add this line to sites/internal_req_mgmt.localhost/site_config.json:
# "developer_mode": 1
```

### 6. Install Process Manager (if needed)
```bash
# If you get errors about missing process manager
pip install honcho
```

### 7. Start Bench
```bash
bench start
```

The site will be available at:
```
http://localhost:8000
```

Or if accessing remotely:
```
http://your-vm-ip:8000
```

## Development Workflow

### Starting Bench After SSH Reconnection

If you SSH into the VM again or bench processes are running, you need to clean up first:
```bash
# Navigate to bench directory
cd ~/frappe-bench

# Activate virtual environment
source env/bin/activate

# Kill old processes
sudo pkill redis-server

# Kill processes on port 8000
sudo lsof -i :8000
sudo kill -9 <process_ids>

# Kill remaining frappe and bench processes
sudo pkill -f frappe
sudo pkill -f bench

# Clear cache
bench clear-cache

# Start bench again
bench start
```

### Common Development Commands
```bash
# Clear cache after code changes
bench clear-cache

# Restart bench
bench restart

# Migrate database after schema changes
bench migrate

# Update app
bench update --reset

# View logs
bench --site internal_req_mgmt.localhost console
```

## Testing the Workflow

### Access the Site

1. Open browser and go to: `http://localhost:8000` (or `http://your-vm-ip:8000`)
2. Login with Administrator credentials created during site setup

### Create Test Users

Create two test users with different roles:

1. **Go to:** User List → New User

2. **Create Requester User:**
   - Email: `requester@test.com`
   - First Name: `Test`
   - Last Name: `Requester`
   - Password: `Test@123`
   - Role: `Requester`
   - Send Welcome Email: Unchecked

3. **Create Manager User:**
   - Email: `manager@test.com`
   - First Name: `Test`
   - Last Name: `Manager`
   - Password: `Test@123`
   - Roles: `Manager`, `Requester`
   - Send Welcome Email: Unchecked

4. **Create Dual-Role User (for self-approval test):**
   - Email: `hello@test.com`
   - First Name: `Hello`
   - Last Name: `Test`
   - Password: `Test@123`
   - Roles: `Requester`, `Manager` (both roles)
   - Send Welcome Email: Unchecked

### Test Scenario 1: Self-Approval Prevention (Critical Test)

This test verifies that the logical enforcement works.

1. **Login as user with both roles**
   - Email: `hello@test.com`
   - Password: `Test@123`

2. **Create a New Internal Request**
   - Go to: Internal Request list
   - Click: "New"
   - Fill in:
     - Title: "Test Self-Approval Prevention"
     - Description: "Testing workflow"
     - Other required fields
   - Notice: "Requested By" is automatically set to `hello@test.com`
   - Click: "Save"

3. **Submit the Request**
   - Click: "Submit" button
   - Status changes: Draft → Submitted

4. **Try to Approve Your Own Request**
   - Click: "Approve" button
   - **Expected Result:** ❌ Error message appears:
```
     You cannot approve or reject your own request.
```
   - This proves the logical enforcement is working!

5. **Try to Reject Your Own Request**
   - Click: "Reject" button
   - **Expected Result:** ❌ Same error message appears

### Test Scenario 2: Normal Approval Flow

This test verifies the normal workflow works correctly.

1. **Login as Requester**
   - Email: `requester@test.com`
   - Password: `Test@123`

2. **Create and Submit Request**
   - Create new Internal Request
   - Fill in details
   - Click "Save" then "Submit"
   - Logout

3. **Login as Manager**
   - Email: `manager@test.com`
   - Password: `Test@123`

4. **View and Approve Request**
   - Go to: Internal Request list
   - Open the request created by `requester@test.com`
   - Click: "Approve" button
   - **Expected Result:** ✅ Request status changes to "Approved"
   - Success! Manager can approve requests they didn't create

### Test Scenario 3: Rejection Flow

1. **Login as Requester and create another request**
2. **Login as Manager and reject it**
3. **Expected Result:** ✅ Request status changes to "Rejected"

## Key Features

### 1. Automatic Requester Assignment
- When a user creates a new Internal Request, the "Requested By" field is automatically set to the logged-in user
- Implemented in `before_insert` hook
- Prevents manual manipulation of requester field

**Code:**
```python
def before_insert(self):
    if not self.requested_by:
        self.requested_by = frappe.session.user
```

### 2. Self-Approval Prevention (Logical Enforcement)
- Users cannot approve or reject their own requests, even if they have both Requester and Manager roles
- This is **logically enforced** in the backend, not just through permissions
- Implemented in `on_update_after_submit` hook
- Raises a `PermissionError` if self-approval is attempted

**Code:**
```python
def on_update_after_submit(self):
    if self.workflow_state in ("Approved", "Rejected"):
        if self.requested_by == frappe.session.user:
            frappe.throw(
                "You cannot approve or reject your own request.",
                frappe.PermissionError
            )
```

### 3. Workflow States
- **Draft:** Initial state when request is created
- **Submitted:** Request has been submitted for approval
- **Approved:** Manager has approved the request
- **Rejected:** Manager has rejected the request

### 4. Role-Based Permissions
- **Requester:** Can create and view their own requests
- **Manager:** Can view all requests and approve/reject submitted requests

## Technical Implementation

### Backend Logic (Python)

**File:** `irm/irm/doctype/internal_request/internal_request.py`
```python
import frappe
from frappe.model.document import Document

class InternalRequest(Document):

    def before_insert(self):
        """
        Automatically set requested_by to logged-in user.
        Prevents users from creating requests on behalf of others.
        """
        if not self.requested_by:
            self.requested_by = frappe.session.user

    def on_update_after_submit(self):
        """
        Prevent users from approving/rejecting their own requests,
        even if they have both Requester and Manager roles.
        
        This hook fires when a submitted document is updated,
        which includes workflow state changes.
        """
        if self.workflow_state in ("Approved", "Rejected"):
            if self.requested_by == frappe.session.user:
                frappe.throw(
                    "You cannot approve or reject your own request.",
                    frappe.PermissionError
                )
```

### Why `on_update_after_submit`?

During development and testing, we discovered that:

1. **`validate` hook** - Fires on create and submit, but **NOT** on workflow state changes for submitted documents
2. **`before_workflow_action` hook** - Should work in theory, but doesn't fire reliably in practice
3. **`on_update_after_submit` hook** - ✅ The correct hook that fires whenever a submitted document is updated, including workflow state changes

### DocType Fields

The Internal Request DocType includes:

| Field Name | Field Type | Options | Required | Description |
|------------|-----------|---------|----------|-------------|
| title | Data | - | Yes | Request title/subject |
| description | Text Editor | - | No | Detailed description |
| request_category | Select | - | No | Category/type of request |
| priority | Select | Low/Medium/High | Yes | Request priority |
| workflow_state | Link | Workflow State | - | Current state in workflow |
| requested_by | Link | User | Yes | User who created request |
| approved_by | Link | User | No | User who approved/rejected |
| created_on | Datetime | - | Auto | Creation timestamp |

## Troubleshooting

### Issue 1: `before_workflow_action` Hook Not Firing

**Problem:** The standard `before_workflow_action` hook doesn't reliably fire for workflow state changes on submitted documents.

**Solution:** Use `on_update_after_submit` hook instead, which fires whenever a submitted document is updated (including workflow state changes).

### Issue 2: MariaDB Root User Permission Issues

**Problem:** Using MariaDB root user can cause "Access denied" errors during bench setup.

**Solution:** Create a dedicated `frappe` user with full privileges as shown in the setup steps.

### Issue 3: Port 8000 Already in Use

**Problem:** Error message: "Address already in use" when running `bench start`.

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or kill all bench/frappe processes
sudo pkill -f bench
sudo pkill -f frappe
```

### Issue 4: Redis Connection Errors

**Problem:** Redis connection refused errors.

**Solution:**
```bash
# Kill old redis processes
sudo pkill redis-server

# Start bench again
bench start
```

### Issue 5: UV Not Found When Creating App

**Problem:** `bench new-app` fails with UV not found error.

**Solution:**
```bash
# Install UV in the virtual environment
source env/bin/activate
pip install uv
```

### Issue 6: Honcho Not Found

**Problem:** Error about missing process manager when running `bench start`.

**Solution:**
```bash
pip install honcho
```

### Issue 7: Changes Not Reflecting

**Problem:** Code changes not showing up in the browser.

**Solution:**
```bash
# Clear cache
bench clear-cache

# Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

# If still not working, restart bench
bench restart
```

## Design Decisions

### 1. Self-Approval Check in Backend vs Permissions

**Decision:** Implement self-approval prevention in `on_update_after_submit` hook rather than relying solely on permissions.

**Rationale:**
- Permissions alone cannot prevent users with multiple roles from approving their own requests
- A user with both Requester and Manager roles would bypass permission-based restrictions
- Backend validation ensures the rule is enforced regardless of permission configuration
- Provides a single source of truth for this business rule

### 2. Automatic Requester Assignment

**Decision:** Automatically set `requested_by` field in `before_insert` hook.

**Rationale:**
- Reduces user error and ensures data consistency
- User cannot accidentally or maliciously assign request to someone else
- Simplifies the user interface (one less field to fill)
- Creates an audit trail of who actually created each request

### 3. Using Frappe Workflow vs Custom Status Field

**Decision:** Use Frappe's built-in Workflow engine instead of a custom status field.

**Rationale:**
- Leverages Frappe's workflow engine for state management
- Provides audit trail and transition history out of the box
- Enforces allowed state transitions automatically
- Integrates with Frappe's permission system
- No need to write custom transition logic

### 4. Hook Selection: `on_update_after_submit`

**Decision:** Use `on_update_after_submit` instead of `before_workflow_action` or `validate`.

**Rationale:**
- `validate` doesn't fire on workflow state changes for submitted documents
- `before_workflow_action` doesn't fire reliably in all Frappe versions
- `on_update_after_submit` consistently fires for any update to submitted documents
- Catches all workflow state transitions (Approved, Rejected)

## Production Deployment (Optional)

For production deployment, consider these additional steps:

### 1. Setup Supervisor for Process Management
```bash
bench setup supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
```

### 2. Setup Nginx as Reverse Proxy
```bash
bench setup nginx
sudo service nginx reload
```

### 3. Enable Production Mode
```bash
# Disable developer mode
bench set-config -g developer_mode 0

# Enable scheduler for background jobs
bench --site internal_req_mgmt.localhost enable-scheduler

# Turn off maintenance mode
bench --site internal_req_mgmt.localhost set-maintenance-mode off
```

### 4. Setup SSL (Optional)
```bash
# Using Let's Encrypt
sudo bench setup lets-encrypt internal-req-mgmt.localhost
```

## Assumptions and Limitations

### Assumptions
1. Single-site deployment on the VM
2. MariaDB and Redis running on the same server
3. Users have email addresses for login
4. Basic approval workflow (no multi-level approvals)

### Known Limitations
1. **No email notifications** - Currently no email alerts when requests are submitted/approved
2. **Single approver** - Only one manager can approve, no multi-stage approval
3. **No request delegation** - Users cannot reassign requests to others
4. **No comments/notes** - No communication thread within the request

### Potential Enhancements
- Email notifications on state changes
- Comments/discussion thread

## Support & Resources

### Official Documentation
- [Frappe Framework Docs](https://frappeframework.com/docs)
- [Frappe Forum](https://discuss.frappe.io/)
- [Frappe GitHub](https://github.com/frappe/frappe)

### Key Concepts to Understand
- [DocTypes](https://frappeframework.com/docs/user/en/basics/doctypes)
- [Workflows](https://frappeframework.com/docs/user/en/desk/workflows)
- [Hooks](https://frappeframework.com/docs/user/en/basics/hooks)
- [Controllers](https://frappeframework.com/docs/user/en/api/model)
- [Permissions](https://frappeframework.com/docs/user/en/desk/role-based-permissions)

## Lessons Learned

1. **Document Hooks Behavior** - Different hooks fire at different stages of the document lifecycle. Understanding when each hook fires is crucial for implementing business logic correctly.

2. **Workflow State Changes** - Workflow actions on submitted documents require special handling with `on_update_after_submit` rather than standard validation hooks.

3. **Permission vs Logic Enforcement** - Critical business rules should be enforced in code, not just through permissions, especially when dealing with users who have multiple roles.

4. **MariaDB User Setup** - Using a dedicated database user (`frappe`) instead of root prevents permission issues during development.

5. **Process Management** - Proper cleanup of old processes is essential when reconnecting to development environments via SSH.

## License

This project is licensed under the MIT License.

---

**Author:** Aryan Shandilya  
**Created:** January 2026  
**Assignment:** Frappe Custom App Development  
**Frappe Version:** 15  
**Python Version:** 3.14  
**Node Version:** 24  
**Database:** MariaDB 10.x
