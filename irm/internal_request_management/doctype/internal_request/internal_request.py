import frappe
from frappe.model.document import Document

class InternalRequest(Document):

    def before_insert(self):
        # Always set requested_by to logged-in user
        if not self.requested_by:
            self.requested_by = frappe.session.user

    def on_update_after_submit(self):
        """
        Prevent users from approving/rejecting their own requests,
        even if they have both Requester and Manager roles.
        """
        if self.workflow_state in ("Approved", "Rejected"):
            if self.requested_by == frappe.session.user:
                frappe.throw(
                    "You cannot approve or reject your own request.",
                    frappe.PermissionError
                )
