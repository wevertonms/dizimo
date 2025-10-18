#!/bin/bash
set -e

python manage.py migrate

# Create admin user if it doesn't exist
python << END
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dizimo.settings")
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = "admin"
password = os.environ.get("ADMIN_PASSWORD", "admin123")
email = "admin@example.com"
user = User.objects.filter(username=username)
if not user.exists():
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    user = user.first()
    user.set_password(password)
    user.save()
END

exec "$@"
