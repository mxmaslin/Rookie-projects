# -*- coding: utf-8 -*-
import re
import datetime
from calendar import monthrange
from decimal import Decimal
from dateutil import relativedelta
from django.utils import timezone

from django.db import models
from django.db.models import Sum
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


class Building(models.Model):
    address = models.CharField(max_length=100, unique=True)
    has_garage = models.BooleanField(verbose_name='Garage')

    class Meta:
        ordering = ['address']

    def __str__(self):
        return self.address


class Apartment(models.Model):
    apt_num = models.CharField(max_length=15)
    rent_legal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    building = models.ForeignKey('Building')
    notes = models.TextField(blank=True)
    # lease = models.OneToOneField('Contract', null=True,
    #         related_name='apartment_active_contract')

    class Meta:
        unique_together = ("apt_num", "building")
        ordering = ['building__address', 'apt_num']

    @property
    def has_active_contract(self):
        return self.contract_set.filter(is_active=True).exists()

    @property
    def current_contract(self):
        try:
            return self.contract_set.get(is_active=True)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return '{}, {}'.format(self.apt_num, self.building.address)


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    additional_contacts = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def formatted_phone(self, country=None):
        if len(self.phone) >= 10:
            return self.phone[:3] + '-' + self.phone[3:6] + '-' + self.phone[6:]
        else:
            return self.phone

    def save(self, *args, **kwargs):
        self.phone = re.sub(r"\D", "", self.phone)
        super(Tenant, self).save(*args, **kwargs)


class Payment(models.Model):
    date = models.DateField(default=now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    contract = models.ForeignKey('Contract')

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return '{date} - {amount} from {tenant} for {apartment}'.format(
            amount=self.amount,
            tenant=self.contract.main_tenant_name,
            date=self.date,
            apartment=self.contract.apartment)


class RentAdjustment(models.Model):
    date = models.DateField(default=now)
    amount = models.DecimalField(max_digits=10, decimal_places=2,
        help_text="Enter negative amount to decrease tenant's debt or positive to increase",)
    note = models.CharField(max_length=255, null=True, blank=True)
    contract = models.ForeignKey('Contract')

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return 'Adjustment for {contract}'.format(contract=self.contract)


class Contract(models.Model):
    ONE_YEAR = 1
    TWO_YEARS = 2
    TERM_CHOICES = ((ONE_YEAR, 'One year'), (TWO_YEARS, 'Two years'))

    lease_start = models.DateField()
    lease_end = models.DateField(null=True, blank=True)
    lease_term = models.IntegerField(choices=TERM_CHOICES, default=ONE_YEAR, verbose_name='Initial lease term')
    signed_date = models.DateField(default=now)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    apartment = models.ForeignKey('Apartment')
    tenants = models.ManyToManyField('Tenant')
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)

    def get_absolute_url(self):
        return reverse('contract_info', kwargs={'apt_pk': self.apartment.id})

    @property
    def main_tenant_name(self):
        return self.tenants.all().first()

    def contract_end_date(self):
        return self.contractcondition_set.order_by('lease_start').last().lease_end

    def days_till_lease_end(self):
        return (self.contract_end_date() - datetime.datetime.now().date()).days

    @property
    def current_conditions(self):
        cc = self.contractcondition_set.filter(lease_start__lte=timezone.now()).order_by('lease_start').last()
        if not cc:
            cc = self.contractcondition_set.order_by('lease_start').first()
        return cc

    @property
    def is_lease_renewal_offer_sent(self):
        return self.current_conditions.leaserenewaloffer != None

    @property
    def is_lease_renewal_offer_accepted(self):
        return self.current_conditions.leaserenewaloffer.tenant_choice != None

    @property
    def debit(self):
        lease_sum = Decimal('0.00')
        for cc in self.contractcondition_set.all():
            lease_sum += cc.debit

        # Add debt for months after lease end
        today = datetime.datetime.now().date()
        contract_end_date = self.contract_end_date()

        if today > contract_end_date:
            # Lease already ended, but tenant still lives in apartment

            # For the last month of lease we add full monthly rent amount even
            #   if lease ends in the middle of month
            # That's why we start count from 1st day of next month after lease ends

            if contract_end_date.month == 12:
                first_day_after_lease = datetime.date(
                    contract_end_date.year+1, 1, 1)
            else:
                first_day_after_lease = datetime.date(
                    contract_end_date.year, contract_end_date.month+1, 1)

            if today >= first_day_after_lease:
                ddelta = relativedelta.relativedelta(today, first_day_after_lease)
                months_after_lease = ddelta.years * 12 + ddelta.months + 1

                conditions = self.current_conditions
                rent_payment = conditions.rent_preferential + conditions.rent_for_garage

                lease_sum += round(rent_payment * Decimal(months_after_lease), 2)

        adjustments_sum = self.rentadjustment_set.all().aggregate(Sum('amount'))[
            'amount__sum']
        if adjustments_sum:
            lease_sum += adjustments_sum

        return lease_sum

    @property
    def credit(self):
        payments_sum = self.payment_set.all().aggregate(Sum('amount'))[
            'amount__sum']

        return payments_sum if payments_sum else Decimal('0.00')

    @property
    def balance(self):
        return self.credit - self.debit

    def __str__(self):
        return '{building}, {apt} lease with {tenant}'.format(
            apt=self.apartment.apt_num,
            building=self.apartment.building.address,
            tenant=self.main_tenant_name)


class ContractCondition(models.Model):
    # period start date, not lease start! Should be renamed
    lease_start = models.DateField(verbose_name='Period start')
    lease_end = models.DateField(verbose_name='Period end')
    is_active = models.BooleanField()
    rent_preferential = models.DecimalField(max_digits=10, decimal_places=2)
    is_garage_included = models.BooleanField(verbose_name='Garage')
    rent_for_garage = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))
    contract = models.ForeignKey('Contract')

    @property
    def days_till_lease_end(self):
        return (self.lease_end - datetime.datetime.now().date()).days

    @property
    def debit(self):
        today = datetime.datetime.now().date()
        period_start_date = self.lease_start

        if today < period_start_date:
            # Lease period (ContractCondition) in future
            return Decimal('0.00')
        else:
            # how much full months
            period_end_date = min(today, self.lease_end)
            ddelta = relativedelta.relativedelta(
                period_end_date,
                datetime.date(period_start_date.year, period_start_date.month, 1)
                )
            month_count = ddelta.years * 12 + ddelta.months  # count from second month

        rent_payment = self.rent_preferential + self.rent_for_garage

        # Calc debt for first month
        if period_start_date.day == 1:
            debit = rent_payment
        else:
            first, days_in_month = monthrange(
                period_start_date.year, period_start_date.month)
            days = days_in_month - period_start_date.day
            debit = round(rent_payment / days_in_month * days, 2)

        return debit + round(rent_payment * Decimal(month_count), 2)

    def __str__(self):
        return 'Period of contract for {building}, apt {apt} from {start} to {end}'.format(
                apt=self.contract.apartment.apt_num,
                building=self.contract.apartment.building.address,
                start=self.lease_start,
                end=self.lease_end
                )

    class Meta:
        verbose_name = 'Lease period'
        verbose_name_plural = 'Lease periods'


class LeaseRenewalOffer(models.Model):
    # ONE_YR = 1
    # TWO_YRS = 2
    # STOP_LEASE = 0
    # TERM_CHOICES = ((ONE_YR, 'One year term'), (TWO_YRS, 'Two years term'))
    ACCEPTANCE_CHOICES = ((1, 'One year term'),
                          (2, 'Two years term'), (0, 'No renew'))
    # YES = True
    # NO = False
    # ACCEPTANCE_CHOICES = ((YES, 'Offer accepted'), (NO, 'Offer rejected'))
    # new_term = models.IntegerField(choices=TERM_CHOICES)
    tenant_choice = models.SmallIntegerField(
        choices=ACCEPTANCE_CHOICES, blank=True, null=True)
    date_issued = models.DateField(default=now)
    rent_legal_one_year = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    rent_preferential_one_year = models.DecimalField(
        max_digits=10, decimal_places=2)
    rent_legal_two_years = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    rent_preferential_two_years = models.DecimalField(
        max_digits=10, decimal_places=2)
    is_garage_included = models.BooleanField(verbose_name='Garage')
    rent_for_garage = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default='0.00')
    is_sent = models.BooleanField(default=True, verbose_name='Sent')
    # is_accepted = models.BooleanField(verbose_name='Offer status', choices=ACCEPTANCE_CHOICES)
    is_response_received = models.BooleanField(
        default=False, verbose_name='Response')
    # contract = models.ForeignKey('Contract')
    lease_period = models.OneToOneField('ContractCondition')

    def __str__(self):
        return 'Lease Renewal Offer for contract with {} that was started at {}'.format(
            self.lease_period.contract.main_tenant_name,
            self.lease_period.contract.signed_date)

    def is_accepted(self):
        return self.tenant_choice != None
