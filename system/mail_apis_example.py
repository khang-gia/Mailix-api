"""
Example usage of mail_apis module

Before using, make sure to configure in Django admin:
1. Go to /admin/constance/config/
2. Set MAIL_SERVER_URL to: https://uat.mailix.vn/mail
3. Set MAIL_SERVER_TOKEN to your API token
"""

from system.mail_apis import (
    create_mail_user,
    get_mail_user,
    list_mail_users,
    update_mail_user_password,
    delete_mail_user
)

# Example 1: Create a new mail user
def example_create_user():
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "refId": "550e8400-e29b-41d4-a716-446655440000",  # Example UUID
        "role": "USER",
        "active": True
    }
    
    success, response = create_mail_user(data)
    if success:
        print(f"✅ User created successfully: {response}")
    else:
        print(f"❌ Failed to create user: {response}")


# Example 2: Get user details
def example_get_user():
    email = "newuser@example.com"
    
    user = get_mail_user(email)
    if user:
        print(f"✅ User details: {user}")
    else:
        print(f"❌ User not found")


# Example 3: List all users
def example_list_users():
    users = list_mail_users()
    print(f"📋 Total users: {len(users)}")
    for user in users:
        print(f"  - {user}")


# Example 4: Update user password
def example_update_password():
    email = "newuser@example.com"
    new_password = "NewSecurePassword456!"
    
    success, response = update_mail_user_password(email, new_password)
    if success:
        print(f"✅ Password updated successfully: {response}")
    else:
        print(f"❌ Failed to update password: {response}")


# Example 5: Delete user
def example_delete_user():
    email = "newuser@example.com"
    
    success, response = delete_mail_user(email)
    if success:
        print(f"✅ User deleted successfully: {response}")
    else:
        print(f"❌ Failed to delete user: {response}")


# Usage in your views.py (like in core/views.py create_account action):
"""
from system.mail_apis import create_mail_user

@action(detail=True, methods=['post'])
def create_account(self, request, pk=None):
    profile_hr = self.get_object()
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    
    # Create mail account using custom mail server
    mail_data = {
        "username": username,
        "email": email,
        "password": password,
        "refId": profile_hr.ref_uuid,
        "role": "USER",
        "active": True
    }
    success, response = create_mail_user(mail_data)
    if not success:
        return Response({'detail': f'Cannot create email account: {response}'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Continue with user creation...
"""
