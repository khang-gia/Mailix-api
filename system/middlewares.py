from system.permissions import AclPermission

class PermissionMiddleware:
    """
    Automatically applies AclPermission to all API views except:
    - Authentication endpoints
    - Profile endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Exempt certain paths
        exempt_paths = [
            '/api/v1/auth',
            '/api/v1/core/profile',
            '/api/v1/core/users/me',
        ]
        
        is_exempt = any(request.path.startswith(path) for path in exempt_paths)
        
        if is_exempt:
            # Remove AclPermission if present
            if hasattr(view_func, 'cls') and hasattr(view_func.cls, 'permission_classes'):
                if AclPermission in view_func.cls.permission_classes:
                    view_func.cls.permission_classes.remove(AclPermission)
        else:
            # Add AclPermission
            if hasattr(view_func, 'cls'):
                if hasattr(view_func.cls, 'permission_classes'):
                    if AclPermission not in view_func.cls.permission_classes:
                        view_func.cls.permission_classes.append(AclPermission)
                else:
                    view_func.cls.permission_classes = [AclPermission]
        
        return None
