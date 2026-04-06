"""
WSGI config for writespace project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Ensure the writespace project directory is on sys.path so that app imports
# (e.g., blog, accounts) resolve correctly in deployment environments like Vercel.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writespace.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# Cold-start setup: run collectstatic, migrate, and create_default_admin
# These are safe to run repeatedly (idempotent).
from django.core.management import call_command  # noqa: E402

try:
    call_command('collectstatic', '--noinput')
except Exception:
    pass

try:
    call_command('migrate', '--noinput')
except Exception:
    pass

try:
    call_command('create_default_admin')
except Exception:
    pass

# Expose ``app`` for Vercel's Python runtime.
app = application