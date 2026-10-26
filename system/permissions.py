from rest_framework.permissions import BasePermission
from system.models import Permission
from system.module_config import get_module_from_url, get_company_from_user

class AclPermission(BasePermission):
    """
    Custom permission class for granular API access control.
    
    Permission Strategy: UNION (Most Permissive)
    - Users inherit permissions from ALL their groups
    - Individual group permissions + Department group permissions
    - Access granted if ANY group allows it
    
    Checks:
    1. User's groups (individual + department) have permission for requested resource+action
    2. User's company has access to the module (if applicable)
    """
    
    def has_permission(self, request, view):
        user = request.user
        
        # Superusers bypass all checks
        if user.is_superuser:
            return True
        
        # System admins bypass all checks
        if hasattr(user, 'profile') and user.profile.is_system_admin:
            return True
        
        # Extract action from view
        action = self._extract_action(view, request)
        
        # Check module access first (if URL belongs to a specific module)
        if not self._check_module_access(user, request.path):
            return False
        
        # Collect all groups this user belongs to
        groups = self._get_user_groups(user)
        
        if not groups:
            return False
        
        # Check if ANY of the user's groups has permission (UNION strategy)
        return self._check_permission_for_groups(groups, request.path, action)
    
    def _get_user_groups(self, user):
        """
        Collect all group IDs that this user belongs to.
        Returns a list of group IDs from:
        1. Individual user group (Profile.group)
        2. Individual user group (ProfileHR.group)
        3. Department group (ProfileHR.department.group)
        """
        groups = []
        
        if user.is_anonymous:
            return groups
        
        try:
            # 1. Individual group from Profile (regular users)
            if hasattr(user, 'profile') and user.profile and user.profile.group:
                groups.append(user.profile.group.id)
        except Exception:
            pass  # Profile doesn't exist or no group
        
        try:
            # 2. Individual group from ProfileHR (HR module users)
            if hasattr(user, 'profile_hr') and user.profile_hr:
                # Individual HR group
                if user.profile_hr.group:
                    groups.append(user.profile_hr.group.id)
                
                # 3. Department group (shared by all users in the department)
                if user.profile_hr.department and user.profile_hr.department.group:
                    groups.append(user.profile_hr.department.group.id)
        except Exception:
            pass  # ProfileHR doesn't exist or no department/group
        
        # Remove duplicates (in case same group is assigned multiple ways)
        return list(set(groups))
    
    def _check_module_access(self, user, url):
        """
        Check if the user is allowed to access the module required by this URL.

        Two checks run in order:
        1. Company module check (company.enabled_modules) — billing-level gate.
        2. Department resource check (dept.resources codes) — org-level gate.

        Returns True only if BOTH checks pass (or the URL has no module mapping).
        """
        module_code = get_module_from_url(url)

        # If URL doesn't map to a specific module, allow access
        if not module_code:
            return True

        # --- Check 1: Company must have this module enabled ---
        company = get_company_from_user(user)
        if company and not company.has_module(module_code):
            return False

        # --- Check 2 (NEW): User's department must include this module in its resources ---
        # This enforces the sidebar view-lock at the API level, preventing users
        # from bypassing the frontend gate by calling API URLs directly.
        dept_resource_codes = self._get_dept_resource_codes(user)
        if dept_resource_codes is not None:
            # dept_resource_codes is None only when no dept restriction applies
            # (e.g. user has no dept set — graceful degradation)
            if module_code not in dept_resource_codes:
                return False

        return True

    def _get_dept_resource_codes(self, user):
        """
        Return the list of SystemResource codes the user's department allows.

        Priority order:
        1. Department.resources (directly assigned resources)
        2. Department.group.resources (inherited from dept's SystemGroup)

        Returns None when no restriction applies (graceful degradation):
        - User has no profile_hr
        - User has no department
        - Department has no resources AND no group with resources
        """
        try:
            profile_hr = getattr(user, 'profile_hr', None)
            if not profile_hr:
                return None

            dept = profile_hr.department
            if not dept:
                return None

            # Direct resources on the department
            codes = list(dept.resources.values_list('code', flat=True))
            if codes:
                return codes

            # Fallback: inherit from the department's assigned SystemGroup
            if dept.group:
                codes = list(dept.group.resources.values_list('code', flat=True))
                if codes:
                    return codes

        except Exception:
            pass

        # No restriction found — allow access (graceful degradation)
        return None

    def _extract_action(self, view, request):
        """Extract action from view or request"""
        if hasattr(view, 'action'):
            return view.action
        else:
            # Parse from URL
            url = request.path.rstrip('/')
            parts = url.split('/')
            if len(parts) > 0:
                return parts[-1]
            return request.method.lower()
    
    def _check_permission_for_groups(self, group_ids, url, action):
        """
        Check if ANY of the provided groups has permission for url + action.
        This implements the UNION strategy (most permissive).
        """
        import re
        
        # Extract API pattern from URL
        # Example: /api/v1/core/customers/ → /api/v1/core/customers/
        pattern = r'(\/api\/v\d+\/\w+\/\w+)+'
        match = re.search(pattern, url)
        
        if not match:
            return False
        
        api_url = match.group() + '/'
        
        # Query Permission table - check if ANY group has access
        permissions = Permission.objects.filter(
            status=True,
            group_id__in=group_ids,  # Check all user's groups
            resource__url=api_url,
            resource__action__iexact=action
        )
        
        return permissions.exists()
