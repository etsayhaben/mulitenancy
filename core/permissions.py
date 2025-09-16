# core/permissions.py
from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """
    Generic permission: set required_permission in subclass.
    """
    required_permission = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if self.required_permission is None:
            return True
        return request.user.has_perm(self.required_permission)


# Shortcut classes
class CanViewFinancialReports(HasPermission):
    required_permission = "core.can_view_financial_reports"

class CanProcessPayments(HasPermission):
    required_permission = "core.can_process_payments"

class CanManageUsers(HasPermission):
    required_permission = "core.can_manage_users"
# core/permissions.py (add this)

from rest_framework.permissions import BasePermission
import logging

audit_logger = logging.getLogger('audit.permissions')

class HasContextualPermission(BasePermission):
    """
    Enhanced permission class supporting:
    - Object-level checks
    - Contextual logic (ABAC)
    - Audit logging
    """
    required_permission = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if self.required_permission is None:
            return True
        return request.user.has_perm(self.required_permission)

    def has_object_permission(self, request, view, obj):
        """
        Override this for contextual logic.
        Default: fall back to has_permission.
        """
        return self.has_permission(request, view)

    def _log_check(self, request, obj, allowed, reason=""):
        user_id = request.user.id if request.user.is_authenticated else "anonymous"
        resource_type = obj.__class__.__name__ if obj else "n/a"
        resource_id = getattr(obj, 'id', 'n/a') if obj else 'n/a'
        action = self.__class__.__name__

        audit_logger.info(
            "Permission check",
            extra={
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "allowed": allowed,
                "reason": reason,
            }
        )

# Example: Contextual Bill Approval
class CanApproveBill(HasContextualPermission):
    required_permission = "core.can_approve_bill"  # ← Add this to CUSTOM_PERMISSIONS

    def has_object_permission(self, request, view, obj):
        # obj = Bill instance
        base_perm = super().has_object_permission(request, view, obj)
        if not base_perm:
            self._log_check(request, obj, False, "Missing base permission")
            return False

        # Contextual rule: amount-based escalation
        if obj.amount > 10000:
            allowed = request.user.has_role("superadmin") or request.user.has_role("admin")
            reason = "High amount — requires admin/superadmin" if allowed else "Insufficient role for high amount"
        else:
            allowed = request.user.has_role("accountant") or request.user.has_role("admin")
            reason = "Standard approval" if allowed else "Not authorized for approval"

        self._log_check(request, obj, allowed, reason)
        return allowed