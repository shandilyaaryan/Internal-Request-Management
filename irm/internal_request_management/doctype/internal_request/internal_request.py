import frappe
from frappe.model.document import Document

class InternalRequest(Document):

    def validate(self):
        # Only run on existing docs
        if not self._doc_before_save:
            return

        old_state = self._doc_before_save.workflow_state
        new_state = self.workflow_state

        # Detect approval / rejection transition
        if old_state != new_state and new_state in ("Approved", "Rejected"):
            if self.requested_by == frappe.session.user:
                frappe.throw(
                    "You cannot approve or reject your own request.",
                    frappe.PermissionError
                )

