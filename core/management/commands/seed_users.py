import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ProfileHR
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Generate 100 test users with ProfileHR'

    def handle(self, *args, **kwargs):
        first_names = ['An', 'Bình', 'Chi', 'Dũng', 'Em', 'Hạnh', 'Khang', 'Linh', 'Minh', 'Nam', 'Oanh', 'Phúc', 'Quân', 'Sơn', 'Tuấn', 'Vinh']
        last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô']

        created_count = 0
        for i in range(100):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{last_name} {first_name}"
            
            # Generate unique username
            base_username = slugify(full_name).replace('-', '.')
            username = f"{base_username}.{random.randint(1000, 9999)}"
            
            # Ensure uniqueness
            while User.objects.filter(username=username).exists():
                username = f"{base_username}.{random.randint(1000, 9999)}"

            email = f"{username}@example.com"
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name
                )
                
                # ProfileHR creation (avoiding duplicates if signal exists)
                ProfileHR.objects.get_or_create(
                    user=user,
                    defaults={
                        'full_name': full_name,
                        'employee_code': f"EMP{random.randint(100000, 999999)}",
                        'gender': random.choice(['Male', 'Female', 'Other']),
                        'phone': f"09{random.randint(10000000, 99999999)}",
                        'status': 0  # Working
                    }
                )
                created_count += 1
                if created_count % 10 == 0:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} users'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {i}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'FINISHED: Created {created_count} users with ProfileHR'))
