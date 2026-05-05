from django.conf import settings
from rest_framework.test import APIClient
from django.contrib.auth.models import User
client = APIClient()
user = User.objects.first()
client.force_authenticate(user=user)
res = client.get('/api/v1/system/admin-config/')
print("STATUS:", res.status_code)
print("DATA:", res.data)
