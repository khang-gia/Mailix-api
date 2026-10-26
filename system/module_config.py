# Module definitions and URL pattern mappings
# This file defines which API endpoints belong to which modules.
#
# IMPORTANT: The module codes here MUST match:
#   - Department.resources SystemResource codes  (sidebar view lock)
#   - Company.enabled_modules list values        (company-level feature flags)
# This alignment means no translation layer is needed between the two systems.

MODULE_URL_MAP = {
    'hrm': [
        '/api/v1/core/profile_hr/',
        '/api/v1/core/employees/',
        '/api/v1/timekeeping/',
    ],
    'crm': [
        '/api/v1/core/customers/',
        '/api/v1/core/contacts/',
        '/api/v1/consult/',
    ],
    'workspace': [
        '/api/v1/core/works/',
        '/api/v1/social/',
    ],
    # 'company'    → admin/system routes, no module URL restriction
    # 'guide_mail' → static guide pages, no API URLs to restrict
    # 'guide_app'  → static guide pages, no API URLs to restrict
}

def get_module_from_url(url):
    """
    Determine which module a URL belongs to.
    Returns the module code (e.g. 'hrm', 'crm') or None if the URL
    doesn't belong to any gated module.
    """
    for module_code, url_patterns in MODULE_URL_MAP.items():
        for pattern in url_patterns:
            if url.startswith(pattern):
                return module_code
    return None

def get_company_from_user(user):
    """
    Get the company associated with a user.
    Lookup path: User → ProfileHR → Department → Company
    """
    if hasattr(user, 'profile_hr') and user.profile_hr:
        if user.profile_hr.department and user.profile_hr.department.company:
            return user.profile_hr.department.company
    return None
