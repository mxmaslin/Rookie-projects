from calendar import monthrange
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db.models import F, Q

from .models import *
from .forms import *


# Apartments list filter - top navigation

@login_required
def index(request):
    apartments = Apartment.objects.all().select_related('building')
    return render(request, 'rentcrm/index.html', {'apartments': apartments})


@login_required
def free(request):
    free_apartments = Apartment.objects.exclude(contract__is_active=True)
    return render(request, 'rentcrm/free.html', {'apartments': free_apartments})


@login_required
def moving_out(request):
    apartments = Apartment.objects.filter(
        contract__is_active=True
    ).filter(
        Q(contract__contractcondition__leaserenewaloffer__tenant_choice=0)|
        ~Q(contract__lease_end=None)
    ).distinct()
    # Apartment with overdue rent
    # Q(contract__contractcondition__lease_end__lte=timezone.now())
    return render(request, 'rentcrm/moving-out.html', {'apartments': apartments})


@login_required
def debitors(request):
    apartments = []
    leases = Contract.objects.filter(is_active=True)
    for lease in leases:
        if lease.balance < 0:
            apartments.append(lease.apartment)
    return render(request, 'rentcrm/debitors.html', {'apartments': apartments})


@login_required
def renewal_required(request):
    now = timezone.now()
    renew_term_apartments = Apartment.objects.filter(
            contract__is_active=True,
            contract__contractcondition__lease_end__lt=now + timedelta(days=120),
            contract__contractcondition__leaserenewaloffer=None
        )
    return render(request, 'rentcrm/renewal-required.html', {'apartments': renew_term_apartments})


@login_required
def renewal_sent(request):
    apartments = Apartment.objects.filter(
        contract__is_active=True,
        contract__contractcondition__lease_end__lte=timezone.now() + timedelta(days=120),
        contract__contractcondition__leaserenewaloffer__tenant_choice=None
    ).exclude(
        contract__contractcondition__leaserenewaloffer=None
    )
    return render(request, 'rentcrm/renewal-sent.html', {'apartments': apartments})


@login_required
def renewal_send_pastdue(request):
    apartments = Apartment.objects.filter(
        contract__is_active=True,
        contract__contractcondition__lease_end__lte=timezone.now() + timedelta(days=90),
        contract__contractcondition__leaserenewaloffer=None
    ).exclude(
        contract__contractcondition__leaserenewaloffer__tenant_choice=0
    )
    return render(request, 'rentcrm/renewal-send-pastdue.html', {'apartments': apartments})


@login_required
def renewal_pastdue(request):
    # 60 days after lease renewal form sent or 30 days before lease end_lease
    # only for contracts with LeaseRenewalForm sent
    apartments = Apartment.objects.filter(
        Q(contract__is_active=True),
        Q(contract__contractcondition__leaserenewaloffer__date_issued__lte=
            timezone.now() - timedelta(days=60))|
        Q(contract__contractcondition__lease_end__lte=
            timezone.now() + timedelta(days=30))
    ).exclude(
        contract__contractcondition__leaserenewaloffer=None
    ).exclude(
        contract__contractcondition__leaserenewaloffer__tenant_choice=0
    )

    # 30 days before lease end_lease
    # apartments = Apartment.objects.filter(
    #     contract__is_active=True,
    #     contract__contractcondition__lease_end__lte=timezone.now() + timedelta(days=30),
    # ).exclude(contract__contractcondition__leaserenewaloffer=None)
    return render(request, 'rentcrm/renewal-pastdue.html', {'apartments': apartments})


@login_required
def building_apartments(request, building_pk):
    building = Building.objects.get(pk=building_pk)
    return render(request, 'rentcrm/building-apartments.html', {'building': building})




# details view

@login_required
def cc_info(request, apt_pk):
    apartment = Apartment.objects.select_related('building').get(pk=apt_pk)
    form = ApartmentNotesForm(instance=apartment)
    return render(request, 'rentcrm/details/cc-info.html',
        {'apartment': apartment, 'form': form})


@login_required
def contract_payments(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    startdate = request.GET.get('from')
    enddate = request.GET.get('to')
    payments = contract.payment_set.all()
    if startdate:
        payments = payments.filter(date__gte=startdate)
    if enddate:
        payments = payments.filter(date__lte=enddate)
    adjustments = contract.rentadjustment_set.all()
    return render(request, 'rentcrm/details/contract-payments.html',
        {'contract': contract, 'payments': payments, 'adjustments': adjustments})




# Actions

@login_required
def pay_in(request, apt_pk):
    apartment = get_object_or_404(Apartment, pk=apt_pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, prefix='payment')
        adjustment_form = RentAdjustmentForm(request.POST, prefix='adjust')
        if form.is_valid() and adjustment_form.is_valid():
            next_page = request.GET.get('next',reverse('apartments_all'))
            payment = form.save(commit=False)
            payment.contract = apartment.current_contract
            payment.save()
            if adjustment_form.cleaned_data['amount'] != 0:
                adjustment = adjustment_form.save(commit=False)
                adjustment.contract = apartment.current_contract
                adjustment.save()
            return HttpResponseRedirect(next_page)
    else:
        form = PaymentForm(prefix='payment')
        adjustment_form = RentAdjustmentForm(prefix='adjust', initial={'amount': 0})
    return render(request, 'rentcrm/pay-in.html',
        {'form': form, 'adjustment_form': adjustment_form, 'apartment': apartment})


@login_required
def rent_adjustment(request, apt_pk):
    apartment = get_object_or_404(Apartment, pk=apt_pk)
    if request.method == 'POST':
        form = RentAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.contract = apartment.current_contract
            adjustment.save()
            next_page = request.GET.get('next',reverse('apartments_all'))
            return HttpResponseRedirect(next_page)
    else:
        form = RentAdjustmentForm()
    return render(request, 'rentcrm/adjust.html', {'form': form, 'apartment': apartment})


@login_required
def start_lease(request, apt_pk):
    apartment = get_object_or_404(Apartment, id=apt_pk)

    if request.method == 'POST' and not apartment.current_contract:
        legalrentform = LegalRentForm(request.POST, instance=apartment)
        tenantform = TenantForm(request.POST)
        contractform = ContractForm(request.POST)
        conditionsform = ContractConditionForm(request.POST)

        if tenantform.is_valid() and contractform.is_valid() \
            and conditionsform.is_valid() and legalrentform.is_valid():

            legalrentform.save()

            tenant, tenant_is_new = Tenant.objects.get_or_create(
                **tenantform.cleaned_data)

            contract = contractform.save(commit=False)
            lease_period = conditionsform.save(commit=False)

            contract.apartment = apartment
            startdate = lease_period.lease_start
            contract.signed_date = startdate
            contract.lease_start = startdate

            lease_period.lease_end = startdate.replace(
                year=startdate.year + contract.lease_term) - timedelta(days=1)
            if startdate.day != 1:
                lease_end_year = lease_period.lease_end.year
                lease_end_month = lease_period.lease_end.month
                lease_end_month_last_day = monthrange(
                    lease_end_year, lease_end_month)[1]
                lease_period.lease_end = lease_period.lease_end.replace(
                    day=lease_end_month_last_day)

                # lease_period.lease_end -= timedelta(days=lease_period.lease_end.day)

            lease_period.is_active = True

            if request.POST['pref_rent_sum'] == '':
                lease_period.rent_preferential = apartment.rent_legal
            else:
                lease_period.rent_preferential = request.POST[
                    'pref_rent_sum']
            contract.security_deposit = lease_period.rent_preferential

            contract.save()
            lease_period.contract = contract
            lease_period.save()
            contract.tenants.add(tenant)

            if apartment.rent_legal == 0:  # Decimal('0.00'):
                apartment.rent_legal = lease_period.rent_preferential
                apartment.save(update_fields=['rent_legal'])

            return HttpResponseRedirect(reverse('contract_info', args=[apartment.id]))
    else:
        contractform = ContractForm()
        tenantform = TenantForm()
        legalrentform = LegalRentForm(instance=apartment)

        if apartment.rent_legal > 0:
            conditionsform = ContractConditionForm(
                initial={'rent_preferential': apartment.rent_legal})
        else:
            conditionsform = ContractConditionForm()

    return render(request, 'rentcrm/forms/start-lease.html',
                  {'contractform': contractform,
                   'tenantform': tenantform,
                   'conditionsform': conditionsform,
                   'apartment': apartment,
                   'legalrentform': legalrentform})


@login_required
def set_moving_out_date(request, apt_pk):
    apartment = get_object_or_404(Apartment, pk=apt_pk)
    contract = apartment.current_contract
    next_page = request.GET.get('prev', reverse('apartments_all'))

    if request.method == 'POST':
        form = MovingOutForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next_page)
    else:
        form = MovingOutForm(instance=contract)
    return render(request, 'rentcrm/forms/lease-movingout.html',
        {'apartment': apartment, 'form': form})



@login_required
def end_lease(request, apt_pk):
    apartment = get_object_or_404(Apartment, pk=apt_pk)
    if request.method == 'POST':
        if request.POST.get('confirm')=='yes':
            contract = apartment.current_contract
            contract.is_active = False
            contract.save()
            return HttpResponseRedirect(reverse('apartments_all'))
    return render(request, 'rentcrm/forms/lease-end-confirm.html', {'apartment': apartment})


@login_required
def edit_apartment_note(request, apt_pk):
    apartment = get_object_or_404(Apartment, pk=apt_pk)
    next_page = request.GET.get('next',
        reverse('contract_info', kwargs={'apt_pk': apartment.id}))

    if request.method == 'POST':
        form = ApartmentNotesForm(request.POST, instance=apartment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(next_page)
    return HttpResponseRedirect(next_page)


@login_required
def add_tenant(request, apt_pk):
    next_page = request.GET.get('next',reverse('apartments_all'))
    apartment = Apartment.objects.get(pk=apt_pk)
    if request.method == 'POST':
        tenantform = TenantForm(request.POST)
        if tenantform.is_valid():
            tenant, tenant_is_new = Tenant.objects.get_or_create(
                **tenantform.cleaned_data)
            contract = apartment.current_contract
            contract.tenants.add(tenant)
            return HttpResponseRedirect(next_page)
    else:
        tenantform = TenantForm()
    return render(request, 'rentcrm/tenant-add.html', {'apartment': apartment, 'tenantform': tenantform})


@login_required
def edit_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    next_page = request.GET.get('next',reverse('apartments_all'))

    if request.method == 'POST':
        tenantform = TenantForm(request.POST, instance=tenant)
        if tenantform.is_valid():
            tenantform.save()
            return HttpResponseRedirect(next_page)
    else:
        tenantform = TenantForm(instance=tenant)
    return render(request, 'rentcrm/tenant-edit.html', {'tenant': tenant, 'tenantform': tenantform})


@login_required
def delete_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    next_page = request.GET.get('next')
    if request.method == 'POST':
        if request.POST.get('confirm')=='yes':
            if not next_page:
                next_page = reverse('apartments_all')
            tenant.delete()
            return HttpResponseRedirect(next_page)
    return render(request, 'rentcrm/tenant-delete.html', {'tenant': tenant})



@login_required
def send_renewal(request, apt_pk):
    next_page = request.GET.get('next',reverse('apartments_all'))
    apartment = Apartment.objects.get(pk=apt_pk)
    lease_period = apartment.current_contract.current_conditions
    # Is offer_sent_already?
    if hasattr(lease_period, 'leaserenewaloffer'):
        # Already sent!
        return HttpResponseRedirect(next_page)

    if request.method == 'POST':
        offerform = LeaseRenewalOfferForm(request.POST)
        if offerform.is_valid():
            offer = offerform.save(commit=False)
            offer.lease_period = lease_period
            offer.save()
            return HttpResponseRedirect(next_page)
    else:
        offerform = LeaseRenewalOfferForm()
    return render(request, 'rentcrm/send_renewal.html',
                  {'apartment': apartment, 'offerform': offerform})


@login_required
def update_lease(request, apt_pk):
    next_page = request.GET.get('next',reverse('apartments_all'))
    apartment = Apartment.objects.get(pk=apt_pk)
    current_contract = apartment.current_contract
    current_period = current_contract.current_conditions

    # Is there unaccepted sent LeaseRenewalForm ? Exit if not!
    if not hasattr(current_period, 'leaserenewaloffer') or current_period.leaserenewaloffer.is_accepted():
        # Nothing to update!
        return HttpResponseRedirect(next_page)

    sent_offer = current_period.leaserenewaloffer

    if request.method == 'POST':
        acceptform = OfferAcceptanceForm(request.POST, instance=sent_offer)
        if acceptform.is_valid():
            sent_offer = acceptform.save()
            if sent_offer.tenant_choice == 1:
                # Update lease for 1 year
                apartment.rent_legal = sent_offer.rent_legal_one_year

                startdate = current_period.lease_end + timedelta(days=1)
                enddate = startdate.replace(
                    year=startdate.year + 1) - timedelta(days=1)

                new_period = ContractCondition(lease_start=startdate, lease_end=enddate, is_active=False, rent_preferential=sent_offer.rent_preferential_one_year,
                                               is_garage_included=sent_offer.is_garage_included, rent_for_garage=sent_offer.rent_for_garage, contract=current_contract)
                new_period.save()
                apartment.save(update_fields=['rent_legal'])

            elif sent_offer.tenant_choice == 2:
                # Update lease for 2 years
                new_rent_preferential = sent_offer.rent_preferential_two_years
                apartment.rent_legal = sent_offer.rent_legal_two_years

                startdate = current_period.lease_end + timedelta(days=1)
                enddate = startdate.replace(
                    year=startdate.year + 2) - timedelta(days=1)

                new_period = ContractCondition(lease_start=startdate, lease_end=enddate, is_active=False, rent_preferential=sent_offer.rent_preferential_two_years,
                                               is_garage_included=sent_offer.is_garage_included, rent_for_garage=sent_offer.rent_for_garage, contract=current_contract)
                new_period.save()
                apartment.save(update_fields=['rent_legal'])

            return HttpResponseRedirect(next_page)
    else:
        acceptform = OfferAcceptanceForm(instance=sent_offer)

    return render(request, 'rentcrm/update-lease.html',
                  {'apartment': apartment, 'acceptform': acceptform})




# login - logout

def user_login(request):
    next_page = request.GET.get('next',reverse('apartments_all'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(next_page)
            else:
                return HttpResponse("Your account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rentcrm/login.html', {'next': next_page})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
