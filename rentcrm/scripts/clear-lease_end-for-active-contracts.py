import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

from rentcrm.models import Contract
print('Inactive contracts:', Contract.objects.filter(is_active=False))
print('All contracts:', len(Contract.objects.all()))
print('Updated:', Contract.objects.filter(is_active=True).update(lease_end=None))
