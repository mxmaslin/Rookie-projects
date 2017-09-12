import re
from django.http import HttpResponse

from rentcrm.models import Contract, Tenant

def format_phone_numbers(request):
    tenants = Tenant.objects.all()
    for t in tenants:
        t.phone = re.sub(r"\D", "", t.phone)
        t.save(update_fields=['phone'])
    return HttpResponse('Formatted %d phones!' % len(tenants))


def clear_lease_end(request):
    if request.GET.get('yes'):
        inactive = Contract.objects.filter(is_active=False).count()
        all_contracts = Contract.objects.all().count()
        updated = Contract.objects.filter(is_active=True).update(lease_end=None)
        return HttpResponse('All contracts: %s, inactive: %s, updated: %s' \
            % (all_contracts, inactive, updated))
    else:
        return HttpResponse('Please confirm')
