import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gateadvisor.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = "admin"
password = "Neeraj@123"
email = "admin@gateadvisor.demo"

try:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Admin '{username}' successfully created.")
    else:
        # Just update the password to be sure
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Admin '{username}' already exists. Password updated.")
except Exception as e:
    print(f"Error seeding admin: {e}")
